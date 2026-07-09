# Main Program Algorithm Walkthrough

This document explains the calculation logic in the main program, focusing only on the core workflow in [main.py](main.py). It is written as a step-by-step guide, function by function.

## 1. What the program is trying to do

The program helps plan a qPCR RNA dilution for one or more viruses that will be combined into a shared final sample vial.

For each virus, it estimates:

- the dilution needed to reach a target Ct value,
- the RNA volume to pipette,
- the diluent volume to add,
- and the predicted final Ct value after dilution.

The calculation is based on the standard qPCR relationship:

- $\text{required dilution factor} = 10^{(\text{target Ct} - \text{stock Ct}) / 3.3}$

The value 3.3 is the assumed Ct change per 10-fold dilution.

---

## 2. Configuration constants

At the top of the file, the program defines a set of configuration values such as:

- `FINAL_VOLUME_UL`: the target final sample volume
- `CT_PER_10X`: the Ct change expected for a 10-fold dilution
- `CT_TOLERANCE`: acceptable error when matching the target Ct
- `MIN_TOTAL_DILUTION`: minimum required dilution factor
- `MIN_ADDITIONAL_DILUTION`: minimum practical additional dilution step
- `STARTING_DILUTION`: the base dilution factor used for calculations
- `MAX_TARGET_CT`: the upper limit for allowed targets
- `MIN_PIPETTE_VOLUME_UL`: smallest practical RNA volume to pipette

These values are the fixed assumptions behind the whole calculation.

---

## 3. Function-by-function walkthrough

### 3.1 `_validate_positive_number(name, value)`

Purpose:
- Validates that a numeric input is present and greater than zero.

What it does:
- Checks whether the input is `None` or less than or equal to zero.
- Raises a `ValueError` if the input is invalid.

Why it matters:
- The rest of the program depends on positive numbers for Ct values, volumes, and similar inputs.

---

### 3.2 `build_components_from_selection(selected_viruses, target_cts, stock_cts=None)`

Purpose:
- Converts user input into a validated list of virus components.

What it does:
- Ensures that the number of selected viruses matches the number of target Ct values.
- Ensures that the total number of viruses does not exceed 3.
- Checks that each virus name is recognized.
- Uses the default stock Ct values unless a custom stock Ct dictionary is provided.
- Builds a list of dictionaries, each containing:
  - `virus`
  - `target_ct`
  - `stock_ct`

Why it matters:
- This is the step that transforms raw CLI input into a structured list the calculator can process.

---

### 3.3 `calculate_component(stock_ct, target_ct, final_volume_ul, component_count=1, min_pipette_volume_ul=MIN_PIPETTE_VOLUME_UL)`

This is the core calculation function for one virus component.

#### Step A: Input validation

The function first validates:
- `stock_ct`
- `target_ct`
- `final_volume_ul`
- `min_pipette_volume_ul`

It also checks that `component_count` is between 1 and 3, because the app is designed to support up to 3 viruses in one vial.

It also rejects target Ct values above the configured maximum.

#### Step B: Calculate the theoretical dilution needed

The function computes the theoretical dilution factor required to change the stock Ct to the target Ct:

- $\text{required total dilution} = 10^{(\text{target Ct} - \text{stock Ct}) / 3.3}$

This value represents the dilution needed in principle to reach the requested Ct.

#### Step C: Choose a practical dilution factor

The program does not use the theoretical value directly. Instead, it searches for a practical whole-number dilution factor that is close enough to the target.

It starts with:
- `additional_factor = max(2, ceil(required_total_dilution / 4))`

Then it repeatedly computes:

- `total_dilution_factor = 4 * additional_factor`
- `achieved_ct = stock_ct + 3.3 * log10(total_dilution_factor)`

The loop continues until the predicted Ct is within the allowed tolerance of the target Ct.

If the predicted Ct is too high, the function raises an error because no practical dilution factor can reach the target within the acceptable tolerance.

#### Step D: Compute pipetting volumes

Once the practical dilution factor is found, the function calculates:

- `rna_volume_ul = final_volume_ul * 4 / total_dilution_factor`
- `diluent_volume_ul = final_volume_ul - rna_volume_ul`

The logic is based on the idea that the RNA sample is diluted by the chosen total dilution factor, while the remaining volume is filled with diluent.

#### Step E: Check physical practicality

The function checks whether the computed RNA volume is at least the minimum pipette volume.

If the calculated RNA volume is below the minimum practical handling volume, the function raises an error.

#### Step F: Return the result

The function returns a dictionary with the calculated values, including:

- `stock_ct`
- `target_ct`
- `component_count`
- `component_volume_ul`
- `total_dilution_factor`
- `additional_dilution_factor`
- `shared_vial_dilution_factor`
- `achieved_ct`
- `rna_volume_ul`
- `diluent_volume_ul`

This result is the central output for a single virus component.

---

### 3.4 `calculate_mix(components, final_volume_ul=FINAL_VOLUME_UL)`

Purpose:
- Combines multiple virus components into one shared final vial.

What it does:
- Accepts a list of component dictionaries.
- Loops through each component.
- Calls `calculate_component()` for each one using the same final vial volume.
- Adds the virus name to each result.
- Sums the RNA volumes from all components.
- Computes the shared diluent volume for the full mixture:

- $\text{shared diluent volume} = \text{final volume} - \text{sum of RNA volumes}$

Why it matters:
- This function is where the program moves from single-component planning to a full multi-virus formulation plan.

---

### 3.5 `run_cli()`

Purpose:
- Provides the command-line interface for the program.

What it does:
- Parses command-line arguments using `argparse`.
- Supports:
  - `--virus`
  - `--target-ct`
  - `--final-volume`
- If no virus targets are supplied, it falls back to a simple example calculation for PEDV.
- If virus and target lists are provided, it:
  - validates that they are the same length,
  - builds the component list,
  - calls `calculate_mix()`,
  - and prints a human-readable plan.

This is the user-facing entry point for the program.

---

## 4. End-to-end flow of the main program

When the program is run, it follows this sequence:

1. The user provides virus names, target Ct values, and an optional final volume.
2. The program validates the input.
3. It builds a list of virus components.
4. For each component, it computes the dilution and volume plan.
5. It combines the components into one shared vial.
6. It calculates the total shared diluent needed.
7. It prints the plan in a readable summary.

---

## 5. Important assumptions in the algorithm

The main program uses a few simplifying assumptions:

- Ct change is assumed to be 3.3 per 10-fold dilution.
- Dilution factors are chosen as practical whole numbers.
- The program supports up to 3 viruses in one final vial.
- The RNA volume must remain above a minimum practical pipetting threshold.
- The target Ct cannot exceed the configured maximum.

---

## 6. Summary

In short, the main program works like this:

- It takes a virus and a desired Ct target.
- It converts that target into a required dilution factor.
- It finds a practical whole-number dilution that gets as close as possible.
- It calculates how much RNA and diluent are needed.
- It repeats that for each virus and combines them into a shared final sample.

This makes it a practical planning tool for multi-virus qPCR formulation setup.

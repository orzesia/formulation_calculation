"""Simple qPCR formulation calculator for up to three viruses.

This script is intended to be run from an IDE such as PyCharm, where the
user can enter values in the console.
"""

PEDV_stock_ct = 23.3
PDCoV_stock_ct = 27.95
TGEV_stock_ct = 18.0
PRVA_stock_ct = 24.98

VIRUS_STOCK_CTS = {
    "PEDV": PEDV_stock_ct,
    "PDCoV": PDCoV_stock_ct,
    "TGEV": TGEV_stock_ct,
    "PRVA": PRVA_stock_ct,
}

VALID_VIRUS_NAMES = tuple(VIRUS_STOCK_CTS.keys())


def get_number_of_viruses(user_input):
    """Validate and return the number of viruses in the sample.

    Parameters:
        user_input (str): The value entered by the user.

    Returns:
        int: A validated value of 1, 2, or 3.

    Raises:
        ValueError: If the input is not a whole number between 1 and 3.
    """
    try:
        number_of_viruses = int(user_input)
    except (TypeError, ValueError) as error:
        raise ValueError("Please enter 1, 2, or 3.") from error

    if number_of_viruses not in (1, 2, 3):
        raise ValueError("Please enter 1, 2, or 3.")

    return number_of_viruses


def ask_for_number_of_viruses():
    """Ask the user how many viruses are in the sample."""
    while True:
        user_input = input("How many viruses are in the sample? Enter 1, 2, or 3: ").strip()
        try:
            return get_number_of_viruses(user_input)
        except ValueError as error:
            print(error)


def normalize_virus_name(virus_name_input):
    """Return a valid virus name in a fixed format.

    Parameters:
        virus_name_input (str): The raw virus name entered by the user.

    Returns:
        str: A normalized virus name such as PEDV.

    Raises:
        ValueError: If the name is not one of the allowed virus names.
    """
    trimmed_name = virus_name_input.strip()
    if not trimmed_name:
        raise ValueError("Virus name cannot be empty.")

    for valid_virus_name in VALID_VIRUS_NAMES:
        if trimmed_name.casefold() == valid_virus_name.casefold():
            return valid_virus_name

    raise ValueError(
        f"Unknown virus name '{virus_name_input}'. Choose from: {', '.join(VALID_VIRUS_NAMES)}"
    )


def get_valid_virus_name(prompt_text, seen_virus_names):
    """Ask for a virus name and ensure it is valid and not repeated."""
    while True:
        virus_name_input = input(prompt_text).strip()
        try:
            normalized_virus_name = normalize_virus_name(virus_name_input)
        except ValueError as error:
            print(error)
            continue

        if normalized_virus_name in seen_virus_names:
            print("That virus was already entered. Please choose a different virus.")
            continue

        seen_virus_names.add(normalized_virus_name)
        return normalized_virus_name


def get_valid_desired_ct(virus_name, stock_ct):
    """Ask for a desired Ct value and validate it against the rules."""
    while True:
        try:
            desired_ct = float(input(f"Enter the desired Ct for {virus_name}: ").strip())
        except ValueError:
            print("Please enter a numeric Ct value.")
            continue

        if desired_ct > 32:
            print("Desired Ct must be 32 or lower.")
            continue

        if desired_ct < stock_ct + 2:
            print("Desired Ct must be at least 2 ct higher than the stock Ct.")
            continue

        delta_ct = desired_ct - stock_ct
        dilution_factor = 10 ** (delta_ct / 3.3)
        if dilution_factor < 8:
            print("The required dilution is below 8x. Please choose a higher desired Ct.")
            continue

        return desired_ct


def get_valid_final_volume():
    """Ask for the final sample volume and validate it."""
    while True:
        try:
            final_volume = float(input("Enter the final volume of the sample in microliters (µL): ").strip())
        except ValueError:
            print("Please enter a numeric volume.")
            continue

        if final_volume <= 0:
            print("Final volume must be positive.")
            continue

        return final_volume


def calculate_formulation_from_inputs(virus_names, desired_cts, final_volume_ul):
    """Calculate the formulation plan from explicit virus names and target Cts.

    Parameters:
        virus_names (list[str]): Virus names to include in the mix.
        desired_cts (list[float]): Desired Ct values for each virus.
        final_volume_ul (float): Final sample volume in microliters.

    Returns:
        tuple[list[dict], float]: A list of per-virus results and the required diluent volume.

    Raises:
        ValueError: If the inputs violate the validation rules.
    """
    if len(virus_names) != len(desired_cts):
        raise ValueError("The number of virus names and desired Cts must match.")

    if len(virus_names) not in (1, 2, 3):
        raise ValueError("Please provide 1, 2, or 3 viruses.")

    if len(set(virus_names)) != len(virus_names):
        raise ValueError("Virus names must be unique.")

    virus_results = []
    for virus_name_input, desired_ct in zip(virus_names, desired_cts):
        virus_name = normalize_virus_name(virus_name_input)
        stock_ct = VIRUS_STOCK_CTS[virus_name]

        if desired_ct > 32:
            raise ValueError("Desired Ct must be 32 or lower.")

        if desired_ct < stock_ct + 2:
            raise ValueError("Desired Ct must be at least 2 ct higher than the stock Ct.")

        delta_ct = desired_ct - stock_ct
        dilution_factor = 10 ** (delta_ct / 3.3)
        if dilution_factor < 8:
            raise ValueError("The required dilution is below 8x. Please choose a higher desired Ct.")

        stock_volume_ul = (final_volume_ul / dilution_factor) * 4
        virus_results.append(
            {
                "virus_name": virus_name,
                "stock_ct": stock_ct,
                "desired_ct": desired_ct,
                "delta_ct": delta_ct,
                "dilution_factor": dilution_factor,
                "stock_volume_ul": stock_volume_ul,
            }
        )

    total_stock_volume_ul = sum(result["stock_volume_ul"] for result in virus_results)
    diluent_volume_ul = final_volume_ul - total_stock_volume_ul

    if diluent_volume_ul <= 0:
        raise ValueError(
            "Diluent volume is not positive. Please choose different target Cts or a larger final volume."
        )

    return virus_results, diluent_volume_ul


def calculate_formulation_plan(number_of_viruses, final_volume_ul):
    """Calculate dilution and volume details for each virus in the sample."""
    seen_virus_names = set()
    virus_names = []
    desired_cts = []

    for virus_index in range(1, number_of_viruses + 1):
        virus_name = get_valid_virus_name(f"Enter the name of virus {virus_index}: ", seen_virus_names)
        virus_names.append(virus_name)
        stock_ct = VIRUS_STOCK_CTS[virus_name]
        desired_ct = get_valid_desired_ct(virus_name, stock_ct)
        desired_cts.append(desired_ct)

    return calculate_formulation_from_inputs(virus_names, desired_cts, final_volume_ul)


def run_program():
    """Run the full interactive workflow for the formulation calculator."""
    number_of_viruses = ask_for_number_of_viruses()
    final_volume_ul = get_valid_final_volume()

    virus_results, diluent_volume_ul = calculate_formulation_plan(number_of_viruses, final_volume_ul)

    print("\nFormulation plan")
    print("================")
    for virus_result in virus_results:
        print(
            f"{virus_result['virus_name']}: desired Ct {virus_result['desired_ct']:.2f}, "
            f"delta Ct {virus_result['delta_ct']:.2f}, dilution {virus_result['dilution_factor']:.2f}x, "
            f"stock volume {virus_result['stock_volume_ul']:.2f} µL"
        )

    print(f"Total stock volume: {sum(result['stock_volume_ul'] for result in virus_results):.2f} µL")
    print(f"Diluent volume: {diluent_volume_ul:.2f} µL")


if __name__ == "__main__":
    run_program()


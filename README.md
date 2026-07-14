# formulation_calculation

A simple Python program for planning multi-virus qPCR formulation dilutions from stock Ct values and desired target Ct values.

## What the program does

This script helps calculate how much stock virus solution and diluent are needed to prepare a final sample mix for 1, 2, or 3 viruses.

For each virus, the program asks for:
- the virus name
- the desired Ct value
- the final sample volume

It then calculates:
- delta Ct
- dilution factor
- stock volume to add
- diluent volume to add

## Hard-coded stock Ct values

The program includes the hardcoded ct stock values.
These values are stored at the top of the script in a single place so they are easy to update.

## Validation rules

The program checks the entered values and refuses invalid input when needed. It enforces:
- only 1, 2, or 3 viruses are allowed
- virus names must match the supported list
- virus names cannot be repeated
- desired Ct must be at least 2 Ct higher than the stock Ct
- desired Ct cannot exceed 32
- dilution cannot be below 8x
- diluent volume must remain positive

## How to run it

This program is designed to be run from an IDE such as PyCharm rather than from the command line.

1. Open the project in PyCharm.
2. Open [simplified.py](simplified.py).
3. Run the file with the Python runner.
4. Enter the requested values in the console.

## Notes

The calculations use the simple formula:
- dilution = 10^(delta Ct / 3.3)
- stock volume = (final volume / dilution) * 4

The stock is assumed to be stored as a 1:4 dilution.


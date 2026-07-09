# formulation_calculation

A small Python tool for planning multi-virus qPCR formulation dilutions from stock Ct values and desired target Ct values.

## What it does

- Calculates a practical dilution plan for one virus component at a time
- Supports multi-virus mixes in a shared final vial
- Estimates RNA volume, diluent volume, and the predicted final Ct value
- Can be used from the command line or through a simple Shiny web interface

## Files

- main.py: core calculation logic and CLI entry point
- main_py.py: interactive prompt-based entry point for local Python environments such as PyCharm
- shiny_main.py: separate Shiny app for interactive use
- test_main.py: unit tests for the calculator functions
- test_main_py.py: tests for the prompt-based entry point

## Run the CLI

```bash
python main.py --virus PEDV --target-ct 26 --virus PDCoV --target-ct 26 --final-volume 3000
```

## Run the interactive PyCharm-friendly version

If you want to use the program in a local Python IDE without shell arguments, run:

```bash
python main_py.py
```

When you run this script, it will prompt you for:

- each virus name,
- the target Ct for each virus,
- and the final volume in uL.

This version uses the logic from main.py, so you only need to run main_py.py as long as both files are in the same project folder.

## Run the Shiny app

```bash
python shiny_main.py
```

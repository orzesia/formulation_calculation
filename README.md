# formulation_calculation

A small Python tool for planning multi-virus qPCR formulation dilutions from stock Ct values and desired target Ct values.

## What it does

- Calculates a practical dilution plan for one virus component at a time
- Supports multi-virus mixes in a shared final vial
- Estimates RNA volume, diluent volume, and the predicted final Ct value
- Can be used from the command line or through a simple Shiny web interface

## Files

- main.py: core calculation logic and CLI entry point
- shiny_main.py: separate Shiny app for interactive use
- test_main.py: unit tests for the calculator functions

## Run the CLI

```bash
python main.py --virus PEDV --target-ct 26 --virus PDCoV --target-ct 26 --final-volume 3000
```

## Run the Shiny app

```bash
python shiny_main.py
```

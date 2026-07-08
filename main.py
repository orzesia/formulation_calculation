"""qPCR RNA dilution calculator for multi-virus formulations.

Example:
python main.py --virus PEDV --target-ct 25 --virus PDCoV --target-ct 17 --final-volume 3000
"""

from __future__ import annotations

import argparse
import math
from typing import Dict, List

# Editable configuration section.
FINAL_VOLUME_UL = 3000.0
CT_PER_10X = 3.3
CT_TOLERANCE = 0.5
MIN_TOTAL_DILUTION = 8.0
MIN_ADDITIONAL_DILUTION = 2
STARTING_DILUTION = 4.0
MAX_TARGET_CT = 32.0
MIN_PIPETTE_VOLUME_UL = 2.0

VIRUS_STOCKS: Dict[str, float] = {
    "PEDV": 22.2,
    "PDCoV": 21.6,
    "TGEV": 18.9,
}


def _validate_positive_number(name: str, value: float) -> None:
    if value is None or value <= 0:
        raise ValueError(f"{name} must be a positive number")


def calculate_component(
    stock_ct: float,
    target_ct: float,
    final_volume_ul: float,
    component_count: int = 1,
    min_pipette_volume_ul: float = MIN_PIPETTE_VOLUME_UL,
) -> Dict[str, float]:
    """Calculate a practical dilution and pipetting volumes for one virus component."""
    _validate_positive_number("stock_ct", stock_ct)
    _validate_positive_number("target_ct", target_ct)
    _validate_positive_number("final_volume_ul", final_volume_ul)
    _validate_positive_number("min_pipette_volume_ul", min_pipette_volume_ul)

    if component_count < 1 or component_count > 3:
        raise ValueError("This calculator supports 1, 2, or 3 viruses in one vial")

    if target_ct > MAX_TARGET_CT:
        raise ValueError(f"target_ct cannot exceed {MAX_TARGET_CT}")

    required_total_dilution = 10 ** ((target_ct - stock_ct) / CT_PER_10X)
    additional_factor = max(
        MIN_ADDITIONAL_DILUTION,
        math.ceil(required_total_dilution / STARTING_DILUTION),
    )

    while True:
        total_dilution_factor = STARTING_DILUTION * additional_factor
        achieved_ct = stock_ct + CT_PER_10X * math.log10(total_dilution_factor)
        if abs(achieved_ct - target_ct) <= CT_TOLERANCE + 1e-9:
            break
        if achieved_ct > target_ct + CT_TOLERANCE:
            raise ValueError(
                f"No practical whole-number dilution factor reaches target Ct within ±{CT_TOLERANCE}"
            )
        additional_factor += 1

    component_volume_ul = final_volume_ul / component_count
    rna_volume_ul = component_volume_ul / additional_factor
    diluent_volume_ul = component_volume_ul - rna_volume_ul

    if rna_volume_ul < min_pipette_volume_ul:
        raise ValueError(
            "The calculated RNA volume is below the minimum pipette volume for practical handling"
        )

    return {
        "stock_ct": stock_ct,
        "target_ct": target_ct,
        "component_count": component_count,
        "component_volume_ul": component_volume_ul,
        "total_dilution_factor": int(STARTING_DILUTION * additional_factor),
        "additional_dilution_factor": int(additional_factor),
        "shared_vial_dilution_factor": int(component_count),
        "achieved_ct": achieved_ct,
        "rna_volume_ul": rna_volume_ul,
        "diluent_volume_ul": diluent_volume_ul,
    }


def calculate_mix(
    components: List[Dict[str, object]],
    final_volume_ul: float = FINAL_VOLUME_UL,
) -> Dict[str, object]:
    """Calculate dilution plans for a multi-virus mix."""
    _validate_positive_number("final_volume_ul", final_volume_ul)
    if not components:
        raise ValueError("At least one virus component is required")

    component_count = len(components)
    results: List[Dict[str, object]] = []
    for component in components:
        virus = str(component["virus"])
        stock_ct = float(component.get("stock_ct", VIRUS_STOCKS[virus]))
        target_ct = float(component["target_ct"])
        result = calculate_component(
            stock_ct=stock_ct,
            target_ct=target_ct,
            final_volume_ul=final_volume_ul,
            component_count=component_count,
        )
        result["virus"] = virus
        results.append(result)

    total_rna_volume_ul = sum(result["rna_volume_ul"] for result in results)
    shared_diluent_volume_ul = final_volume_ul - total_rna_volume_ul
    return {
        "components": results,
        "shared_diluent_volume_ul": shared_diluent_volume_ul,
        "final_volume_ul": final_volume_ul,
    }


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Calculate qPCR RNA dilution volumes")
    parser.add_argument(
        "--virus",
        action="append",
        help="Virus name from the configuration (repeat for multiple viruses)",
    )
    parser.add_argument(
        "--target-ct",
        type=float,
        action="append",
        help="Target Ct for the corresponding virus (repeat for multiple viruses)",
    )
    parser.add_argument("--final-volume", type=float, default=FINAL_VOLUME_UL)
    args = parser.parse_args()

    if not args.virus or not args.target_ct:
        print("No virus targets provided. Falling back to an example calculation.")
        example = calculate_component(
            stock_ct=VIRUS_STOCKS["PEDV"],
            target_ct=26.0,
            final_volume_ul=args.final_volume,
            component_count=1,
        )
        print("Virus: PEDV")
        print(f"Starting Ct: {example['stock_ct']:.1f}")
        print(f"Target Ct: {example['target_ct']:.1f}")
        print(f"Total dilution factor: {example['total_dilution_factor']}x")
        print(f"Additional dilution factor: {example['additional_dilution_factor']}x")
        print(f"Shared vial dilution factor: {example['shared_vial_dilution_factor']}x")
        print(f"RNA volume added: {example['rna_volume_ul']:.1f} uL")
        print(f"Diluent volume added: {example['diluent_volume_ul']:.1f} uL")
        print(f"Final predicted Ct: {example['achieved_ct']:.2f}")
        return

    if len(args.virus) != len(args.target_ct):
        raise ValueError("Each virus needs exactly one target Ct")

    components = []
    for virus, target_ct in zip(args.virus, args.target_ct):
        if virus not in VIRUS_STOCKS:
            raise ValueError(
                f"Unknown virus {virus}. Available options: {', '.join(sorted(VIRUS_STOCKS))}"
            )
        components.append({"virus": virus, "target_ct": target_ct})

    mix = calculate_mix(components, final_volume_ul=args.final_volume)
    print("Prepared dilution plan:")
    print(f"Shared diluent for the full vial: {mix['shared_diluent_volume_ul']:.1f} uL")
    for index, result in enumerate(mix["components"], start=1):
        print(f"\nComponent {index}: {result['virus']}")
        print(f"Starting Ct: {result['stock_ct']:.1f}")
        print(f"Target Ct: {result['target_ct']:.1f}")
        print(f"Total dilution factor: {result['total_dilution_factor']}x")
        print(f"Additional dilution factor: {result['additional_dilution_factor']}x")
        print(f"Shared vial dilution factor: {result['shared_vial_dilution_factor']}x")
        print(f"RNA volume added: {result['rna_volume_ul']:.1f} uL")
        print(f"Final predicted Ct: {result['achieved_ct']:.2f}")


if __name__ == "__main__":
    try:
        run_cli()
    except Exception as exc:  # pragma no cover - simple CLI error handling
        print(f"Error: {exc}")
        raise SystemExit(1)

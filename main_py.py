"""Interactive entry point for the qPCR dilution calculator.

This module provides a prompt-driven interface that works well in local Python
environments such as PyCharm, VS Code, or any other IDE that can run a Python
script without relying on shell arguments.
"""

from __future__ import annotations

from typing import List, Sequence

from main import FINAL_VOLUME_UL, VIRUS_STOCKS, build_components_from_selection, calculate_mix


def _prompt_non_empty(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Please enter a value.")


def _prompt_float(message: str, default: float | None = None) -> float:
    while True:
        raw_value = input(message).strip()
        if not raw_value and default is not None:
            return default
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def build_plan_from_inputs(
    selected_viruses: Sequence[str],
    target_cts: Sequence[float],
    final_volume_ul: float = FINAL_VOLUME_UL,
) -> dict:
    """Build a dilution plan from a supplied list of viruses and target Ct values."""
    components = build_components_from_selection(selected_viruses, target_cts)
    return calculate_mix(components, final_volume_ul=final_volume_ul)


def run_interactive() -> None:
    """Run the calculator through interactive prompts in a local Python IDE."""
    print("qPCR RNA dilution calculator")
    print("Enter one virus at a time. Type 'done' when finished.")

    viruses: List[str] = []
    target_cts: List[float] = []

    while True:
        virus_name = _prompt_non_empty(
            "Virus name (PEDV, PDCoV, TGEV) or 'done' to finish: "
        ).strip().upper()
        if virus_name.lower() in {"done", "exit", "quit"}:
            break

        if virus_name not in VIRUS_STOCKS:
            print(f"Unknown virus '{virus_name}'. Available options: {', '.join(sorted(VIRUS_STOCKS))}")
            continue

        target_ct = _prompt_float("Target Ct for this virus: ")
        viruses.append(virus_name)
        target_cts.append(target_ct)

    if not viruses:
        print("No viruses entered. Using a simple example with PEDV.")
        viruses = ["PEDV"]
        target_cts = [26.0]

    final_volume_ul = _prompt_float(
        f"Final volume in uL (default {FINAL_VOLUME_UL}): ",
        default=FINAL_VOLUME_UL,
    )

    mix = build_plan_from_inputs(viruses, target_cts, final_volume_ul=final_volume_ul)

    print("\nPrepared dilution plan:")
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
    run_interactive()

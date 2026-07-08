"""A small Shiny application for planning multi-virus qPCR dilution formulations."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from main import VIRUS_STOCKS, calculate_mix, build_components_from_selection


try:
    from shiny import App, Inputs, Outputs, Session, ui
except ImportError as exc:  # pragma no cover - runtime dependency
    raise SystemExit("Shiny is not installed. Install it with `pip install shiny`.") from exc


VIRUS_OPTIONS = list(VIRUS_STOCKS.keys())
DEFAULT_TARGETS = {
    "PEDV": 26.0,
    "PDCoV": 26.0,
    "TGEV": 26.0,
}


def _make_component_rows() -> List[Dict[str, Any]]:
    """Create the default virus metadata used to populate the input controls."""
    return [
        {
            "virus": virus,
            "stock_ct": VIRUS_STOCKS[virus],
            "target_ct": DEFAULT_TARGETS[virus],
            "selected": virus == "PEDV",
        }
        for virus in VIRUS_OPTIONS
    ]


app_ui = ui.page_fluid(
    ui.h2("qPCR RNA dilution calculator"),
    ui.p("Select up to three viruses, edit the starting Ct values if needed, and calculate the mix."),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_numeric("final_volume", "Final volume (uL)", value=3000.0, min=1.0),
            ui.input_checkbox_group(
                "selected_viruses",
                "Viruses",
                choices=VIRUS_OPTIONS,
                selected=["PEDV"],
            ),
            ui.input_action_button("calculate", "Calculate"),
            ui.input_action_button("reset", "Reset"),
            width=350,
        ),
        ui.div(
            ui.h4("Virus inputs"),
            ui.output_ui("virus_inputs"),
            ui.br(),
            ui.h4("Results"),
            ui.output_table("results_table"),
            ui.br(),
            ui.output_text_verbatim("summary"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    """Define the Shiny app layout and reactive behavior for calculating dilution plans."""
    component_rows = _make_component_rows()

    @output
    @ui.render_ui
    def virus_inputs() -> Any:
        """Render the editable input controls for each selected virus."""
        selected = list(input.selected_viruses())
        if not selected:
            return ui.p("Select at least one virus to calculate a dilution plan.")

        rows: List[Any] = []
        for virus in VIRUS_OPTIONS:
            if virus not in selected:
                continue
            rows.append(
                ui.div(
                    ui.tags.div(
                        ui.tags.label(virus),
                        ui.input_numeric(f"target_ct_{virus}", f"Target Ct for {virus}", value=DEFAULT_TARGETS[virus], min=1.0, max=32.0),
                        ui.input_numeric(f"stock_ct_{virus}", f"Starting Ct for {virus}", value=VIRUS_STOCKS[virus], min=1.0, max=32.0),
                    ),
                    style="margin-bottom: 12px;",
                )
            )
        return ui.TagList(*rows)

    @input
    @ui.bind_action_button("calculate")
    def run_calculation() -> None:
        """Handle the calculate button event by triggering the reactive results display."""
        pass

    @output
    @ui.render_table
    def results_table() -> Any:
        """Render the per-virus and shared-diluent results as a table."""
        selected = list(input.selected_viruses())
        if not selected:
            return []

        try:
            target_cts = []
            stock_cts: Dict[str, float] = {}
            for virus in selected:
                target_cts.append(float(input[f"target_ct_{virus}"]()))
                stock_cts[virus] = float(input[f"stock_ct_{virus}"]())
            components = build_components_from_selection(selected, target_cts, stock_cts=stock_cts)
            mix = calculate_mix(components, final_volume_ul=float(input.final_volume()))
        except Exception as exc:  # pragma no cover - UI error handling
            return [{"error": str(exc)}]

        rows = []
        for result in mix["components"]:
            rows.append(
                {
                    "Virus": result["virus"],
                    "RNA volume (uL)": round(float(result["rna_volume_ul"]), 2),
                    "Predicted Ct": round(float(result["achieved_ct"]), 2),
                    "Total dilution": int(result["total_dilution_factor"]),
                    "Additional dilution": int(result["additional_dilution_factor"]),
                    "Shared vial dilution": int(result["shared_vial_dilution_factor"]),
                }
            )
        rows.append(
            {
                "Virus": "Shared diluent",
                "RNA volume (uL)": round(float(mix["shared_diluent_volume_ul"]), 2),
                "Predicted Ct": "-",
                "Total dilution": "-",
                "Additional dilution": "-",
                "Shared vial dilution": "-",
            }
        )
        return rows

    @output
    @ui.render_text
    def summary() -> str:
        """Render a compact text summary of the calculated dilution plan."""
        selected = list(input.selected_viruses())
        if not selected:
            return "Select at least one virus to see a summary."

        try:
            target_cts = []
            stock_cts: Dict[str, float] = {}
            for virus in selected:
                target_cts.append(float(input[f"target_ct_{virus}"]()))
                stock_cts[virus] = float(input[f"stock_ct_{virus}"]())
            components = build_components_from_selection(selected, target_cts, stock_cts=stock_cts)
            mix = calculate_mix(components, final_volume_ul=float(input.final_volume()))
        except Exception as exc:  # pragma no cover - UI error handling
            return f"Error: {exc}"

        lines = [
            f"Final volume: {mix['final_volume_ul']:.0f} uL",
            f"Shared diluent for the full vial: {mix['shared_diluent_volume_ul']:.2f} uL",
        ]
        for result in mix["components"]:
            lines.append(
                f"{result['virus']}: RNA {float(result['rna_volume_ul']):.2f} uL, predicted Ct {float(result['achieved_ct']):.2f}, total dilution {int(result['total_dilution_factor'])}x"
            )
        return "\n".join(lines)

    @input
    @ui.bind_action_button("reset")
    def reset_form() -> None:
        """Reset the form to the default virus selection and starting values."""
        for virus in VIRUS_OPTIONS:
            session.input.set("target_ct_" + virus, DEFAULT_TARGETS[virus])
            session.input.set("stock_ct_" + virus, VIRUS_STOCKS[virus])
        session.input.set("final_volume", 3000.0)
        session.input.set("selected_viruses", ["PEDV"])


app = App(app_ui, server)


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "8000")))

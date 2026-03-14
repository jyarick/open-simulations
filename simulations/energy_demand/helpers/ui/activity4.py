# helpers/ui/activity4.py

import ipywidgets as widgets
import IPython.display as ipd

from helpers.guards import require_users
from helpers.ui.power_outputs import run_power_outputs
from helpers.ui.power_plots import export_power_plots
from helpers.ui.energy_outputs import run_energy_outputs


def _hr_widget(label: str) -> widgets.HTML:
    """Gray titled separator as a WIDGET (safe to place inside VBox/HBox)."""
    return widgets.HTML(
        "<hr style='margin:14px 0;'>"
        f"<div style='color:#666; font-size:13px; margin:-10px 0 10px 0;'><b>{label}</b></div>"
    )


def _hr_display(label: str) -> None:
    """Gray titled separator as DISPLAY output (for export_out prints)."""
    ipd.display(ipd.HTML(
        "<hr style='margin:14px 0;'>"
        f"<div style='color:#666; font-size:13px; margin:-10px 0 10px 0;'><b>{label}</b></div>"
    ))


def show_activity4_export_button(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    excel_filename="act4_power.xlsx",
    scaled_png="users_power_plots_scaled.png",
    unscaled_png="users_power_plots_unscaled.png",
    table_png="max_power_table.png",
    energy_daily_png="users_energy_plots.png",
    energy_cumulative_png="users_cumulative_energy_plots.png",
    show_scaled=True,
    show_unscaled=True,
    show_24=True,
):
    """
    Export-only UI: shows ONE Export button.
    Clicking it saves:
      - energy plots (daily + cumulative)
      - power plots (scaled + unscaled)
      - max-power table PNG
      - Excel power dataframe

    It does NOT re-render the display plots/tables above.
    """
    if not require_users(state, 1, "Activity 4 Export"):
        return None

    export_btn = widgets.Button(
        description="Export Files (Plots + Tables + Excel)",
        button_style="success",
        layout=widgets.Layout(width="320px")
    )
    export_out = widgets.Output()

    def _do_export(_):
        export_btn.disabled = True
        export_btn.description = "Exporting..."
        try:
            with export_out:
                ipd.clear_output(wait=True)

                run_energy_outputs(
                    state=state,
                    minutes_per_step=minutes_per_step,
                    daily_png=energy_daily_png,
                    cumulative_png=energy_cumulative_png,
                    show_24=show_24,
                    export=True,
                    show_saved_messages=True
                )

                _hr_display("Power Plots Unscaled")
                if show_unscaled:
                    export_power_plots(
                        state=state,
                        all_users=all_users,
                        start_time=start_time,
                        end_time=end_time,
                        minutes_per_step=minutes_per_step,
                        scaled_users=False,
                        savepath=unscaled_png,
                        show_24=show_24
                    )
                    ipd.display(ipd.HTML(
                        f"<div style='color:green; margin-top:6px;'><b>✅ Saved:</b> <code>{unscaled_png}</code></div>"
                    ))

                _hr_display("Power Plots Scaled")
                if show_scaled:
                    export_power_plots(
                        state=state,
                        all_users=all_users,
                        start_time=start_time,
                        end_time=end_time,
                        minutes_per_step=minutes_per_step,
                        scaled_users=True,
                        savepath=scaled_png,
                        show_24=show_24
                    )
                    ipd.display(ipd.HTML(
                        f"<div style='color:green; margin-top:6px;'><b>✅ Saved:</b> <code>{scaled_png}</code></div>"
                    ))

                _hr_display("Exporting max-power table + Excel")

                run_power_outputs(
                    state=state,
                    all_users=all_users,
                    start_time=start_time,
                    end_time=end_time,
                    minutes_per_step=minutes_per_step,
                    excel_filename=excel_filename,
                    table_png=table_png,
                    export=True,
                    show_saved_messages=True,
                    display_table=False,  # no pandas table in export flow
                    display_png=True,     # show the PNG (the saved artifact)
                )

                ipd.display(ipd.HTML(
                    "<hr style='margin:14px 0;'>"
                    "<div style='color:green; font-weight:bold;'>✅ Export complete.</div>"
                    "<div style='color:#555; font-size:13px; margin-top:6px;'>"
                    "<b>Saved:</b> "
                    f"<code>{energy_daily_png}</code>, "
                    f"<code>{energy_cumulative_png}</code>, "
                    f"<code>{unscaled_png}</code>, "
                    f"<code>{scaled_png}</code>, "
                    f"<code>{table_png}</code>, "
                    f"<code>{excel_filename}</code>"
                    "</div>"
                ))
        finally:
            export_btn.disabled = False
            export_btn.description = "Export Files (Plots + Tables + Excel)"

    export_btn.on_click(_do_export)

    ipd.display(widgets.VBox([
        _hr_widget("Export"),
        widgets.HTML(
            "<div style='color:#666; font-size:13px; margin:6px 0 10px 0;'>"
            "Exports all required artifacts in one click. "
            "This button does not re-render the plots/tables above."
            "</div>"
        ),
        export_btn,
        export_out
    ]))

    return True

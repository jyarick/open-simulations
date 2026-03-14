# helpers/ui/energy_outputs.py

import ipywidgets as widgets
import IPython.display as ipd
import numpy as np

from helpers.guards import require_users
from helpers.render import plot_profiles_grid


def _hr(label=None):
    if label:
        ipd.display(ipd.HTML(
            f"<hr style='margin:14px 0;'>"
            f"<div style='color:#666; font-size:13px; margin:-10px 0 10px 0;'><b>{label}</b></div>"
        ))
    else:
        ipd.display(ipd.HTML("<hr style='margin:14px 0;'>"))


def run_energy_outputs(
    state,
    minutes_per_step=15,
    daily_png="users_energy_plots.png",
    cumulative_png="users_cumulative_energy_plots.png",
    show_24=True,
    export=False,
    show_saved_messages=True
):
    """
    Render energy plots (daily + cumulative). By default this is display-only.
    Set export=True to save PNG artifacts.
    """
    if not require_users(state, 1, "Energy Outputs"):
        return None

    if not hasattr(run_energy_outputs, "_out"):
        run_energy_outputs._out = widgets.Output()
    out = run_energy_outputs._out

    with out:
        ipd.clear_output(wait=True)

        _hr("Daily energy profiles (kWh)")
        plot_profiles_grid(
            state.modified_data,
            unit="kWh",
            savepath=(daily_png if export else None),
            title="Modified Daily Energy Profiles for Power Users",
            minutes_per_step=minutes_per_step,
            show_24=show_24
        )
        if export and show_saved_messages:
            ipd.display(ipd.HTML(f"<div style='color:green;'><b>✅ Saved:</b> <code>{daily_png}</code></div>"))

        _hr("Cumulative energy profiles (kWh)")
        cumulative = {
            k: np.cumsum(np.asarray(v, dtype=float))
            for k, v in state.modified_data.items()
        }
        plot_profiles_grid(
            cumulative,
            unit="kWh",
            savepath=(cumulative_png if export else None),
            title="Cumulative Energy Profiles for Power Users",
            minutes_per_step=minutes_per_step,
            show_24=show_24
        )
        if export and show_saved_messages:
            ipd.display(ipd.HTML(f"<div style='color:green;'><b>✅ Saved:</b> <code>{cumulative_png}</code></div>"))

    ipd.display(out)
    return True

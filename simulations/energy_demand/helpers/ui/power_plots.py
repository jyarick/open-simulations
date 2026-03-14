# helpers/ui/power_plots.py

import ipywidgets as widgets
import IPython.display as ipd

from helpers.guards import require_users
from helpers.metrics import build_power_dataframe
from helpers.render import plot_power_profiles_grid


def _hr(label):
    ipd.display(ipd.HTML(
        "<hr style='margin:14px 0;'>"
        f"<div style='color:#666; font-size:13px; margin:-10px 0 10px 0;'><b>{label}</b></div>"
    ))


# Separate, persistent outputs so scaled/unscaled don't overwrite each other
_PLOTS_OUT = {
    "unscaled": widgets.Output(),
    "scaled": widgets.Output(),
}


def show_power_plots(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    scaled_users=True,
    savepath=None,
    show_24=True,
    df_power=None,   # optional: allow caller to pass precomputed df
):
    if not require_users(state, 1, "Power Plots"):
        return None

    out = _PLOTS_OUT["scaled" if scaled_users else "unscaled"]

    with out:
        ipd.clear_output(wait=True)

        if df_power is None:
            df_power = build_power_dataframe(
                all_users=all_users,
                modified_data=state.modified_data,
                counts=state.counts,
                start_time=start_time,
                end_time=end_time,
                minutes_per_step=minutes_per_step
            )

        mode = "Scaled" if scaled_users else "Unscaled"
        _hr(f"Power Plots — {mode}")

        plot_power_profiles_grid(
            df_power=df_power,
            user_names=list(state.modified_data.keys()),
            title=f"Daily Power Consumption (kW) for User Types & Total Grid ({mode})",
            savepath=savepath,
            scaled_users=scaled_users,
            show_24=show_24,
            minutes_per_step=minutes_per_step
        )

        if savepath is not None and str(savepath).strip() != "":
            ipd.display(ipd.HTML(
                f"<div style='color:green; margin-top:6px;'><b>✅ Saved:</b> <code>{savepath}</code></div>"
            ))

    ipd.display(out)
    return df_power


def export_power_plots(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    scaled_users=True,
    savepath="users_power_plots.png",
    show_24=True,
    df_power=None,
):
    """
    Save-only power plots export (no widget outputs, no clearing displays).

    Use this for "Export Files" so clicking export does NOT overwrite the
    on-screen plot outputs created by show_power_plots().
    """
    if not require_users(state, 1, "Power Plots"):
        return None

    if df_power is None:
        df_power = build_power_dataframe(
            all_users=all_users,
            modified_data=state.modified_data,
            counts=state.counts,
            start_time=start_time,
            end_time=end_time,
            minutes_per_step=minutes_per_step
        )

    mode = "Scaled" if scaled_users else "Unscaled"

    plot_power_profiles_grid(
        df_power=df_power,
        user_names=list(state.modified_data.keys()),
        title=f"Daily Power Consumption (kW) for User Types & Total Grid ({mode})",
        savepath=savepath,
        scaled_users=scaled_users,
        show_24=show_24,
        minutes_per_step=minutes_per_step
    )

    return df_power

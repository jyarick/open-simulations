# helpers/ui/sections.py

import IPython.display as ipd
import ipywidgets as widgets

from helpers.guards import require_users
from helpers.tools import solve_scale_shift

try:
    from scipy.ndimage import gaussian_filter1d as _gaussian_filter1d
except Exception:
    _gaussian_filter1d = None



# -----------------------------------------------------------------------------
# Section 1 — Power User Selection
# -----------------------------------------------------------------------------

def show_power_user_selector(state, all_users, user_map, start_time, end_time, required_count=10):
    """Render Power User Selection UI in a stable output box (safe rerun)."""
    from helpers.ui.power_users import render_power_user_selector

    if not hasattr(show_power_user_selector, "_out"):
        show_power_user_selector._out = widgets.Output()
    out = show_power_user_selector._out

    with out:
        ipd.clear_output(wait=True)
        render_power_user_selector(
            state=state,
            all_users=all_users,
            user_map=user_map,
            start_time=start_time,
            end_time=end_time,
            required_count=required_count,
        )

    ipd.display(out)
    return None


# -----------------------------------------------------------------------------
# Scratch Tool — Scale + Shift Calculator (pure scratch; no state)
# -----------------------------------------------------------------------------

def show_scale_shift_calculator():
    """
    Pure scratch calculator.
    No state read/write. No refresh hooks.
    Uses canonical solve_scale_shift.
    """
    if not hasattr(show_scale_shift_calculator, "_out"):
        show_scale_shift_calculator._out = widgets.Output()
        show_scale_shift_calculator._built = False

    out = show_scale_shift_calculator._out

    # Build widgets once (avoids recreating inputs/buttons every rerun)
    if not getattr(show_scale_shift_calculator, "_built", False):
        E0_min = widgets.FloatText(description="E_0_min:", layout={"width": "150px"})
        E0_max = widgets.FloatText(description="E_0_max:", layout={"width": "150px"})
        E1_min = widgets.FloatText(description="E_1_min:", layout={"width": "150px"})
        E1_max = widgets.FloatText(description="E_1_max:", layout={"width": "150px"})

        compute_btn = widgets.Button(
            description="Compute Scale + Shift",
            button_style="success",
            layout={"width": "180px"},
        )
        result_out = widgets.Output()

        def compute(_):
            with result_out:
                ipd.clear_output(wait=True)
                try:
                    a, b = solve_scale_shift(E0_min.value, E0_max.value, E1_min.value, E1_max.value)
                except Exception as e:
                    print(f"⚠️ {e}")
                    return
                print("Model: E_1 = a·E_0 + b\n")
                print(f"a (scale) = {a:.6f}")
                print(f"b (shift) = {b:.6f}")

        compute_btn.on_click(compute)

        panel = widgets.VBox(
            [
                widgets.HTML("<h2 style='color:purple;'>Linear Calibration (Scale + Shift)</h2>"),
                widgets.HTML("Solve <b>E<sub>1</sub> = a·E<sub>0</sub> + b</b> from two known endpoints."),
                widgets.HBox([E0_min, E0_max]),
                widgets.HBox([E1_min, E1_max]),
                compute_btn,
                result_out,
            ]
        )

        show_scale_shift_calculator._panel = panel
        show_scale_shift_calculator._built = True

    with out:
        ipd.clear_output(wait=True)
        ipd.display(show_scale_shift_calculator._panel)

    ipd.display(out)
    return None


# -----------------------------------------------------------------------------
# Section 2 — Math Editor
# -----------------------------------------------------------------------------

def show_math_editor(state, minutes_per_step=15):
    if not require_users(state, 1, "the Math Editor"):
        return None

    import scipy as sp
    from helpers.ui.math_editor import render_math_editor
    from helpers.render import format_x_day, format_y_units

    return render_math_editor(
        state=state,
        format_x_day=format_x_day,
        format_y_units=format_y_units,
        minutes_per_step=minutes_per_step,
        gaussian_filter1d=_gaussian_filter1d,
    )


# -----------------------------------------------------------------------------
# Building Counts
# -----------------------------------------------------------------------------

def show_building_counts(state, min_count=1, max_count=50):
    if not require_users(state, 1, "Building Counts"):
        return None
    from helpers.ui.building_counts import render_building_counts

    return render_building_counts(state, min_count=min_count, max_count=max_count)


# -----------------------------------------------------------------------------
# Activity 4 — Energy Outputs (display-only; auto-refresh)
# -----------------------------------------------------------------------------

def show_energy_outputs(
    state,
    minutes_per_step=15,
    daily_png="users_energy_plots.png",
    cumulative_png="users_cumulative_energy_plots.png",
    show_24=True,
):
    if not require_users(state, 1, "Energy Outputs"):
        return None

    from helpers.ui.energy_outputs import run_energy_outputs

    if not hasattr(show_energy_outputs, "_out"):
        show_energy_outputs._out = widgets.Output()
    out = show_energy_outputs._out

    def _render():
        with out:
            ipd.clear_output(wait=True)
            run_energy_outputs(
                state=state,
                minutes_per_step=minutes_per_step,
                daily_png=daily_png,
                cumulative_png=cumulative_png,
                show_24=show_24,
                export=False,
            )

    # Avoid rebinding observers per state instance
    if not hasattr(show_energy_outputs, "_bound_states"):
        show_energy_outputs._bound_states = set()

    sig = getattr(state, "_state_signal", None)
    if sig is not None:
        sid = id(state)
        if sid not in show_energy_outputs._bound_states:
            sig.observe(lambda _: _render(), names="value")
            show_energy_outputs._bound_states.add(sid)

    _render()
    ipd.display(out)
    return True


# -----------------------------------------------------------------------------
# Activity 4 — Power Outputs (display-only; auto-refresh)
# -----------------------------------------------------------------------------

def show_power_outputs(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    excel_filename="act4_power.xlsx",
    table_png="max_power_table.png",
):
    if not require_users(state, 1, "Power Outputs"):
        return None

    from helpers.ui.power_outputs import run_power_outputs

    if not hasattr(show_power_outputs, "_out"):
        show_power_outputs._out = widgets.Output()
    out = show_power_outputs._out

    def _render():
        with out:
            ipd.clear_output(wait=True)
            run_power_outputs(
                state=state,
                all_users=all_users,
                start_time=start_time,
                end_time=end_time,
                minutes_per_step=minutes_per_step,
                excel_filename=excel_filename,
                table_png=table_png,
                export=False,
            )

    # Avoid rebinding observers per state instance
    if not hasattr(show_power_outputs, "_bound_states"):
        show_power_outputs._bound_states = set()

    sig = getattr(state, "_state_signal", None)
    if sig is not None:
        sid = id(state)
        if sid not in show_power_outputs._bound_states:
            sig.observe(lambda _: _render(), names="value")
            show_power_outputs._bound_states.add(sid)

    _render()
    ipd.display(out)
    return None


# -----------------------------------------------------------------------------
# Activity 4 — Power Plots (display-only; auto-refresh)
# -----------------------------------------------------------------------------

def show_power_plots(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    scaled_users=True,
    savepath=None,
    show_24=True,
):
    """
    Display-only wrapper around helpers.ui.power_plots.show_power_plots.

    - Uses a stable output box (safe rerun)
    - Auto-refreshes on state._state_signal changes
    """
    if not require_users(state, 1, "Power Plots"):
        return None

    from helpers.ui.power_plots import show_power_plots as _show

    # Separate persistent outputs for scaled/unscaled so they don't overwrite each other
    if not hasattr(show_power_plots, "_outs"):
        show_power_plots._outs = {
            "unscaled": widgets.Output(),
            "scaled": widgets.Output(),
        }

    out = show_power_plots._outs["scaled" if scaled_users else "unscaled"]

    def _render():
        with out:
            ipd.clear_output(wait=True)
            _show(
                state=state,
                all_users=all_users,
                start_time=start_time,
                end_time=end_time,
                minutes_per_step=minutes_per_step,
                scaled_users=scaled_users,
                savepath=savepath,
                show_24=show_24,
                df_power=None,  # let module compute internally
            )

    # Avoid rebinding observers per state instance AND per mode
    if not hasattr(show_power_plots, "_bound_states"):
        show_power_plots._bound_states = set()

    sig = getattr(state, "_state_signal", None)
    if sig is not None:
        sid = id(state)
        key = (sid, "scaled" if scaled_users else "unscaled")
        if key not in show_power_plots._bound_states:
            sig.observe(lambda _: _render(), names="value")
            show_power_plots._bound_states.add(key)

    _render()
    ipd.display(out)
    return None


# -----------------------------------------------------------------------------
# Activity 4 — Compute outputs (returns df_power, max_power_table)
# -----------------------------------------------------------------------------

def run_activity4_outputs(state, all_users, start_time, end_time, minutes_per_step=15):
    from helpers.ui.power_outputs import run_power_outputs
    return run_power_outputs(
        state=state,
        all_users=all_users,
        start_time=start_time,
        end_time=end_time,
        minutes_per_step=minutes_per_step,
        export=False,
    )


# -----------------------------------------------------------------------------
# Activity 4 — Export button (stable output box)
# -----------------------------------------------------------------------------

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
    Wrapper for helpers.ui.activity4.show_activity4_export_button
    but rendered inside a stable Output box (safe rerun / no duplicates).
    """
    if not require_users(state, 1, "Activity 4 Export"):
        return None

    from helpers.ui.activity4 import show_activity4_export_button as _show

    if not hasattr(show_activity4_export_button, "_out"):
        show_activity4_export_button._out = widgets.Output()
    out = show_activity4_export_button._out

    with out:
        ipd.clear_output(wait=True)
        _show(
            state=state,
            all_users=all_users,
            start_time=start_time,
            end_time=end_time,
            minutes_per_step=minutes_per_step,
            excel_filename=excel_filename,
            scaled_png=scaled_png,
            unscaled_png=unscaled_png,
            table_png=table_png,
            energy_daily_png=energy_daily_png,
            energy_cumulative_png=energy_cumulative_png,
            show_scaled=show_scaled,
            show_unscaled=show_unscaled,
            show_24=show_24,
        )

    ipd.display(out)
    return True


# -----------------------------------------------------------------------------
# Small utility
# -----------------------------------------------------------------------------

def banner(text, color="gray"):
    ipd.display(ipd.HTML(f"<p style='color:{color}; margin: 6px 0;'><b>{text}</b></p>"))

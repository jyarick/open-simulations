# helpers/ui/math_editor.py

import numpy as np
import ipywidgets as widgets
import IPython.display as ipd
import matplotlib.pyplot as plt

from helpers.core import sync_state as core_sync_state, emit_change
from helpers.transform import transform_data_using_params
from helpers.tools import get_rng, steps_per_day


def render_math_editor(
    state,
    format_x_day,
    format_y_units,
    minutes_per_step=15,
    gaussian_filter1d=None
):
    """Data Transformation Editor UI (no auto-select; clear resets defaults)."""

    core_sync_state(state, verbose=False)
    output_custom = widgets.Output()

    user_select = widgets.Combobox(
        options=sorted(list(state.modified_data.keys())),
        description="User Type:",
        ensure_option=False,
        layout={"width": "360px"}
    )

    clear_user_select_btn = widgets.Button(
        description="✕",
        tooltip="Clear search text",
        layout=widgets.Layout(width="35px", height="28px")
    )
    user_select_row = widgets.HBox([user_select, clear_user_select_btn])

    W180 = {"width": "180px"}

    scale_input      = widgets.FloatText(description="Scale Factor:", layout=W180)
    shift_input      = widgets.FloatText(description="Shift/Offset:", layout=W180)
    noise_input      = widgets.FloatText(description="Noise/Jitter:", layout=W180)
    f_input          = widgets.FloatText(description="Deviation:", layout=W180)
    smooth_input     = widgets.IntText(description="Smoothness:", layout=W180)
    time_shift_input = widgets.IntText(description="Time Shift:", layout=W180)

    # RNG intent widgets (do NOT auto-mutate state on toggle)
    noise_seed_w = widgets.IntText(
        value=0,
        description="Noise Seed:",
        layout=W180
    )
    lock_noise_cb = widgets.Checkbox(
        value=False,
        description="Lock noise (reproducible)"
    )

    preview_button = widgets.Button(description="Preview Changes", button_style="info", layout={"width": "160px"})
    apply_button   = widgets.Button(description="Apply Changes",   button_style="success", layout={"width": "160px"})
    revert_button  = widgets.Button(description="Revert to Original", button_style="warning", layout={"width": "160px"})

    time_weights_labels = [f"{h:02d}-{h+1:02d}h" for h in range(24)]
    time_weights_widgets = [widgets.FloatText(layout={"width": "70px"}) for _ in range(24)]
    labeled_tw = [
        widgets.HBox([widgets.Label(value=time_weights_labels[i], layout={"width": "50px"}), time_weights_widgets[i]])
        for i in range(24)
    ]
    weights_rows = widgets.VBox([widgets.HBox(labeled_tw[i*6:(i+1)*6]) for i in range(4)])

    load_status_html   = widgets.HTML("")
    action_status_html = widgets.HTML("")

    internals = {"suppress_user_change": False}
    current_user = {"name": None}  # track which user is currently selected
    

    def _defaults():
        scale_input.value = 1.0
        shift_input.value = 0.0
        noise_input.value = 0.0
        f_input.value = 1.0
        smooth_input.value = 0
        time_shift_input.value = 0
        noise_seed_w.value = 0
        lock_noise_cb.value = False
        for w in time_weights_widgets:
            w.value = 1.0

    _defaults()

    def clear_preview(msg=""):
        with output_custom:
            output_custom.clear_output(wait=True)
            if msg:
                print(msg)

    def _get_selected_user_or_none():
        name = (user_select.value or "").strip()
        return name if (name in set(user_select.options)) else None

    def refresh_user_select_options(keep_value=True):
        opts = sorted(list(state.modified_data.keys()))
        cur = (user_select.value or "").strip()

        internals["suppress_user_change"] = True
        try:
            user_select.options = opts

            if not opts:
                user_select.value = ""
                load_status_html.value = "<p style='color:red;'>⚠️ No users available. Add users first.</p>"
                return

            if keep_value and (cur in opts):
                user_select.value = cur
            else:
                user_select.value = ""  # ✅ no auto-select
        finally:
            internals["suppress_user_change"] = False

    def _on_state_signal_change(change):
        core_sync_state(state, verbose=False)
        refresh_user_select_options(keep_value=True)

        if _get_selected_user_or_none() is None:
            load_status_html.value = "<p style='color:gray;'>Type to search, then pick a user.</p>"

        clear_preview("User list updated.")
        action_status_html.value = ""

    sig = getattr(state, "_state_signal", None)
    if sig is not None:
        flag = getattr(state, "_math_editor_bound", False)
        if not flag:
            sig.observe(_on_state_signal_change, names="value")
            setattr(state, "_math_editor_bound", True)

    def load_user_params_into_widgets(name):
        if name not in state.params:
            state.params[name] = dict(state.default_params)
            state.params[name]["time_weights"] = list(state.default_params["time_weights"])

        params = state.params[name]
        params.setdefault("noise_seed", 0)
        params.setdefault("lock_noise", False)
        
        scale_input.value      = float(params.get("scale", 1.0))
        shift_input.value      = float(params.get("shift", 0.0))
        noise_input.value      = float(params.get("noise", 0.0))
        f_input.value          = float(params.get("f", 1.0))
        smooth_input.value     = int(params.get("smooth", 0))
        time_shift_input.value = int(params.get("time_shift", 0))

        tw = params.get("time_weights", state.default_params["time_weights"])
        for i, w in enumerate(time_weights_widgets):
            w.value = float(tw[i] if i < len(tw) else 1.0)

        noise_seed_w.value = int(params.get("noise_seed", 0))
        lock_noise_cb.value = bool(params.get("lock_noise", False))

        load_status_html.value = f"<p style='color:blue;'>📂 Loaded parameters for <b>{name}</b></p>"

    def save_widgets_to_params(name):
        state.params[name] = {
            "scale": float(scale_input.value),
            "shift": float(shift_input.value),
            "noise": float(noise_input.value),
            "f": float(f_input.value),
            "smooth": int(smooth_input.value),
            "time_shift": int(time_shift_input.value),
            "time_weights": [float(w.value) for w in time_weights_widgets],
            "noise_seed": int(noise_seed_w.value),
            "lock_noise": bool(lock_noise_cb.value),

        }

    def _get_rng():
        """Return RNG consistent with UI lock/seed (no state mutation)."""
        locked = bool(lock_noise_cb.value)
        seed = int(noise_seed_w.value)
        return get_rng(seed=seed, locked=locked)


    def _clear_user_select(_=None):
        internals["suppress_user_change"] = True
        current_user["name"] = None
        try:
            user_select.value = ""
        finally:
            internals["suppress_user_change"] = False

        _defaults()
        load_status_html.value = "<p style='color:gray;'>Type to search, then pick a user.</p>"
        action_status_html.value = ""
        clear_preview("Cleared selection. Choose a user.")

    clear_user_select_btn.on_click(_clear_user_select)

    def on_user_change(change):
        if change.get("name") != "value":
            return
        if internals.get("suppress_user_change", False):
            return

        selected = _get_selected_user_or_none()
        action_status_html.value = ""

        if selected is None:
            load_status_html.value = "<p style='color:gray;'>Type to search, then pick a user.</p>"
            return
            
        current_user["name"] = selected

        clear_preview("Selection updated.")
        load_user_params_into_widgets(selected)

    user_select.observe(on_user_change, names="value")

    def preview_changes(_=None):
        name = _get_selected_user_or_none()
        action_status_html.value = ""

        if name is None:
            action_status_html.value = "<p style='color:red;'>⚠️ Pick a user from the list to preview.</p>"
            return
        if name not in state.original_data:
            action_status_html.value = "<p style='color:red;'>⚠️ Missing original data for this user. Re-add the user.</p>"
            return

        orig = np.asarray(state.original_data[name]["daily_data"], dtype=float)

        temp_params = {
            "scale": float(scale_input.value),
            "shift": float(shift_input.value),
            "noise": float(noise_input.value),
            "f": float(f_input.value),
            "smooth": int(smooth_input.value),
            "time_shift": int(time_shift_input.value),
            "time_weights": [float(w.value) for w in time_weights_widgets],
        }

        modified = transform_data_using_params(
            orig,
            temp_params,
            minutes_per_step=minutes_per_step,
            rng=_get_rng(),
            gaussian_filter1d=gaussian_filter1d
        )

        with output_custom:
            output_custom.clear_output(wait=True)
            fig, axs = plt.subplots(1, 2, figsize=(14, 4), dpi=120, constrained_layout=True)

            t = np.arange(len(orig))
            axs[0].plot(t, orig, linestyle="--", lw=2)
            axs[0].set_title(f"{name} — Original")

            axs[1].plot(t, modified, lw=2)
            axs[1].set_title(f"{name} — Modified (preview)")

            ppd = steps_per_day(minutes_per_step)
            for ax in axs:
                ax.grid(alpha=0.3)
                format_x_day(ax, points_per_day=ppd, minutes_per_step=minutes_per_step, tick_hours=4, show_24=True)
                format_y_units(ax, unit="kWh", decimals=2, max_ticks=6)
                ax.set_xlabel("Time of Day")
                ax.set_ylabel("Energy (kWh)")

            ipd.display(fig)
            plt.close(fig)

        action_status_html.value = f"<p style='color:blue;'>👀 Preview done for <b>{name}</b>.</p>"

    preview_button.on_click(preview_changes)

    def apply_changes(_=None):
        name = _get_selected_user_or_none()
        action_status_html.value = ""

        if name is None:
            action_status_html.value = "<p style='color:red;'>⚠️ Pick a user from the list to apply.</p>"
            return
        if name not in state.original_data:
            action_status_html.value = "<p style='color:red;'>⚠️ Missing original data for this user. Re-add the user.</p>"
            return

        save_widgets_to_params(name)

        orig = np.asarray(state.original_data[name]["daily_data"], dtype=float)
        params = state.params[name]

        modified_array = transform_data_using_params(
            orig,
            params,
            minutes_per_step=minutes_per_step,
            rng=_get_rng(),
            gaussian_filter1d=gaussian_filter1d
        )

        state.modified_data[name] = modified_array.copy()

        emit_change(state, "apply transform", sync=True)

        clear_preview("Applied changes.")
        action_status_html.value = f"<p style='color:green;'>✅ <b>Applied</b> changes to <b>{name}</b></p>"

    apply_button.on_click(apply_changes)

    def revert_original(_=None):
        name = _get_selected_user_or_none()
        action_status_html.value = ""

        if name is None:
            action_status_html.value = "<p style='color:red;'>⚠️ Pick a user from the list to revert.</p>"
            return
        if name not in state.original_data:
            action_status_html.value = "<p style='color:red;'>⚠️ Missing original data for this user. Re-add the user.</p>"
            return

        orig = np.asarray(state.original_data[name]["daily_data"], dtype=float)
        state.modified_data[name] = orig.copy()

        state.params[name] = dict(state.default_params)
        state.params[name]["time_weights"] = list(state.default_params["time_weights"])
        
        # reset per-user noise controls too
        state.params[name]["noise_seed"] = 0
        state.params[name]["lock_noise"] = False

        load_user_params_into_widgets(name)


        emit_change(state, "revert", sync=True)

        clear_preview("Reverted to original.")
        action_status_html.value = "<p style='color:orange;'>↩️ <b>Reverted</b> to original data and default parameter values.</p>"

    revert_button.on_click(revert_original)

    refresh_user_select_options(keep_value=False)
    user_select.value = ""
    load_status_html.value = "<p style='color:gray;'>Type to search, then pick a user.</p>"
    clear_preview("")

    ipd.display(widgets.VBox([
        widgets.HTML("<h3 style='font-size:22px; font-weight:bold; color:purple;'>Data Transformation Editor</h3>"),
        widgets.HTML("<small><b>Select a User Type:</b></small>"),
        user_select_row,
        load_status_html,
        widgets.HTML("<hr><small><b>Adjustable Math Parameters:</b></small>"),
        widgets.HBox([scale_input, shift_input, noise_input]),
        widgets.HBox([f_input, smooth_input, time_shift_input]),
        widgets.HBox([noise_seed_w, lock_noise_cb]),
        widgets.HTML("<hr><small><b>Hourly Time Weights:</b></small>"),
        weights_rows,
        widgets.HTML("<hr>"),
        widgets.HBox([preview_button, apply_button, revert_button]),
        action_status_html,
        output_custom,
    ]))

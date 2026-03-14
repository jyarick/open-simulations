# helpers/ui/building_counts.py

import ipywidgets as widgets
import IPython.display as ipd

from helpers.core import sync_state as core_sync_state, emit_change


def render_building_counts(state, min_count=1, max_count=50):
    """
    Render sliders to choose number of buildings per selected user type.
    Uses state.counts[name] as source of truth.

    Auto-refreshes when state._state_signal changes (if present).

    Key behavior:
      - Status output is NOT overwritten on every re-render (prevents flicker).
      - Confirm/Reset write the status and it stays.
      - If roster changes, status updates to "Loaded ..." once.
    """

    label = widgets.HTML("""
    <span style='font-size:20px; font-weight:bold; color:purple;'>
        Building Counts Editor
    </span>
    """)

    output_sliders = widgets.Output()

    confirm_button = widgets.Button(description="Confirm Selection", button_style="success")
    reset_button   = widgets.Button(description="Reset to 1", button_style="warning")

    sliders_box = widgets.VBox([], layout=widgets.Layout(width="760px"))

    slider_by_user = {}

    # -----------------------------
    # Status helpers (anti-flicker)
    # -----------------------------
    # Persist last "meaningful" status in state so rerenders can keep it.
    if not hasattr(state, "_building_counts_status_lines"):
        state._building_counts_status_lines = []
    if not hasattr(state, "_building_counts_last_roster"):
        state._building_counts_last_roster = None

    def _set_status(lines):
        state._building_counts_status_lines = list(lines)
        with output_sliders:
            ipd.clear_output(wait=True)
            for line in state._building_counts_status_lines:
                print(line)

    def _ensure_status_visible(default_lines):
        # Only write something if status is currently empty (first render).
        if not state._building_counts_status_lines:
            _set_status(default_lines)
        else:
            # Re-display existing lines without changing them
            with output_sliders:
                ipd.clear_output(wait=True)
                for line in state._building_counts_status_lines:
                    print(line)

    # -----------------------------
    # Slider rendering
    # -----------------------------
    def render_sliders():
        core_sync_state(state, verbose=False)

        slider_by_user.clear()
        rows = []

        roster = tuple(sorted(state.modified_data.keys()))

        for user_name in roster:
            state.counts.setdefault(user_name, 1)

            lbl = widgets.Label(value=user_name, layout=widgets.Layout(width="250px"))
            sldr = widgets.IntSlider(
                min=min_count,
                max=max_count,
                value=int(state.counts[user_name]),
                description="",
                layout=widgets.Layout(width="460px"),
                continuous_update=True,
            )
            slider_by_user[user_name] = sldr
            rows.append(widgets.HBox([lbl, sldr]))

        sliders_box.children = rows

        # Only update status if the roster changed (otherwise keep last Confirm output)
        if roster != state._building_counts_last_roster:
            state._building_counts_last_roster = roster
            if not rows:
                _set_status(["No users added yet. Add power users first."])
            else:
                _set_status([f"Loaded {len(rows)} user type(s). Adjust sliders, then click Confirm."])
        else:
            # Keep whatever status user last saw (no flicker)
            _ensure_status_visible(["(Status will appear here after you confirm or reset.)"])

    # -----------------------------
    # Handlers
    # -----------------------------
    def on_confirm_clicked(_):
        core_sync_state(state, verbose=False)

        if not slider_by_user:
            _set_status(["No users to confirm. Add power users first."])
            return

        lines = []
        for user_name, sldr in slider_by_user.items():
            if user_name in state.modified_data:
                state.counts[user_name] = int(sldr.value)
                lines.append(f"{user_name}: {state.counts[user_name]} building(s)")

        _set_status(lines)

        # Trigger downstream refresh (power plots/tables)
        emit_change(state, "confirm building counts", sync=False)

    def on_reset_clicked(_):
        core_sync_state(state, verbose=False)

        if not slider_by_user:
            _set_status(["No users to reset. Add power users first."])
            emit_change(state, "reset building counts", sync=False)
            return

        for user_name, sldr in slider_by_user.items():
            if user_name in state.modified_data:
                state.counts[user_name] = 1
                sldr.value = 1

        _set_status(["Reset complete: all building counts set to 1."])

        # Trigger downstream refresh
        emit_change(state, "reset building counts", sync=False)

    confirm_button.on_click(on_confirm_clicked)
    reset_button.on_click(on_reset_clicked)

    # -----------------------------
    # Auto-refresh when roster changes
    # -----------------------------
    def _on_state_signal_change(change):
        if change.get("name") != "value":
            return
        render_sliders()

    sig = getattr(state, "_state_signal", None)
    if sig is not None:
        if not getattr(state, "_building_counts_bound", False):
            sig.observe(_on_state_signal_change, names="value")
            setattr(state, "_building_counts_bound", True)

    # Initial render
    render_sliders()

    ipd.display(
        label,
        sliders_box,
        widgets.HBox([confirm_button, reset_button]),
        output_sliders
    )

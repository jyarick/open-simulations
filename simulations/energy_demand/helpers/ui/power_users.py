# helpers/ui/power_users.py

import re
import ipywidgets as widgets
import IPython.display as ipd

from helpers.core import (
    sync_state as core_sync_state,
    emit_change,
    rename_user,
    delete_user_by_index,
    add_user_record,
)


def render_power_user_selector(state, all_users, user_map, start_time, end_time, required_count=10):
    """
    Power User Selection UI (Add / Rename / Delete).

    Contract:
      - Mutate state via helpers.core functions
      - Call emit_change(...) exactly once per mutation (canonical UI refresh signal)
      - No manual bumping/signal hacks in this module
    """

    editor_box = widgets.Output()
    preview_box = widgets.Output()

    # ---------- Checkboxes ----------
    checkboxes = [
        widgets.Checkbox(value=False, description=key, indent=False)
        for key in sorted(user_map.keys())
    ]

    # ---------- Buttons ----------
    add_btn = widgets.Button(description="Add Power User", button_style="info")
    check_btn = widgets.Button(description="Check User Count", button_style="success")
    remove_all_btn = widgets.Button(description="Remove All Users", button_style="danger")
    select_all_btn = widgets.Button(description="Select All")
    clear_all_btn = widgets.Button(description="Clear All")

    # ---------- Search ----------
    search = widgets.Text(
        placeholder="Search user types...",
        layout=widgets.Layout(width="300px")
    )
    clear_search_btn = widgets.Button(description="✕", layout=widgets.Layout(width="35px"))
    search_row = widgets.HBox([search, clear_search_btn])

    checked_status = widgets.HTML("")

    # ---------- UI helpers ----------
    def _clear_preview():
        with preview_box:
            ipd.clear_output(wait=True)

    def update_checked_status(_=None):
        visible = sum(cb.layout.display != "none" for cb in checkboxes)
        checked = sum(cb.value and cb.layout.display != "none" for cb in checkboxes)
        checked_status.value = f"<span style='color:gray;'>Showing: <b>{visible}</b> | Checked: <b>{checked}</b></span>"

    def apply_search(change):
        q = (change["new"] or "").lower().strip()
        for cb in checkboxes:
            cb.layout.display = "" if q in cb.description.lower() else "none"
        update_checked_status()

    def clear_search(_=None):
        search.value = ""

    search.observe(apply_search, names="value")
    clear_search_btn.on_click(clear_search)

    for cb in checkboxes:
        cb.observe(update_checked_status, names="value")

    def select_all(_=None):
        for cb in checkboxes:
            if cb.layout.display != "none":
                cb.value = True
        update_checked_status()

    def clear_all(_=None):
        clear_search()
        for cb in checkboxes:
            cb.value = False
        update_checked_status()

    select_all_btn.on_click(select_all)
    clear_all_btn.on_click(clear_all)

    # ---------- Editor ----------
    def render_editor():
        with editor_box:
            ipd.clear_output(wait=True)

            remaining = max(0, required_count - len(state.entries))
            ipd.display(ipd.HTML(
                f"<b>Current Power Users:</b> "
                f"<span style='color:gray'>(count: {len(state.entries)} | remaining: {remaining})</span>"
            ))

            if not state.entries:
                ipd.display(ipd.HTML("<i>No power users added yet.</i>"))
                return

            rows = []
            for entry in state.entries:
                # always read live from entry (never captured)
                name_label = widgets.Label(entry.get("current_name", ""), layout=widgets.Layout(width="200px"))
                rename_box = entry["rename_widget"]

                rename_btn = widgets.Button(description="Rename", button_style="warning")
                delete_btn = widgets.Button(description="Delete", button_style="danger")
                status = widgets.HTML("")

                def on_rename(_b, e=entry, status=status):
                    _clear_preview()
                    status.value = ""

                    old = (e.get("current_name") or "").strip()
                    new = (e["rename_widget"].value or "").strip()

                    if not new:
                        status.value = "<span style='color:red;'>⚠️ Name cannot be blank.</span>"
                        return

                    try:
                        rename_user(state, e, old, new)
                    except Exception as ex:
                        status.value = f"<span style='color:red;'>⚠️ {ex}</span>"
                        # keep user's typed value; don't force revert
                        return

                    core_sync_state(state, verbose=False)
                    emit_change(state, note="rename user", sync=False)
                    render_editor()

                def on_delete(_b, e=entry):
                    _clear_preview()
                    try:
                        idx = state.entries.index(e)
                    except ValueError:
                        return
                    delete_user_by_index(state, idx)
                    core_sync_state(state, verbose=False)
                    emit_change(state, note="delete user", sync=False)
                    render_editor()

                rename_btn.on_click(on_rename)
                delete_btn.on_click(on_delete)

                rows.append(widgets.HBox([name_label, rename_box, rename_btn, delete_btn, status]))

            ipd.display(widgets.VBox(rows))
            ipd.display(ipd.HTML("<hr>"))

    # ---------- Add Users ----------
    def add_checked_users(_=None):
        _clear_preview()
        added = []

        for cb in checkboxes:
            if not cb.value:
                continue

            formal = cb.description
            template_key = user_map[formal]
            col = f"{template_key}_kWh"

            if col not in all_users.columns:
                with preview_box:
                    print(f"⚠️ Missing column: {col}")
                cb.value = False
                continue

            data = all_users[col].iloc[start_time:end_time].to_numpy()

            # Guard: keep intent explicit (15-min window)
            if len(data) != 96:
                with preview_box:
                    print(f"⚠️ Bad window length for {formal}: got {len(data)} (expected 96).")
                cb.value = False
                continue

            base = formal
            nums = []
            for k in state.modified_data:
                if k.startswith(base):
                    m = re.match(rf"^{re.escape(base)}(?: (\d+))?$", k)
                    if m:
                        nums.append(int(m.group(1) or 1))

            n = max(nums, default=0) + 1
            display_name = f"{base} {n}" if n > 1 else base

            rename_box = widgets.Text(value=display_name, layout=widgets.Layout(width="300px"))

            add_user_record(
                state=state,
                template_key=template_key,
                formal_name=formal,
                display_name=display_name,
                daily_data=data,
                rename_widget=rename_box,
            )

            cb.value = False
            added.append(display_name)

        if added:
            core_sync_state(state, verbose=False)
            emit_change(state, note="add users", sync=False)
            render_editor()
            with preview_box:
                print(f"✅ Added: {', '.join(added)}")
        else:
            with preview_box:
                print("Nothing was checked. Check at least one user type, then click Add Power User.")

        update_checked_status()

    add_btn.on_click(add_checked_users)

    # ---------- Check count ----------
    def check_user_count(_=None):
        _clear_preview()
        with preview_box:
            if len(state.entries) != required_count:
                print(f"❌ You must have exactly {required_count} power users. Currently {len(state.entries)}.")
                return
            print(f"✅ Power User Count Check Passed ({required_count} selected):")
            for i, e in enumerate(state.entries, start=1):
                print(f"{i}. {e.get('current_name', '').strip()}  (based on {e.get('formal_name', '')})")

    check_btn.on_click(check_user_count)

    # ---------- Remove all ----------
    def remove_all(_=None):
        _clear_preview()
        state.entries.clear()
        state.original_data.clear()
        state.modified_data.clear()
        state.params.clear()
        state.counts.clear()

        core_sync_state(state, verbose=False)
        emit_change(state, note="remove all users", sync=False)

        clear_all()
        render_editor()
        with preview_box:
            print("✅ Removed all users.")

    remove_all_btn.on_click(remove_all)

    # ---------- Initial render ----------
    apply_search({"new": ""})
    update_checked_status()
    render_editor()

    ipd.display(widgets.VBox([
        widgets.HTML("<h2 style='font-size:22px; font-weight:bold; color:purple;'>Power Users Selection Editor</h2>"),
        widgets.HBox([select_all_btn, clear_all_btn]),
        search_row,
        checked_status,
        widgets.GridBox(checkboxes, layout=widgets.Layout(grid_template_columns="repeat(3, 1fr)")),
        add_btn,
        widgets.HTML("<hr><i>Edit the name, then click Rename.</i>"),
        editor_box,
        widgets.HBox([check_btn, remove_all_btn]),
        preview_box
    ], layout=widgets.Layout(width="100%")))

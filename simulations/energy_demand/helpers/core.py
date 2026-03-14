# helpers/core.py
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np


def fresh_default_params(default_params: Dict[str, Any]) -> Dict[str, Any]:
    """Return a fresh copy (avoid shared list references)."""
    p = dict(default_params)
    if "time_weights" in p:
        p["time_weights"] = list(p["time_weights"])
    return p


def get_entry_name(entry: Dict[str, Any]) -> str:
    """Best-effort: return current active name for an entry."""
    name = (entry.get("current_name") or "").strip()
    if name:
        return name
    rw = entry.get("rename_widget")
    if rw is not None:
        return (getattr(rw, "value", "") or "").strip()
    return ""


def sync_state(state, verbose: bool = False) -> List[str]:
    """
    Keep dict stores consistent with entries.
    Invariant:
      keys(original_data)==keys(modified_data)==keys(params)==keys(counts)==active_names
    """
    active_names: List[str] = []
    seen = set()

    for e in state.entries:
        name = get_entry_name(e)
        if not name:
            continue
        e["current_name"] = name
        if name not in seen:
            active_names.append(name)
            seen.add(name)

    active_set = set(active_names)

    def prune(d: Dict[str, Any], label: str):
        stray = set(d.keys()) - active_set
        for k in stray:
            d.pop(k, None)
        if verbose and stray:
            print(f"🧹 pruned from {label}: {sorted(stray)}")

    prune(state.original_data, "original_data")
    prune(state.modified_data, "modified_data")
    prune(state.params, "params")
    prune(state.counts, "counts")

    for name in active_names:
        state.counts.setdefault(name, 1)

        if name not in state.params:
            state.params[name] = fresh_default_params(state.default_params)
        else:
            # Fill missing keys; ensure time_weights is a real list length 24
            for k, v in state.default_params.items():
                if k == "time_weights":
                    tw = state.params[name].get("time_weights")
                    if (tw is None) or (len(tw) != 24):
                        state.params[name]["time_weights"] = list(state.default_params["time_weights"])
                    else:
                        state.params[name]["time_weights"] = list(tw)
                else:
                    state.params[name].setdefault(k, v)

    return active_names


def rename_user(state, entry: Dict[str, Any], old_name: str, new_name: str) -> None:
    """Rename keys across all stores and update entry current_name."""
    old_name = (old_name or "").strip()
    new_name = (new_name or "").strip()

    if (not new_name) or (new_name == old_name):
        entry["current_name"] = old_name
        return

    if (new_name in state.modified_data or new_name in state.original_data) and new_name != old_name:
        raise ValueError(f"Name '{new_name}' already exists.")

    if old_name in state.original_data:
        state.original_data[new_name] = state.original_data.pop(old_name)
    if old_name in state.modified_data:
        state.modified_data[new_name] = state.modified_data.pop(old_name)
    if old_name in state.params:
        state.params[new_name] = state.params.pop(old_name)
    if old_name in state.counts:
        state.counts[new_name] = state.counts.pop(old_name)

    entry["current_name"] = new_name


def delete_user_by_index(state, idx: int) -> None:
    """Delete entry + all associated store keys."""
    entry = state.entries[idx]
    name_candidates = [
        (entry.get("current_name") or "").strip(),
        (getattr(entry.get("rename_widget"), "value", "") or "").strip(),
    ]
    name_candidates = [n for n in name_candidates if n]

    for name in name_candidates:
        state.original_data.pop(name, None)
        state.modified_data.pop(name, None)
        state.params.pop(name, None)
        state.counts.pop(name, None)

    del state.entries[idx]


def add_user_record(
    state,
    template_key: str,
    formal_name: str,
    display_name: str,
    daily_data,
    rename_widget=None,
) -> Dict[str, Any]:
    """Add a new user entry and initialize state stores."""
    entry = {
        "template_key": template_key,
        "formal_name": formal_name,
        "rename_widget": rename_widget,
        "daily_data": np.asarray(daily_data, dtype=float).copy(),
        "current_name": display_name,
        "_rename_bound": False,
    }
    state.entries.append(entry)

    state.original_data[display_name] = {
        "template_key": template_key,
        "daily_data": entry["daily_data"].copy(),
    }
    state.modified_data[display_name] = entry["daily_data"].copy()
    state.params[display_name] = fresh_default_params(state.default_params)
    state.counts[display_name] = 1

    return entry


def emit_change(state, note: str = "", sync: bool = True) -> None:
    """Unified way to notify the UI that state has changed."""
    if sync:
        try:
            sync_state(state, verbose=False)
        except Exception:
            pass

    if hasattr(state, "bump") and callable(getattr(state, "bump")):
        state.bump(note)

    sig = getattr(state, "_state_signal", None)
    if sig is None:
        return

    try:
        v = getattr(state, "version", None)
        if v is None:
            sig.value = int(sig.value) + 1
            return

        # Ensure widget value actually changes (ipywidgets ignores no-op set)
        if int(sig.value) == int(v):
            sig.value = int(sig.value) + 1
        else:
            sig.value = int(v)
    except Exception:
        pass

# helpers/bootstrap.py

import ipywidgets as widgets

from helpers.state import AppState
from helpers.core import sync_state as core_sync_state, emit_change
from helpers.defaults import DEFAULT_PARAMS


def bootstrap_state(g, *, default_params=None, quiet=False):
    """
    Bootstraps state + state_signal + sync_state() + bump_state() in a safe-rerun way.

    Parameters
    ----------
    g : dict
        Pass globals() from the notebook.
    default_params : dict | None
        If None, uses helpers.defaults.DEFAULT_PARAMS
    quiet : bool
        If True, suppresses status prints.

    Returns
    -------
    state, sync_state, bump_state
    """
    dp = DEFAULT_PARAMS if default_params is None else default_params

    # --- state ---
    if "state" not in g or g["state"] is None:
        state = AppState(
            entries=[],
            original_data={},
            modified_data={},
            params={},
            counts={},
            default_params=dp,
            noise_seed=0,
            lock_noise=False,
        )
        g["state"] = state
        if not quiet:
            print("✅ Created NEW AppState.")
    else:
        state = g["state"]
        state.default_params = dp
        # Back-compat for older AppState objects
        if not hasattr(state, "noise_seed"):
            state.noise_seed = 0
        if not hasattr(state, "lock_noise"):
            state.lock_noise = False
        if not quiet:
            print("✅ Reusing EXISTING AppState (safe rerun).")

    # --- state_signal (optional UI trigger) ---
    if "state_signal" not in g or g["state_signal"] is None:
        g["state_signal"] = widgets.IntText(value=0, layout=widgets.Layout(display="none"))
    state_signal = g["state_signal"]

    # Attach for modules that want it
    state._state_signal = state_signal

    def bump_state(note="state changed", sync=True):
        # Back-compat wrapper: canonical signaling path
        emit_change(state, note=note, sync=sync)

    # --- sync_state ---
    def sync_state(verbose=False):
        return core_sync_state(state, verbose=verbose)

    if not quiet:
        print("✅ State ready: state + state_signal + sync_state() + bump_state().")

    return state, sync_state, bump_state

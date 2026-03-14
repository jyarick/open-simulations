"""
Analysis helpers: equilibria and their stability.
"""

import numpy as np
from .stability import classify_equilibrium, equilibrium_eigenvalues


def get_equilibria_with_stability(system, params):
    """
    Return list of (equilibrium_state, stability_label) for the given params.
    """
    equilibria = system.equilibria(params)
    result = []
    for y_eq in equilibria:
        y_eq = np.asarray(y_eq).ravel()
        stability = classify_equilibrium(system, y_eq, params)
        result.append((y_eq, stability))
    return result


def summarize_equilibria(system, params):
    """
    Return a list of dicts with keys: state, stability, eigenvalues (for 2D/3D).
    """
    pairs = get_equilibria_with_stability(system, params)
    out = []
    for y_eq, stability in pairs:
        entry = {"state": y_eq, "stability": stability}
        if system.dimension >= 2:
            entry["eigenvalues"] = equilibrium_eigenvalues(system, y_eq, params)
        out.append(entry)
    return out

"""
Schrödinger's Cat Lab — Quantum superposition and measurement demonstration.

A minimal two-state quantum system modeling the famous thought experiment.
"""

from quantum_cat.state import prepare_state, normalize_state, get_probabilities
from quantum_cat.measurement import measure_state
from quantum_cat.experiments import run_trials, count_outcomes
from quantum_cat.visuals import draw_cat_box, plot_probabilities, plot_histogram

__all__ = [
    "prepare_state",
    "normalize_state",
    "get_probabilities",
    "measure_state",
    "run_trials",
    "count_outcomes",
    "draw_cat_box",
    "plot_probabilities",
    "plot_histogram",
]

"""
Phase Space Explorer: modular dynamical systems teaching tool.

Use from a notebook or scripts:
    from phase_space_explorer import ALL_SYSTEMS, simulate, plot_system
    from phase_space_explorer.core import get_equilibria_with_stability
"""

from .systems import (
    DynamicalSystem,
    LOGISTIC,
    PREDATOR_PREY,
    DAMPED_OSCILLATOR,
    LORENZ,
    ALL_SYSTEMS,
)
from .core import simulate, get_equilibria_with_stability, summarize_equilibria
from .plotting import plot_system

__all__ = [
    "DynamicalSystem",
    "LOGISTIC",
    "PREDATOR_PREY",
    "DAMPED_OSCILLATOR",
    "LORENZ",
    "ALL_SYSTEMS",
    "simulate",
    "get_equilibria_with_stability",
    "summarize_equilibria",
    "plot_system",
]

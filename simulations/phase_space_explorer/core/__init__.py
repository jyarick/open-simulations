"""Core simulation, stability, and analysis."""

from .simulate import simulate
from .stability import (
    classify_equilibrium,
    classify_equilibrium_1d,
    classify_equilibrium_nd,
    equilibrium_eigenvalues,
)
from .jacobian import evaluate_jacobian, numerical_jacobian
from .analysis import get_equilibria_with_stability, summarize_equilibria

__all__ = [
    "simulate",
    "classify_equilibrium",
    "classify_equilibrium_1d",
    "classify_equilibrium_nd",
    "equilibrium_eigenvalues",
    "evaluate_jacobian",
    "numerical_jacobian",
    "get_equilibria_with_stability",
    "summarize_equilibria",
]

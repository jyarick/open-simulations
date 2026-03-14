"""
Base definition for dynamical systems.

Systems are plain objects with required attributes; no heavy class hierarchy.
Used by simulation, stability, and plotting without UI logic.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DynamicalSystem:
    """Minimal descriptor for a dynamical system dy/dt = f(t, y, params)."""

    name: str
    dimension: int
    rhs: Callable[[float, Any, dict], Any]  # (t, y, params) -> dy/dt
    equilibria: Callable[[dict], list]       # params -> list of state arrays
    jacobian: Callable[[Any, dict], Any]    # (y, params) -> Jacobian matrix
    parameter_info: dict                     # param name -> {default, min, max, step}
    initial_condition_info: dict            # state name -> {default, min, max}
    description: str
    interpretation: str

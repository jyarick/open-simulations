"""
Logistic growth: dx/dt = r*x*(1 - x/K).
State: [x]. Parameters: r, K.
"""

import numpy as np
from .base import DynamicalSystem


def _rhs(t, y, params):
    r, K = params["r"], params["K"]
    x = y[0]
    return np.array([r * x * (1 - x / K)])


def _equilibria(params):
    r, K = params["r"], params["K"]
    return [np.array([0.0]), np.array([K])]


def _jacobian(y, params):
    r, K = params["r"], params["K"]
    x = y[0]
    # d/dx [ r*x*(1 - x/K) ] = r*(1 - x/K) - r*x/K = r*(1 - 2*x/K)
    J = np.array([[r * (1 - 2 * x / K)]])
    return J


LOGISTIC = DynamicalSystem(
    name="Logistic growth",
    dimension=1,
    rhs=_rhs,
    equilibria=_equilibria,
    jacobian=_jacobian,
    parameter_info={
        "r": {"default": 1.0, "min": -2.0, "max": 3.0, "step": 0.05},
        "K": {"default": 10.0, "min": 0.5, "max": 20.0, "step": 0.5},
    },
    initial_condition_info={
        "x": {"default": 2.0, "min": 0.0, "max": 25.0},
    },
    description="dx/dt = r·x·(1 − x/K). Population growth with carrying capacity K.",
    interpretation="x: population; r: growth rate; K: carrying capacity.",
)

"""
Lotka–Volterra predator-prey: x' = a*x - b*x*y, y' = -c*y + d*x*y.
State: [x, y]. Parameters: a, b, c, d.
"""

import numpy as np
from .base import DynamicalSystem


def _rhs(t, y, params):
    a, b, c, d = params["a"], params["b"], params["c"], params["d"]
    x, y = y[0], y[1]
    return np.array([
        a * x - b * x * y,
        -c * y + d * x * y,
    ])


def _equilibria(params):
    a, b, c, d = params["a"], params["b"], params["c"], params["d"]
    return [
        np.array([0.0, 0.0]),
        np.array([c / d, a / b]),
    ]


def _jacobian(y, params):
    a, b, c, d = params["a"], params["b"], params["c"], params["d"]
    x, y = y[0], y[1]
    # d/dx (a*x - b*x*y) = a - b*y,  d/dy = -b*x
    # d/dx (-c*y + d*x*y) = d*y,      d/dy = -c + d*x
    J = np.array([
        [a - b * y, -b * x],
        [d * y, -c + d * x],
    ])
    return J


PREDATOR_PREY = DynamicalSystem(
    name="Lotka–Volterra predator-prey",
    dimension=2,
    rhs=_rhs,
    equilibria=_equilibria,
    jacobian=_jacobian,
    parameter_info={
        "a": {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1},
        "b": {"default": 0.5, "min": 0.1, "max": 2.0, "step": 0.05},
        "c": {"default": 0.75, "min": 0.1, "max": 2.0, "step": 0.05},
        "d": {"default": 0.25, "min": 0.05, "max": 1.0, "step": 0.05},
    },
    initial_condition_info={
        "x": {"default": 2.0, "min": 0.0, "max": 10.0},
        "y": {"default": 2.0, "min": 0.0, "max": 10.0},
    },
    description="ẋ = a·x − b·x·y, ẏ = −c·y + d·x·y. Prey x, predator y.",
    interpretation="a: prey growth; b: predation; c: predator death; d: predator growth from prey.",
)

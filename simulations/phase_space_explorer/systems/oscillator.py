"""
Damped harmonic oscillator: x'' + γ·x' + ω²·x = 0.
State space: y0 = x, y1 = v;  y0' = y1,  y1' = -γ·y1 - ω²·y0.
Parameters: gamma, omega.
"""

import numpy as np
from .base import DynamicalSystem


def _rhs(t, y, params):
    gamma, omega_sq = params["gamma"], params["omega"] ** 2
    y0, y1 = y[0], y[1]
    return np.array([
        y1,
        -gamma * y1 - omega_sq * y0,
    ])


def _equilibria(params):
    return [np.array([0.0, 0.0])]


def _jacobian(y, params):
    gamma, omega_sq = params["gamma"], params["omega"] ** 2
    # d/dy0: [y1] -> 0, [-γ*y1 - ω²*y0] -> -ω²
    # d/dy1: [y1] -> 1, [-γ*y1 - ω²*y0] -> -γ
    J = np.array([
        [0.0, 1.0],
        [-omega_sq, -gamma],
    ])
    return J


DAMPED_OSCILLATOR = DynamicalSystem(
    name="Damped harmonic oscillator",
    dimension=2,
    rhs=_rhs,
    equilibria=_equilibria,
    jacobian=_jacobian,
    parameter_info={
        "gamma": {"default": 0.5, "min": 0.0, "max": 3.0, "step": 0.05},
        "omega": {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.05},
    },
    initial_condition_info={
        "x": {"default": 1.0, "min": -5.0, "max": 5.0},
        "v": {"default": 0.0, "min": -5.0, "max": 5.0},
    },
    description="ẍ + γ·ẋ + ω²·x = 0. State: position x, velocity v.",
    interpretation="γ: damping; ω: natural frequency.",
)

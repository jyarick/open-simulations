"""
Lorenz system: ẋ = σ(y−x), ẏ = x(ρ−z)−y, ż = xy−βz.
State: [x, y, z]. Parameters: sigma, rho, beta.
"""

import numpy as np
from .base import DynamicalSystem


def _rhs(t, y, params):
    sigma, rho, beta = params["sigma"], params["rho"], params["beta"]
    x, y, z = y[0], y[1], y[2]
    return np.array([
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z,
    ])


def _equilibria(params):
    sigma, rho, beta = params["sigma"], params["rho"], params["beta"]
    result = [np.array([0.0, 0.0, 0.0])]
    if rho > 1:
        s = np.sqrt(beta * (rho - 1))
        result.append(np.array([s, s, rho - 1]))
        result.append(np.array([-s, -s, rho - 1]))
    return result


def _jacobian(y, params):
    sigma, rho, beta = params["sigma"], params["rho"], params["beta"]
    x, y, z = y[0], y[1], y[2]
    J = np.array([
        [-sigma, sigma, 0],
        [rho - z, -1, -x],
        [y, x, -beta],
    ])
    return J


LORENZ = DynamicalSystem(
    name="Lorenz system",
    dimension=3,
    rhs=_rhs,
    equilibria=_equilibria,
    jacobian=_jacobian,
    parameter_info={
        "sigma": {"default": 10.0, "min": 1.0, "max": 20.0, "step": 0.5},
        "rho": {"default": 28.0, "min": 1.0, "max": 50.0, "step": 0.5},
        "beta": {"default": 8.0 / 3.0, "min": 0.5, "max": 5.0, "step": 0.1},
    },
    initial_condition_info={
        "x": {"default": 1.0, "min": -20.0, "max": 20.0},
        "y": {"default": 1.0, "min": -20.0, "max": 20.0},
        "z": {"default": 1.0, "min": -10.0, "max": 50.0},
    },
    description="ẋ = σ(y−x), ẏ = x(ρ−z)−y, ż = xy−βz. Chaotic attractor for classic parameters.",
    interpretation="σ, ρ, β: dimensionless parameters; classic chaos at σ=10, ρ=28, β=8/3.",
)

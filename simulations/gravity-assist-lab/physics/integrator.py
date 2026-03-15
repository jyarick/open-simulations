"""
Numerical integrators for orbital mechanics.
Supports semi-implicit Euler and RK4.
"""

from typing import Callable

import numpy as np


def integrate_semi_implicit_euler(
    position: np.ndarray,
    velocity: np.ndarray,
    acceleration_fn: Callable[[np.ndarray], np.ndarray],
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Semi-implicit (symplectic) Euler:
    v_new = v + a * dt
    x_new = x + v_new * dt

    Better energy conservation than explicit Euler for orbital motion.
    """
    acc = acceleration_fn(position)
    velocity_new = velocity + acc * dt
    position_new = position + velocity_new * dt
    return position_new, velocity_new


def integrate_rk4(
    position: np.ndarray,
    velocity: np.ndarray,
    acceleration_fn: Callable[[np.ndarray], np.ndarray],
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Fourth-order Runge-Kutta for position and velocity.
    Treats as coupled system: d/dt [x, v] = [v, a(x)]
    """
    state = np.concatenate([position, velocity])

    def deriv(s: np.ndarray) -> np.ndarray:
        pos, vel = s[:2], s[2:]
        acc = acceleration_fn(pos)
        return np.concatenate([vel, acc])

    k1 = deriv(state)
    k2 = deriv(state + 0.5 * dt * k1)
    k3 = deriv(state + 0.5 * dt * k2)
    k4 = deriv(state + dt * k3)

    state_new = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    position_new = state_new[:2]
    velocity_new = state_new[2:]

    return position_new, velocity_new

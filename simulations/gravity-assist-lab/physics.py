"""
Gravity calculations, numerical integration, and vector math helpers.
Newtonian gravity: a = G * M * r_vec / |r|^3 (attraction toward body).
"""

from typing import Callable

import numpy as np

from config import G, MU_STAR


def compute_gravity_acceleration(
    position: np.ndarray,
    attracting_bodies: list,
    softening: float = 1e-6,
) -> np.ndarray:
    """
    Compute total gravitational acceleration at a position due to multiple bodies.
    a = G * M * r_vec / |r|^3  (r_vec points from position toward body)

    Args:
        position: [x, y] of the point experiencing gravity
        attracting_bodies: list of objects with .position and .mass
        softening: small value to avoid division by zero

    Returns:
        [ax, ay] total acceleration vector
    """
    total_acc = np.zeros(2)

    for body in attracting_bodies:
        r_vec = body.position - position
        r = np.linalg.norm(r_vec) + softening
        acc = G * body.mass * r_vec / (r**3)
        total_acc += acc

    return total_acc


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
    Good energy conservation for orbital motion.
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
    More accurate than Euler for complex trajectories.
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
    return state_new[:2], state_new[2:]


def speed(v: np.ndarray) -> float:
    """Magnitude of velocity vector."""
    return np.linalg.norm(v)


def kinetic_energy(mass: float, velocity: np.ndarray) -> float:
    """Kinetic energy: 0.5 * m * v^2."""
    return 0.5 * mass * np.dot(velocity, velocity)


def heliocentric_specific_energy(
    position: np.ndarray,
    velocity: np.ndarray,
    star_position: np.ndarray,
) -> float:
    """
    Heliocentric specific orbital energy: epsilon = v^2/2 - mu/r.
    - epsilon < 0: bound to star (elliptical orbit)
    - epsilon = 0: parabolic (escape)
    - epsilon > 0: hyperbolic (escape trajectory)
    """
    r_vec = position - star_position
    r = np.linalg.norm(r_vec) + 1e-10
    v_sq = np.dot(velocity, velocity)
    return 0.5 * v_sq - MU_STAR / r

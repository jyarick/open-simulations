"""
Newtonian gravity calculations.
Acceleration: a = -G*M / r^3 * r_vector
where r_vector points from spacecraft to the attracting body.
"""

import numpy as np

from config.constants import G


def compute_acceleration(
    position: np.ndarray,
    attracting_bodies: list,
    softening: float = 1e-6,
) -> np.ndarray:
    """
    Compute total gravitational acceleration at a given position
    due to multiple attracting bodies.

    Args:
        position: [x, y] of the point experiencing gravity
        attracting_bodies: list of Body objects with .position and .mass
        softening: small value to avoid division by zero (numerical stability)

    Returns:
        [ax, ay] total acceleration vector
    """
    total_acc = np.zeros(2)

    for body in attracting_bodies:
        r_vec = body.position - position  # vector from position to body
        r = np.linalg.norm(r_vec) + softening

        # a = G*M / r^3 * r_vec (r_vec points toward body, so we add)
        # Actually: F = G*M*m/r^2 toward body, so a = G*M/r^2 * r_hat
        # r_hat = r_vec / r, so a = G*M * r_vec / r^3
        acc = G * body.mass * r_vec / (r**3)
        total_acc += acc

    return total_acc

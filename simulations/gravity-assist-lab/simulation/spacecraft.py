"""
Spacecraft model for gravity assist simulation.
Tracks position, velocity, and trajectory history.
"""

import numpy as np

from physics.bodies import Body
from physics.gravity import compute_acceleration
from physics.integrator import integrate_rk4


class Spacecraft(Body):
    """
    Spacecraft that experiences gravity from star and planet.
    Integrates motion using RK4.
    """

    def __init__(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        mass: float = 1000.0,
        name: str = "spacecraft",
    ):
        super().__init__(position, velocity, mass, name)
        self._attracting_bodies: list = []
        self._initial_speed: float = self.speed
        self._incoming_speed: float | None = None  # Set when approaching planet
        self._outgoing_speed: float | None = None  # Set when leaving

    def set_attractors(self, bodies: list) -> None:
        """Set the list of bodies that exert gravity on the spacecraft."""
        self._attracting_bodies = bodies

    def acceleration_at(self, position: np.ndarray) -> np.ndarray:
        """Compute gravitational acceleration at a given position."""
        return compute_acceleration(position, self._attracting_bodies)

    def step(self, dt: float) -> None:
        """Advance spacecraft state by one time step using RK4."""
        acc_fn = lambda pos: self.acceleration_at(pos)
        self.position, self.velocity = integrate_rk4(
            self.position, self.velocity, acc_fn, dt
        )

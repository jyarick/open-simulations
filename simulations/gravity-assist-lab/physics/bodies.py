"""
Body definitions for the gravity assist simulation.
Represents celestial objects: star, planet, spacecraft.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class Body:
    """Base body with position, velocity, and mass."""

    position: np.ndarray  # [x, y] in 2D
    velocity: np.ndarray  # [vx, vy]
    mass: float
    name: str = "body"

    @property
    def x(self) -> float:
        return self.position[0]

    @property
    def y(self) -> float:
        return self.position[1]

    @property
    def speed(self) -> float:
        """Magnitude of velocity."""
        return np.linalg.norm(self.velocity)

    def kinetic_energy(self) -> float:
        """Kinetic energy: 0.5 * m * v^2."""
        return 0.5 * self.mass * self.speed**2


class FixedBody(Body):
    """Body fixed at a position (e.g., star at center)."""

    def __init__(self, position: np.ndarray, mass: float, name: str = "star"):
        super().__init__(position, np.zeros(2), mass, name)


class OrbitingBody(Body):
    """Body in circular orbit around a center (e.g., planet around star)."""

    def __init__(
        self,
        orbit_center: np.ndarray,
        orbit_radius: float,
        orbit_speed: float,
        mass: float,
        phase: float = 0.0,
        name: str = "planet",
    ):
        """
        orbit_center: [x, y] of the body being orbited
        orbit_radius: distance from center
        orbit_speed: angular velocity (rad/s), positive = counterclockwise
        phase: initial angle (radians) from positive x-axis
        """
        angle = phase
        position = orbit_center + orbit_radius * np.array([np.cos(angle), np.sin(angle)])
        # Tangential velocity: v = omega * r, perpendicular to radius
        velocity = orbit_speed * orbit_radius * np.array(
            [-np.sin(angle), np.cos(angle)]
        )
        super().__init__(position, velocity, mass, name)
        self._orbit_center = orbit_center
        self._orbit_radius = orbit_radius
        self._orbit_speed = orbit_speed
        self._phase = phase

    def update_orbit(self, dt: float) -> None:
        """Advance position along circular orbit."""
        self._phase += self._orbit_speed * dt
        angle = self._phase
        self.position = self._orbit_center + self._orbit_radius * np.array(
            [np.cos(angle), np.sin(angle)]
        )
        self.velocity = self._orbit_speed * self._orbit_radius * np.array(
            [-np.sin(angle), np.cos(angle)]
        )

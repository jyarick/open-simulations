"""
Entity classes: Star, Planet, Spacecraft.
Star is fixed; Planet orbits; Spacecraft is affected by gravity.
"""

import numpy as np

from physics import compute_gravity_acceleration, integrate_rk4


class Star:
    """Fixed star at center. Large mass, does not move."""

    def __init__(self, position: np.ndarray, mass: float):
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(2)
        self.mass = mass
        self.name = "star"

    @property
    def speed(self) -> float:
        return 0.0


class Planet:
    """
    Planet in circular orbit around the star.
    Orbital velocity: v = omega * r (tangential).
    """

    def __init__(
        self,
        orbit_center: np.ndarray,
        orbit_radius: float,
        orbit_speed: float,
        mass: float,
        phase: float = 0.0,
        name: str = "planet",
        radius_visual: float = 0.08,
        color: tuple = (68, 136, 255),
        ring_color: tuple = (68, 136, 255),
    ):
        self._orbit_center = np.array(orbit_center)
        self._orbit_radius = orbit_radius
        self._orbit_speed = orbit_speed
        self._phase = phase
        self.mass = mass
        self.name = name
        self.radius_visual = radius_visual
        self.color = color
        self.ring_color = ring_color
        self._planet_paused = False
        self._update_position_and_velocity()

    def _update_position_and_velocity(self) -> None:
        angle = self._phase
        self.position = self._orbit_center + self._orbit_radius * np.array(
            [np.cos(angle), np.sin(angle)]
        )
        self.velocity = self._orbit_speed * self._orbit_radius * np.array(
            [-np.sin(angle), np.cos(angle)]
        )

    def update_orbit(self, dt: float) -> None:
        """Advance along circular orbit (unless paused)."""
        if not self._planet_paused:
            self._phase += self._orbit_speed * dt
            self._update_position_and_velocity()

    def toggle_pause(self) -> bool:
        """Toggle planet motion pause. Returns new pause state."""
        self._planet_paused = not self._planet_paused
        return self._planet_paused

    @property
    def speed(self) -> float:
        return np.linalg.norm(self.velocity)


class Spacecraft:
    """
    Spacecraft affected by gravity from star and all planets.
    Integrates motion using RK4.
    """

    def __init__(self, position: np.ndarray, velocity: np.ndarray, mass: float = 1.0):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = mass
        self.name = "spacecraft"
        self._attractors: list = []
        self._initial_speed = np.linalg.norm(velocity)

    def set_attractors(self, bodies: list) -> None:
        """Set bodies that exert gravity on the spacecraft."""
        self._attractors = bodies

    def acceleration_at(self, position: np.ndarray) -> np.ndarray:
        return compute_gravity_acceleration(position, self._attractors)

    def step(self, dt: float) -> None:
        """Advance one timestep using RK4."""
        acc_fn = lambda pos: self.acceleration_at(pos)
        self.position, self.velocity = integrate_rk4(
            self.position, self.velocity, acc_fn, dt
        )

    @property
    def speed(self) -> float:
        return np.linalg.norm(self.velocity)

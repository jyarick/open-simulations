"""
Universe: manages star, planet, spacecraft, and simulation state.
"""

import numpy as np

from physics.bodies import FixedBody, OrbitingBody
from simulation.spacecraft import Spacecraft


class Universe:
    """
    Contains star (fixed), planet (orbiting), and spacecraft.
    Coordinates simulation updates.
    """

    def __init__(
        self,
        star_mass: float,
        planet_mass: float,
        planet_orbit_radius: float,
        planet_orbit_speed: float,
        spacecraft_position: np.ndarray,
        spacecraft_velocity: np.ndarray,
        dt: float,
    ):
        center = np.zeros(2)
        self.star = FixedBody(center, star_mass, "star")
        self.planet = OrbitingBody(
            orbit_center=center,
            orbit_radius=planet_orbit_radius,
            orbit_speed=planet_orbit_speed,
            mass=planet_mass,
            phase=0.0,
            name="planet",
        )
        self.spacecraft = Spacecraft(
            position=spacecraft_position.copy(),
            velocity=spacecraft_velocity.copy(),
        )
        self.spacecraft.set_attractors([self.star, self.planet])
        self.dt = dt
        self.time = 0.0

    def step(self) -> None:
        """One simulation step: update planet orbit, then spacecraft."""
        self.planet.update_orbit(self.dt)
        self.spacecraft.step(self.dt)
        self.time += self.dt

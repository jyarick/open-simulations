"""
Simulation state and update loop.
Manages star, planets (list), spacecraft, trail, presets, and encounter tracking.
"""

import math
import numpy as np

from config import (
    STAR_MASS,
    STAR_POSITION,
    PLANET_DEFS,
    PRESETS,
    PRESET_INDEX,
    SPACECRAFT_MASS,
    SIMULATION_DT,
    ENCOUNTER_RADIUS,
    TRAIL_LENGTH,
    TIME_SCALE_DEFAULT,
    VIEW_SCALE,
)
from entities import Star, Planet, Spacecraft
from physics import heliocentric_specific_energy
from utils import TrailManager


def orbit_speed_for_radius(orbit_radius: float) -> float:
    """Angular speed for circular orbit: omega = sqrt(G*M_star/r^3) = 1/sqrt(r^3)."""
    return 1.0 / np.sqrt(orbit_radius**3)


def make_velocity(speed: float, angle_deg: float) -> np.ndarray:
    """Compute velocity vector from speed and angle (degrees from +x)."""
    angle_rad = math.radians(angle_deg)
    return speed * np.array([np.cos(angle_rad), np.sin(angle_rad)])


def build_planets_from_preset(preset: dict, center: np.ndarray) -> list[Planet]:
    """Create Planet instances for the preset's planet list."""
    planet_names = preset["planets"]
    phase_overrides = preset.get("planet_phases", {})
    name_to_def = {d["name"]: d for d in PLANET_DEFS}
    planets = []
    for name in planet_names:
        if name not in name_to_def:
            continue
        d = name_to_def[name]
        phase = phase_overrides.get(name, d["phase"])
        omega = orbit_speed_for_radius(d["orbit_radius"])
        p = Planet(
            orbit_center=center,
            orbit_radius=d["orbit_radius"],
            orbit_speed=omega,
            mass=d["mass"],
            phase=phase,
            name=d["name"],
            radius_visual=d["radius_visual"],
            color=d["color"],
            ring_color=d["ring_color"],
        )
        planets.append(p)
    return planets


def get_spacecraft_initial(preset: dict) -> tuple[np.ndarray, np.ndarray]:
    """Get (position, velocity) from preset spacecraft config."""
    sc = preset["spacecraft"]
    pos = np.array([sc["x"], sc["y"]])
    vel = make_velocity(sc["speed"], sc["angle_deg"])
    return pos, vel


class Simulation:
    """
    Holds simulation state: star, planets, spacecraft, trail, preset.
    Spacecraft gravity = star + all planets.
    """

    def __init__(self):
        self.preset_index = PRESET_INDEX
        self.preset = PRESETS[self.preset_index]
        self._override_speed: float | None = None
        self._override_angle: float | None = None
        self._create_entities()
        self.trail = TrailManager(max_length=TRAIL_LENGTH)
        self.dt = SIMULATION_DT
        self.time = 0.0
        self.paused = False
        self.time_scale = TIME_SCALE_DEFAULT
        self._initial_speed = self.spacecraft.speed
        self._max_speed = self.spacecraft.speed
        self._incoming_speed: float | None = None
        self._outgoing_speed: float | None = None
        self._in_encounter = False
        self._had_encounter = False
        self._planets_paused = False
        self.view_scale = VIEW_SCALE

    def _get_spacecraft_initial(self) -> tuple[np.ndarray, np.ndarray]:
        """Get (position, velocity) from preset, with optional overrides."""
        sc = self.preset["spacecraft"]
        pos = np.array([sc["x"], sc["y"]])
        speed = self._override_speed if self._override_speed is not None else sc["speed"]
        angle = self._override_angle if self._override_angle is not None else sc["angle_deg"]
        vel = make_velocity(speed, angle)
        return pos, vel

    def _create_entities(self) -> None:
        center = np.array(STAR_POSITION)
        self.star = Star(center, STAR_MASS)
        self.planets = build_planets_from_preset(self.preset, center)
        pos, vel = self._get_spacecraft_initial()
        self.spacecraft = Spacecraft(pos, vel, SPACECRAFT_MASS)
        attractors = [self.star] + self.planets
        self.spacecraft.set_attractors(attractors)

    def _nearest_planet_distance(self) -> float:
        """Distance to nearest planet."""
        if not self.planets:
            return float("inf")
        return min(
            np.linalg.norm(self.spacecraft.position - p.position)
            for p in self.planets
        )

    def step(self) -> None:
        """Advance simulation by one step."""
        if self.paused:
            return

        effective_dt = self.dt * self.time_scale
        dist = self._nearest_planet_distance()

        if dist < ENCOUNTER_RADIUS:
            if not self._in_encounter:
                self._incoming_speed = self.spacecraft.speed
            self._in_encounter = True
            self._had_encounter = True
        else:
            if self._in_encounter:
                self._outgoing_speed = self.spacecraft.speed
            self._in_encounter = False

        if not self._planets_paused:
            for planet in self.planets:
                planet.update_orbit(effective_dt)
        self.spacecraft.step(effective_dt)
        self.time += effective_dt

        self._max_speed = max(self._max_speed, self.spacecraft.speed)
        self.trail.add(self.spacecraft.position.copy(), self.spacecraft.speed)

    def reset(self) -> None:
        """Reset simulation to initial state of current preset."""
        self._create_entities()
        self.trail.clear()
        self.time = 0.0
        self._initial_speed = self.spacecraft.speed
        self._max_speed = self.spacecraft.speed
        self._incoming_speed = None
        self._outgoing_speed = None
        self._in_encounter = False
        self._had_encounter = False

    def load_preset(self, index: int) -> None:
        """Load preset by index and reset."""
        self.preset_index = index % len(PRESETS)
        self.preset = PRESETS[self.preset_index]
        self._override_speed = None
        self._override_angle = None
        self.reset()

    def next_preset(self) -> None:
        """Cycle to next preset."""
        self.load_preset(self.preset_index + 1)

    def prev_preset(self) -> None:
        """Cycle to previous preset."""
        self.load_preset(self.preset_index - 1)

    def new_spacecraft(self) -> None:
        """Launch new spacecraft with same planet system. Uses override speed/angle if set."""
        pos, vel = self._get_spacecraft_initial()
        self.spacecraft = Spacecraft(pos, vel, SPACECRAFT_MASS)
        self.spacecraft.set_attractors([self.star] + self.planets)
        self.trail.clear()
        self._initial_speed = self.spacecraft.speed
        self._max_speed = self.spacecraft.speed
        self._incoming_speed = None
        self._outgoing_speed = None
        self._in_encounter = False
        self._had_encounter = False

    def set_trail_length(self, length: int) -> None:
        """Change trail length (keeps recent points)."""
        self.trail.set_max_length(length)

    def set_initial_override(self, speed: float | None = None, angle: float | None = None) -> None:
        """Set override for next new spacecraft / reset. None = use preset."""
        if speed is not None:
            self._override_speed = speed
        if angle is not None:
            self._override_angle = angle

    def toggle_planet_pause(self) -> bool:
        """Toggle all planets' motion. Returns new pause state."""
        self._planets_paused = not self._planets_paused
        return self._planets_paused

    def heliocentric_energy(self) -> float:
        """Current heliocentric specific orbital energy: epsilon = v^2/2 - mu/r."""
        return heliocentric_specific_energy(
            self.spacecraft.position,
            self.spacecraft.velocity,
            self.star.position,
        )

    def is_escape_trajectory(self) -> bool:
        """True if epsilon > 0 (escape from star)."""
        return self.heliocentric_energy() > 0

    @property
    def initial_speed(self) -> float:
        return self._initial_speed

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @property
    def incoming_speed(self) -> float | None:
        return self._incoming_speed

    @property
    def outgoing_speed(self) -> float | None:
        return self._outgoing_speed

    @property
    def had_encounter(self) -> bool:
        return self._had_encounter

    def energy_change(self) -> float | None:
        """Estimated energy change (KE_out - KE_in) if encounter occurred."""
        if self._incoming_speed is None or self._outgoing_speed is None:
            return None
        ke_in = 0.5 * SPACECRAFT_MASS * self._incoming_speed**2
        ke_out = 0.5 * SPACECRAFT_MASS * self._outgoing_speed**2
        return ke_out - ke_in

"""
Simulation phases and global simulation state.
Conceptual backbone of the project.
"""

# Phase constants
STABLE = "stable"
COLLAPSE = "collapse"
BOUNCE = "bounce"
EXPLOSION = "explosion"
REMNANT = "remnant"
DONE = "done"

PHASES = (STABLE, COLLAPSE, BOUNCE, EXPLOSION, REMNANT, DONE)


class SimState:
    """
    Global simulation state. Tracks phase, timing, and high-level flags.
    Does not own drawing objects; the Simulation (in engine) does.
    """

    def __init__(self, star_mass: float = 15.0):
        self.phase = STABLE
        self.phase_time = 0.0
        self.total_time = 0.0
        self.star_mass = star_mass
        self.remnant_type: str | None = None  # "neutron_star" | "black_hole"
        self.star_radius = 0.0  # current display radius (set by star)
        self.flash_active = False
        self.shockwave_active = False
        self.particles_spawned = False

    def reset_phase_timer(self) -> None:
        """Call when transitioning to a new phase."""
        self.phase_time = 0.0

    def advance(self, dt: float) -> None:
        """Advance time."""
        self.phase_time += dt
        self.total_time += dt

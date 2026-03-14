"""
Orchestrates the simulation loop: advance time, update objects, phase transitions, redraw.
"""
from turtle import Turtle, Screen

import config
from sim_state import (
    SimState,
    STABLE,
    COLLAPSE,
    BOUNCE,
    EXPLOSION,
    REMNANT,
    DONE,
)
from background import Background
from star import Star
from shockwave import Shockwave
from particles import ParticleSystem
from remnant import Remnant
from effects import Effects


class Simulation:
    """
    Owns the entire world. Coordinates updates and drawing;
    does not contain drawing logic itself.
    """

    def __init__(self, screen: Screen) -> None:
        self.screen = screen
        self.state = SimState(star_mass=15.0)
        self.dt = config.FRAME_DELAY_MS / 1000.0

        self.background = Background()
        self.star = Star()
        self.star.mass = self.state.star_mass
        self.star.radius = config.STAR_INITIAL_RADIUS
        self.star.base_radius = config.STAR_INITIAL_RADIUS
        self.shockwave = Shockwave()
        self.particles = ParticleSystem()
        self.remnant = Remnant()
        self.effects = Effects()

        self._pens: dict[str, Turtle] = {}
        self._create_pens()

    def _create_pens(self) -> None:
        """Create layered turtles for rendering."""
        for name in ("bg", "star", "shock", "particle", "remnant", "fx"):
            t = Turtle()
            t.hideturtle()
            t.speed(0)
            t.penup()
            self._pens[name] = t

    def transition_to(self, new_phase: str) -> None:
        """Handle phase transition."""
        self.state.phase = new_phase
        self.state.reset_phase_timer()

        if new_phase == COLLAPSE:
            self.star.start_collapse()
        elif new_phase == BOUNCE:
            self.effects.trigger_bounce_flash()
            self.state.flash_active = True
            self.shockwave.trigger()
            self.state.shockwave_active = True
            self.particles.spawn_explosion(self.star.radius)
            self.state.particles_spawned = True
            self.determine_remnant_type()
        elif new_phase == REMNANT:
            self.remnant.type = self.state.remnant_type
            self.remnant.active = True

    def determine_remnant_type(self) -> None:
        """Set remnant type from progenitor mass."""
        if self.state.star_mass < config.BLACK_HOLE_MASS_THRESHOLD:
            self.state.remnant_type = "neutron_star"
        else:
            self.state.remnant_type = "black_hole"

    def update(self) -> None:
        """Advance simulation by one frame."""
        dt = self.dt
        state = self.state

        # Phase transition logic
        if state.phase == STABLE:
            if state.phase_time >= config.STABLE_DURATION:
                self.transition_to(COLLAPSE)
        elif state.phase == COLLAPSE:
            if state.phase_time >= config.COLLAPSE_DURATION:
                self.transition_to(BOUNCE)
        elif state.phase == BOUNCE:
            if state.phase_time >= config.BOUNCE_DURATION:
                self.transition_to(EXPLOSION)
        elif state.phase == EXPLOSION:
            if state.phase_time >= config.EXPLOSION_DURATION or not self.particles.particles:
                self.transition_to(REMNANT)
        elif state.phase == REMNANT:
            pass  # Run indefinitely
        # DONE not used in basic loop

        state.advance(dt)

        self.star.update(dt, state)
        self.shockwave.update(dt, state)
        self.particles.update(dt, state)
        self.remnant.update(dt, state)
        self.effects.update(dt, state)

    def draw(self) -> None:
        """Draw all layers in order."""
        p = self._pens
        for pen in p.values():
            pen.clear()
        self.background.draw(p["bg"])
        self.star.draw(p["star"])
        self.shockwave.draw(p["shock"])
        self.particles.draw(p["particle"])
        self.remnant.draw(p["remnant"])
        self.effects.draw(p["fx"])
        self.screen.update()

    def tick(self) -> None:
        """One frame: update then draw."""
        self.update()
        self.draw()

    def run(self) -> None:
        """Start the main loop using ontimer."""
        self.screen.tracer(0, 0)

        def step() -> None:
            self.tick()
            self.screen.ontimer(step, config.FRAME_DELAY_MS)

        step()

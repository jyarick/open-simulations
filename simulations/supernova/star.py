"""
Star: layered glowing star, pulsation in stable phase, collapse, bounce brighten.
"""
from turtle import Turtle

import config
from sim_state import SimState, STABLE, COLLAPSE, BOUNCE, EXPLOSION, REMNANT
from utils import ease_in_out_quad, lerp


class Star:
    """Handles the star before and during collapse."""

    def __init__(self) -> None:
        self.mass = 15.0
        self.radius = config.STAR_INITIAL_RADIUS
        self.base_radius = config.STAR_INITIAL_RADIUS
        self.brightness = 1.0
        self.pulse_phase = 0.0
        self.collapse_progress = 0.0  # 0 = not started, 1 = fully collapsed

    def update(self, dt: float, state: SimState) -> None:
        state.star_radius = self.radius

        if state.phase == STABLE:
            self.pulse_phase += dt * config.STAR_PULSE_SPEED
            # Pulsation: radius varies slightly
            pulse = 1.0 + config.STAR_PULSE_AMPLITUDE * (
                1.0 if (int(self.pulse_phase) % 2 == 0) else -1.0
            )
            self.radius = self.base_radius * pulse
            self.brightness = 1.0

        elif state.phase == COLLAPSE:
            t = min(1.0, state.phase_time / config.COLLAPSE_DURATION)
            self.collapse_progress = ease_in_out_quad(t)
            # R(t) = R0 * (1 - f(t)), with f(1) = 1 - STAR_COLLAPSE_FINAL_FRACTION
            self.radius = self.base_radius * (
                1.0 - self.collapse_progress * (1.0 - config.STAR_COLLAPSE_FINAL_FRACTION)
            )
            self.brightness = lerp(1.0, 0.7, t)
            self.pulse_phase += dt * 3.0

        elif state.phase == BOUNCE:
            self.brightness = 1.0
            self.radius = self.base_radius * config.STAR_COLLAPSE_FINAL_FRACTION

        elif state.phase in (EXPLOSION, REMNANT):
            # Dim or vanish
            self.brightness = max(0.0, 1.0 - state.phase_time / 0.8)
            self.radius *= 0.97

    def draw(self, pen: Turtle) -> None:
        if self.brightness <= 0.001:
            return

        cx, cy = config.CENTER_X, config.CENTER_Y
        pen.penup()
        pen.hideturtle()

        # Layered glow (outer to inner, dimmer to brighter)
        for i in range(config.STAR_GLOW_LAYERS, 0, -1):
            layer_radius = self.radius * (config.STAR_GLOW_SPREAD ** (i / config.STAR_GLOW_LAYERS))
            pen.goto(cx, cy - layer_radius)
            # Outer layers use a dimmer shade (no alpha in turtle)
            pen.fillcolor(config.STAR_COLLAPSE_COLOR)
            pen.pencolor(config.STAR_COLLAPSE_COLOR)
            pen.pensize(1)
            pen.pendown()
            pen.begin_fill()
            pen.circle(layer_radius)
            pen.end_fill()
            pen.penup()

        # Core
        pen.goto(cx, cy - self.radius)
        if self.collapse_progress > 0.5:
            pen.fillcolor(config.STAR_COLLAPSE_COLOR)
            pen.pencolor(config.STAR_COLLAPSE_COLOR)
        else:
            pen.fillcolor(config.STAR_STABLE_COLOR)
            pen.pencolor(config.STAR_STABLE_COLOR)
        pen.pensize(1)
        pen.pendown()
        pen.begin_fill()
        pen.circle(self.radius)
        pen.end_fill()
        pen.penup()

    def start_collapse(self) -> None:
        """Called when transitioning to collapse."""
        self.collapse_progress = 0.0
        self.base_radius = self.radius

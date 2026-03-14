"""
Outward-moving shock front. Expands and fades over time.
"""
from turtle import Turtle

import config
from sim_state import SimState


class Shockwave:
    """Handles the expanding shock ring."""

    def __init__(self) -> None:
        self.radius = config.SHOCK_INITIAL_RADIUS
        self.speed = config.SHOCK_EXPANSION_SPEED
        self.line_width = config.SHOCK_LINE_WIDTH
        self.opacity_factor = 1.0
        self.active = False

    def update(self, dt: float, state: SimState | None = None) -> None:
        if not self.active:
            return
        self.radius += self.speed * dt
        self.opacity_factor *= config.SHOCK_FADE_RATE ** dt
        if self.radius >= config.SHOCK_MAX_RADIUS or self.opacity_factor <= 0.02:
            self.active = False

    def draw(self, pen: Turtle) -> None:
        if not self.active or self.opacity_factor <= 0:
            return
        pen.penup()
        pen.hideturtle()
        pen.goto(config.CENTER_X, config.CENTER_Y - self.radius)
        pen.pendown()
        pen.pensize(max(1, int(self.line_width * self.opacity_factor)))
        pen.pencolor(config.SHOCK_COLOR)
        pen.circle(self.radius)
        pen.penup()

    def trigger(self) -> None:
        """Start the shockwave (call at bounce)."""
        self.active = True
        self.radius = config.SHOCK_INITIAL_RADIUS
        self.opacity_factor = 1.0

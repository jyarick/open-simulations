"""
Compact remnant: neutron star or black hole. Type from progenitor mass.
"""
import math
from turtle import Turtle

import config
from sim_state import SimState, REMNANT
from utils import polar_to_cartesian


class Remnant:
    """Handles the compact remnant (neutron star or black hole)."""

    def __init__(self) -> None:
        self.type: str | None = None  # "neutron_star" | "black_hole"
        self.mass = 0.0
        self.radius = 0.0
        self.spin_angle = 0.0
        self.beam_angle = 0.0
        self.active = False
        self.fade_in = 0.0  # 0..1 for REMNANT phase

    def update(self, dt: float, state: SimState) -> None:
        if not state.remnant_type or state.phase != REMNANT:
            return
        self.active = True
        self.type = state.remnant_type
        self.fade_in = min(1.0, state.phase_time / config.REMNANT_FADE_IN)
        self.spin_angle += dt * 2.0
        self.beam_angle += dt * config.PULSAR_BEAM_SPEED
        if self.type == "neutron_star":
            self.radius = config.NEUTRON_STAR_RADIUS
        else:
            self.radius = config.BLACK_HOLE_RADIUS

    def draw(self, pen: Turtle) -> None:
        if not self.active or self.type is None:
            return
        pen.penup()
        pen.hideturtle()
        cx, cy = config.CENTER_X, config.CENTER_Y

        if self.type == "neutron_star":
            # Glow
            pen.goto(cx, cy - self.radius * 3)
            pen.fillcolor(config.NEUTRON_STAR_GLOW)
            pen.pencolor(config.NEUTRON_STAR_GLOW)
            pen.pendown()
            pen.begin_fill()
            pen.circle(self.radius * 3)
            pen.end_fill()
            pen.penup()
            # Core
            pen.goto(cx, cy - self.radius)
            pen.fillcolor(config.NEUTRON_STAR_COLOR)
            pen.pencolor(config.NEUTRON_STAR_COLOR)
            pen.pendown()
            pen.begin_fill()
            pen.circle(self.radius)
            pen.end_fill()
            pen.penup()
            # Pulsar beams
            for i in range(2):
                angle = self.beam_angle + i * math.pi
                x1, y1 = polar_to_cartesian(config.PULSAR_BEAM_LENGTH, angle)
                pen.goto(cx, cy)
                pen.pendown()
                pen.pencolor(config.NEUTRON_STAR_GLOW)
                pen.pensize(2)
                pen.goto(cx + x1, cy + y1)
                pen.penup()

        else:
            # Black hole: faint ring then dark disk (so ring shows around it)
            pen.goto(cx, cy - config.ACCRETION_DISK_OUTER)
            pen.fillcolor(config.BLACK_HOLE_RING_COLOR)
            pen.pencolor(config.BLACK_HOLE_RING_COLOR)
            pen.pendown()
            pen.begin_fill()
            pen.circle(config.ACCRETION_DISK_OUTER)
            pen.end_fill()
            pen.penup()
            pen.goto(cx, cy - self.radius)
            pen.fillcolor(config.BLACK_HOLE_COLOR)
            pen.pencolor(config.BLACK_HOLE_COLOR)
            pen.pendown()
            pen.begin_fill()
            pen.circle(self.radius)
            pen.end_fill()
            pen.penup()

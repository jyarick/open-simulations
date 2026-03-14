"""
Short-lived cinematic effects: bounce flash, halo pulses, etc.
"""
from turtle import Turtle

import config
from sim_state import SimState, BOUNCE
from utils import ease_out_quad


class Effects:
    """Handles bounce flash and other visual effects."""

    def __init__(self) -> None:
        self.flash_time = 0.0
        self.flash_active = False

    def trigger_bounce_flash(self) -> None:
        self.flash_active = True
        self.flash_time = 0.0

    def update(self, dt: float, state: SimState) -> None:
        if self.flash_active:
            self.flash_time += dt
            if self.flash_time >= config.BOUNCE_FLASH_DURATION:
                self.flash_active = False

    def draw(self, pen: Turtle) -> None:
        if not self.flash_active:
            return
        t = min(1.0, self.flash_time / config.BOUNCE_FLASH_DURATION)
        # Fade out
        strength = 1.0 - ease_out_quad(t)
        if strength <= 0:
            return
        pen.penup()
        pen.hideturtle()
        pen.goto(-config.SCREEN_WIDTH // 2, -config.SCREEN_HEIGHT // 2)
        pen.fillcolor(config.BOUNCE_FLASH_COLOR)
        pen.pencolor(config.BOUNCE_FLASH_COLOR)
        pen.pendown()
        pen.begin_fill()
        for _ in range(4):
            pen.forward(config.SCREEN_WIDTH)
            pen.left(90)
        pen.end_fill()
        pen.penup()

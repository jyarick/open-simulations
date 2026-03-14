"""
Background layer: starfield and faint nebula haze.
"""
import random
from turtle import Turtle

import config
from utils import polar_to_cartesian


class Background:
    """Handles the visual environment: starfield and nebula."""

    def __init__(self) -> None:
        self._stars: list[tuple[float, float, float, str]] = []  # x, y, size, color
        self._initialized = False

    def _generate_starfield(self) -> None:
        """Generate distant stars once."""
        half_w = config.SCREEN_WIDTH // 2
        half_h = config.SCREEN_HEIGHT // 2
        for _ in range(config.STARFIELD_COUNT):
            x = random.uniform(-half_w, half_w)
            y = random.uniform(-half_h, half_h)
            size = random.choice([1, 1, 1, 2])
            color = random.choice(config.STARFIELD_COLORS)
            self._stars.append((x, y, size, color))
        self._initialized = True

    def draw(self, pen: Turtle) -> None:
        if not self._initialized:
            self._generate_starfield()

        pen.clear()
        pen.penup()
        pen.hideturtle()

        # Faint nebula: a few soft blobs (we can't do alpha; use sparse dots)
        if config.NEBULA_HAZE_STRENGTH > 0:
            for _ in range(40):
                x = random.uniform(-350, 350)
                y = random.uniform(-250, 250)
                pen.goto(config.CENTER_X + x, config.CENTER_Y + y)
                pen.dot(8, config.NEBULA_COLOR)

        for x, y, size, color in self._stars:
            pen.goto(config.CENTER_X + x, config.CENTER_Y + y)
            pen.dot(size, color)

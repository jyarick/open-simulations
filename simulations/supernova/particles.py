"""
Ejecta and debris particles. Spawn during explosion, update motion, draw trails.
"""
import math
import random
from turtle import Turtle

import config
from sim_state import SimState, EXPLOSION, REMNANT
from utils import polar_to_cartesian, random_in_disk


class Particle:
    """Single ejecta particle with trail."""

    def __init__(
        self,
        x: float, y: float,
        vx: float, vy: float,
        color: str,
        size: float,
        lifetime: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.age = 0.0
        self.lifetime = lifetime
        self.trail: list[tuple[float, float]] = []
        self.active = True

    def update(self, dt: float, state: SimState) -> None:
        if not self.active:
            return
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Trail
        self.trail.append((self.x, self.y))
        while len(self.trail) > config.PARTICLE_TRAIL_LENGTH:
            self.trail.pop(0)

    def draw(self, pen: Turtle) -> None:
        if not self.active:
            return
        pen.penup()
        pen.hideturtle()

        # Trail (older = fainter/smaller)
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            t = (i + 1) / max(1, len(self.trail))
            pen.goto(config.CENTER_X + tx, config.CENTER_Y + ty)
            pen.dot(max(0.5, self.size * 0.4 * t), self.color)

        # Head
        pen.goto(config.CENTER_X + self.x, config.CENTER_Y + self.y)
        pen.dot(self.size, self.color)


class ParticleSystem:
    """Manages all ejecta particles."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def spawn_explosion(self, star_radius: float) -> None:
        """Create particles at the core (bounce)."""
        self.particles.clear()
        for _ in range(config.PARTICLE_COUNT):
            dx, dy = random_in_disk(star_radius * 0.5)
            angle = math.atan2(dy, dx) + random.uniform(
                -config.PARTICLE_ANGULAR_NOISE, config.PARTICLE_ANGULAR_NOISE
            )
            speed = config.PARTICLE_BASE_SPEED + random.uniform(
                -config.PARTICLE_SPEED_VARIANCE,
                config.PARTICLE_SPEED_VARIANCE,
            )
            vx, vy = polar_to_cartesian(speed, angle)
            color = random.choice(config.PARTICLE_COLORS)
            size = random.uniform(config.PARTICLE_SIZE_MIN, config.PARTICLE_SIZE_MAX)
            lifetime = random.uniform(
                config.PARTICLE_LIFETIME_MIN,
                config.PARTICLE_LIFETIME_MAX,
            )
            p = Particle(dx, dy, vx, vy, color, size, lifetime)
            self.particles.append(p)

    def update(self, dt: float, state: SimState) -> None:
        for p in self.particles:
            p.update(dt, state)
        self.particles = [p for p in self.particles if p.active]

    def draw(self, pen: Turtle) -> None:
        for p in self.particles:
            p.draw(pen)

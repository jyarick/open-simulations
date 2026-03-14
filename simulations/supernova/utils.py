"""
Helper functions for the supernova simulation.
Keeps the rest of the code clean.
"""
import math
import random


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x to [lo, hi]."""
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation from a to b by t in [0, 1]."""
    return a + (b - a) * clamp(t, 0, 1)


def ease_in_quad(t: float) -> float:
    """Quadratic ease-in: slow start."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out: slow end."""
    return t * (2 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out: slow start and end."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


def polar_to_cartesian(r: float, theta: float) -> tuple[float, float]:
    """Convert polar (r, theta) to Cartesian (x, y). Theta in radians."""
    return (r * math.cos(theta), r * math.sin(theta))


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def random_unit_vector() -> tuple[float, float]:
    """Random 2D unit vector."""
    theta = random.uniform(0, 2 * math.pi)
    return polar_to_cartesian(1.0, theta)


def random_in_disk(radius: float) -> tuple[float, float]:
    """Random point uniformly in a disk of given radius (for spawn positions)."""
    r = radius * math.sqrt(random.random())
    theta = random.uniform(0, 2 * math.pi)
    return polar_to_cartesian(r, theta)

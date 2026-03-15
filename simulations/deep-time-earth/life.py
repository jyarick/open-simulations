"""
Biological progression over deep time.
L in [0, 1] represents life complexity.
"""

from config import LIFE_MILESTONES
from utils import lerp


def get_target_complexity(sim_t: float) -> float:
    """Get target life complexity for given simulation time."""
    sim_t = max(0, min(1, sim_t))
    prev_t, prev_l = LIFE_MILESTONES[0]
    for t, l in LIFE_MILESTONES:
        if sim_t <= t:
            span = t - prev_t
            return lerp(prev_l, l, (sim_t - prev_t) / span) if span > 0 else l
        prev_t, prev_l = t, l
    return prev_l


def update_life_complexity(
    current: float,
    target: float,
    dt: float,
    extinction_dip: float = 0,
) -> float:
    """Smoothly evolve life complexity toward target. Extinction dip reduces it."""
    rate = 0.02
    new = lerp(current, target, rate)
    if extinction_dip > 0:
        new *= 1 - extinction_dip * 0.6
    return max(0, min(1, new))


LIFE_METER_LABELS = [
    (0.0, "no life"),
    (0.1, "microbes"),
    (0.3, "multicellular"),
    (0.5, "marine ecosystems"),
    (0.7, "land plants"),
    (0.85, "dinosaurs"),
    (1.0, "modern"),
]

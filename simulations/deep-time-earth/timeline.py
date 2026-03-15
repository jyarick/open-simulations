"""
Maps normalized time u in [0, 1] to geological epochs.
"""

from config import EPOCHS


def get_current_epoch(sim_t: float) -> str:
    """Return the epoch name for the given normalized simulation time."""
    sim_t = max(0, min(1, sim_t))
    current = EPOCHS[0][1]
    for t, name in EPOCHS:
        if sim_t >= t:
            current = name
    return current


def get_epoch_progress(sim_t: float) -> float:
    """Return progress within current epoch (0-1)."""
    sim_t = max(0, min(1, sim_t))
    prev_t = EPOCHS[0][0]
    for t, name in EPOCHS:
        if sim_t < t:
            span = t - prev_t
            return (sim_t - prev_t) / span if span > 0 else 1.0
        prev_t = t
    return 1.0


def get_timeline_eras() -> list:
    """Return simplified eras for the timeline bar."""
    return [
        (0.0, 0.68, "Precambrian"),
        (0.68, 0.78, "Paleozoic"),
        (0.78, 0.90, "Mesozoic"),
        (0.90, 1.00, "Cenozoic"),
    ]

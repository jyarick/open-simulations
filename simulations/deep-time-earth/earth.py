"""
Planetary surface: continents, oceans, ice, vegetation.
Uses procedural continent generator from drift.py.
"""

from config import CONTINENT_SEED, CONTINENT_COUNT, MOON_VISIBLE_FROM
from drift import generate_initial_continents, update_continents
from utils import lerp


def create_continents(seed: int | None = None, count: int | None = None) -> list:
    """Create initial continent set using procedural generator."""
    return generate_initial_continents(seed=seed, count=count)


def update_continent_drift(state: dict):
    """Update all continent positions and phases."""
    update_continents(state["continents"], dt=1.0)


def get_surface_levels(epoch: str) -> dict:
    """Return ocean_level, ice_level, vegetation_level (0-1) for epoch."""
    levels = {
        "formation": (0, 0, 0),
        "moon_impact": (0, 0, 0),
        "cooling": (0, 0, 0),
        "oceans": (0.7, 0, 0),
        "microbial_life": (0.72, 0, 0.05),
        "oxygenation": (0.74, 0, 0.15),
        "snowball_earth": (0.5, 0.9, 0),
        "complex_life": (0.72, 0.2, 0.35),
        "dinosaurs": (0.7, 0.15, 0.55),
        "kt_extinction": (0.7, 0.2, 0.4),
        "modern": (0.71, 0.1, 0.6),
    }
    base = levels.get(epoch, (0, 0, 0))
    return {"ocean_level": base[0], "ice_level": base[1], "vegetation_level": base[2]}


def update_epoch_state(state: dict):
    """Update ocean, ice, vegetation from epoch. Update moon visibility."""
    levels = get_surface_levels(state["epoch"])
    state["ocean_level"] = lerp(state["ocean_level"], levels["ocean_level"], 0.02)
    state["ice_level"] = lerp(state["ice_level"], levels["ice_level"], 0.02)
    state["vegetation_level"] = lerp(state["vegetation_level"], levels["vegetation_level"], 0.02)
    state["moon_visible"] = state["sim_t"] >= MOON_VISIBLE_FROM

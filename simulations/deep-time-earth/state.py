"""
Simulation state — single source of truth passed through the pipeline.
"""


def create_initial_state():
    """Create the initial simulation state."""
    return {
        "sim_t": 0.0,
        "v_sim": 0.002,
        "paused": False,
        "rotation_angle": 0.0,
        "epoch": "formation",
        "epoch_progress": 0.0,
        "ocean_level": 0.0,
        "ice_level": 0.0,
        "vegetation_level": 0.0,
        "life_complexity": 0.0,
        "atmosphere_tint": (255, 120, 80),
        "extinction_intensity": 0.0,
        "moon_visible": False,
        "moon_angle": 0.0,
        "continents": [],
        "frame_count": 0,
        "spinning": True,
    }


def reset_state(state: dict):
    """Reset state to initial values. Caller must set continents."""
    from config import DEFAULT_V_SIM

    state["sim_t"] = 0.0
    state["v_sim"] = DEFAULT_V_SIM
    state["paused"] = False
    state["rotation_angle"] = 0.0
    state["epoch"] = "formation"
    state["epoch_progress"] = 0.0
    state["ocean_level"] = 0.0
    state["ice_level"] = 0.0
    state["vegetation_level"] = 0.0
    state["life_complexity"] = 0.0
    state["atmosphere_tint"] = (255, 120, 80)
    state["extinction_intensity"] = 0.0
    state["moon_visible"] = False
    state["moon_angle"] = 0.0
    state["continents"] = []
    state["frame_count"] = 0
    state["spinning"] = True

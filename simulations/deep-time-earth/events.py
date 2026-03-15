"""
Dramatic planetary events.
"""

from utils import pulse


def update_events(state: dict):
    """Apply event effects based on current epoch."""
    epoch = state["epoch"]
    frame = state["frame_count"]
    state["extinction_intensity"] = 0.0

    if epoch == "moon_impact":
        state["atmosphere_tint"] = (255, 140, 80)

    elif epoch == "kt_extinction":
        intensity = pulse(frame * 0.3, 15)
        state["extinction_intensity"] = intensity * 0.8
        state["atmosphere_tint"] = (
            int(120 - intensity * 40),
            int(100 - intensity * 30),
            int(80 - intensity * 20),
        )

    elif epoch == "snowball_earth":
        state["atmosphere_tint"] = (200, 215, 230)


def get_extinction_dip(state: dict) -> float:
    """Return 0-1 extinction intensity for life complexity reduction."""
    return state.get("extinction_intensity", 0.0)

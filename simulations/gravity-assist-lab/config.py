"""
Constants, colors, screen size, and physics parameters for Gravity Assist Lab.
All tunable parameters are here for easy modification.
"""

import numpy as np

# =============================================================================
# Screen
# =============================================================================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
PANEL_WIDTH = 260  # Control panel on right
VIEW_SCALE_MIN = 1.0
VIEW_SCALE_MAX = 6.0
TRAIL_LENGTH_MIN = 100
TRAIL_LENGTH_MAX = 2000

# =============================================================================
# Colors (RGB tuples)
# =============================================================================
COLOR_BG = (8, 8, 18)
COLOR_STAR = (255, 221, 68)
COLOR_STAR_GLOW = (255, 200, 50)
COLOR_PLANET = (68, 136, 255)
COLOR_PLANET_RING = (68, 136, 255)
COLOR_JUPITER = (220, 180, 100)
COLOR_JUPITER_RING = (200, 160, 80)
COLOR_SPACECRAFT = (255, 255, 255)
COLOR_VELOCITY_ARROW = (100, 220, 255)
COLOR_PLANET_VELOCITY = (150, 180, 255)
COLOR_HUD_TEXT = (200, 200, 220)
COLOR_HUD_BG = (12, 12, 24, 200)
COLOR_STARFIELD = (60, 60, 90)
COLOR_ESCAPE = (100, 255, 150)
COLOR_BOUND = (255, 180, 100)

# Trail colormap: cool (slow) -> warm (fast)
TRAIL_COLOR_SLOW = (80, 100, 180)
TRAIL_COLOR_FAST = (255, 180, 80)

# =============================================================================
# Physics (normalized units: G=1, star mass=1)
# =============================================================================
G = 1.0
MU_STAR = G * 1.0  # G * M_star for heliocentric energy: epsilon = v^2/2 - mu/r

# Star (fixed at center)
STAR_MASS = 1.0
STAR_POSITION = np.array([0.0, 0.0])
STAR_RADIUS_VISUAL = 0.15

# =============================================================================
# Planet definitions (list of gravitating bodies)
# Each planet: name, mass, orbit_radius, phase (rad), radius_visual, color
# orbit_speed computed from circular orbit: v = sqrt(G*M_star/r), omega = v/r
# =============================================================================
PLANET_DEFS = [
    {
        "name": "inner",
        "mass": 1e-5,
        "orbit_radius": 1.0,
        "phase": 0.0,
        "radius_visual": 0.08,
        "color": COLOR_PLANET,
        "ring_color": COLOR_PLANET_RING,
    },
    {
        "name": "jupiter",
        "mass": 5e-3,  # ~500x inner planet, stronger assists
        "orbit_radius": 2.5,
        "phase": 0.5,  # default; overridden by preset for full_escape
        "radius_visual": 0.12,
        "color": COLOR_JUPITER,
        "ring_color": COLOR_JUPITER_RING,
    },
]

# Spacecraft
SPACECRAFT_MASS = 1.0
SPACECRAFT_RADIUS_VISUAL = 0.02

# Simulation
SIMULATION_DT = 0.002
TIME_SCALE_MIN = 0.1
TIME_SCALE_MAX = 4.0
TIME_SCALE_DEFAULT = 1.0

# View (world coordinates: ±VIEW_SCALE)
VIEW_SCALE = 3.0  # Slightly larger to show outer planet

# =============================================================================
# Scenario presets: different flyby outcomes
# planets: list of planet names from PLANET_DEFS
# spacecraft: x, y, speed, angle_deg (angle from +x axis)
# Geometry: passing "behind" planet (trailing side) gains energy; "in front" loses it
# =============================================================================
PRESETS = [
    {
        "id": "weak_assist",
        "name": "Weak assist",
        "planets": ["inner"],
        "spacecraft": {"x": -2.0, "y": -0.35, "speed": 0.78, "angle_deg": 14},
        "description": "Small boost, stays bound. Pass behind inner planet.",
    },
    {
        "id": "strong_assist",
        "name": "Strong assist",
        "planets": ["inner"],
        "spacecraft": {"x": -2.0, "y": -0.55, "speed": 0.88, "angle_deg": 6},
        "description": "Larger boost, still bound. Closer pass behind inner.",
    },
    {
        "id": "braking_assist",
        "name": "Braking assist",
        "planets": ["inner"],
        "spacecraft": {"x": -2.0, "y": 0.45, "speed": 0.88, "angle_deg": -6},
        "description": "Pass in front of planet: lose heliocentric energy.",
    },
    {
        "id": "near_escape",
        "name": "Near escape",
        "planets": ["jupiter"],
        "planet_phases": {"jupiter": 0.0},
        "spacecraft": {"x": -3.2, "y": -0.35, "speed": 0.74, "angle_deg": 4},
        "description": "Jupiter assist brings epsilon close to zero.",
    },
    {
        "id": "full_escape",
        "name": "Full escape",
        "planets": ["jupiter"],
        "planet_phases": {"jupiter": 0.0},  # Jupiter at (2.5,0) for pass-behind geometry
        "spacecraft": {"x": -3.2, "y": -0.4, "speed": 0.78, "angle_deg": 4},
        "description": "Pass behind Jupiter: prograde assist produces escape.",
    },
    {
        "id": "two_planet_assist",
        "name": "Two-planet assist",
        "planets": ["inner", "jupiter"],
        "spacecraft": {"x": -2.0, "y": -0.5, "speed": 0.82, "angle_deg": 8},
        "description": "Inner then outer: multiple assists build toward escape.",
    },
]

# Active preset: index into PRESETS (0-5). Change here or cycle with keys.
PRESET_INDEX = 0

# =============================================================================
# Visual
# =============================================================================
TRAIL_LENGTH = 800
VELOCITY_ARROW_SCALE = 0.15
PLANET_VELOCITY_ARROW_SCALE = 0.08
GRAVITY_RING_ALPHA = 0.15
GRAVITY_RING_MULTIPLIERS = (1.5, 2.5, 3.5)
STAR_GLOW_RADIUS_MULT = 1.8
NUM_STARS_BACKDROP = 150

# Encounter radius for incoming/outgoing speed tracking
ENCOUNTER_RADIUS = 1.5

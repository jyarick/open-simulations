"""
Global constants for Deep Time Earth simulation.
"""

# Screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Planet
EARTH_RADIUS = 180
EARTH_CENTER_X = 0
EARTH_CENTER_Y = 0

# Timing
FPS = 30
FRAME_TIME = 1.0 / FPS

# Rotation & simulation speed
ROTATION_SPEED = 0.25
DEFAULT_V_SIM = 0.002
MIN_V_SIM = 0.0001
MAX_V_SIM = 0.02

# Starfield
STAR_COUNT = 300

# Epochs (normalized 0-1)
EPOCHS = [
    (0.00, "formation"),
    (0.05, "moon_impact"),
    (0.12, "cooling"),
    (0.22, "oceans"),
    (0.38, "microbial_life"),
    (0.55, "oxygenation"),
    (0.68, "snowball_earth"),
    (0.78, "complex_life"),
    (0.90, "dinosaurs"),
    (0.94, "kt_extinction"),
    (1.00, "modern"),
]

# Procedural continents — point-based rendering
CONTINENT_COUNT = 5
CONTINENT_SEED = 4242
DRIFT_SPEED_SCALE = 1.5
CONTINENT_MIN_RADIUS_DEG = 10
CONTINENT_MAX_RADIUS_DEG = 18
COASTLINE_POINTS = 28
CONTINENT_SURFACE_POINTS = 300  # 200–400 points per continent
CONTINENT_DOT_SIZE = 4
MIN_CONTINENT_SEPARATION_DEG = 40

# Life complexity milestones
LIFE_MILESTONES = [
    (0.0, 0.0),
    (0.22, 0.0),
    (0.38, 0.1),
    (0.55, 0.3),
    (0.68, 0.25),
    (0.78, 0.5),
    (0.90, 0.7),
    (0.94, 0.85),
    (1.00, 1.0),
]

# Moon
MOON_VISIBLE_FROM = 0.05
MOON_RADIUS = 26
MOON_ORBIT_RADIUS = 260
MOON_ORBIT_SPEED = 0.02

# UI layout
LIFE_METER_X = -SCREEN_WIDTH // 2 + 70
LIFE_METER_Y = -SCREEN_HEIGHT // 2 + 120
TIMELINE_Y = -SCREEN_HEIGHT // 2 + 45
TIMELINE_MARGIN = 100
EPOCH_LABEL_Y = SCREEN_HEIGHT // 2 - 35

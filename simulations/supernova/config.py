"""
Central configuration for the supernova turtle simulation.
Tunable constants and style settings — main place for visual and behavior tuning.
"""

# -----------------------------------------------------------------------------
# Screen
# -----------------------------------------------------------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = "#0a0a12"
FRAME_DELAY_MS = 33  # ~30 fps

# -----------------------------------------------------------------------------
# Phase timing (seconds)
# -----------------------------------------------------------------------------
STABLE_DURATION = 3.0
COLLAPSE_DURATION = 2.5
BOUNCE_DURATION = 0.4
EXPLOSION_DURATION = 6.0
REMNANT_FADE_IN = 1.5

# -----------------------------------------------------------------------------
# Star
# -----------------------------------------------------------------------------
STAR_INITIAL_RADIUS = 80
STAR_PULSE_AMPLITUDE = 0.05
STAR_PULSE_SPEED = 2.0
STAR_COLLAPSE_FINAL_FRACTION = 0.08  # R_final = R0 * this
STAR_GLOW_LAYERS = 5
STAR_GLOW_SPREAD = 1.8
STAR_STABLE_COLOR = "#ffcc88"
STAR_COLLAPSE_COLOR = "#cc5522"
STAR_BOUNCE_COLOR = "#ffffcc"

# -----------------------------------------------------------------------------
# Explosion / particles
# -----------------------------------------------------------------------------
PARTICLE_COUNT = 180
PARTICLE_BASE_SPEED = 4.5
PARTICLE_SPEED_VARIANCE = 2.5
PARTICLE_ANGULAR_NOISE = 0.4  # radians
PARTICLE_LIFETIME_MIN = 2.0
PARTICLE_LIFETIME_MAX = 5.0
PARTICLE_SIZE_MIN = 1
PARTICLE_SIZE_MAX = 4
PARTICLE_TRAIL_LENGTH = 12
PARTICLE_COLORS = [
    "#ff8844", "#ffaa66", "#ffcc88", "#ff6622",
    "#cc5522", "#ee7733", "#dd9944", "#ff9966",
]

# -----------------------------------------------------------------------------
# Shockwave
# -----------------------------------------------------------------------------
SHOCK_INITIAL_RADIUS = 20
SHOCK_EXPANSION_SPEED = 120
SHOCK_LINE_WIDTH = 3
SHOCK_FADE_RATE = 0.92  # per second-ish
SHOCK_MAX_RADIUS = 600
SHOCK_COLOR = "#88aaff"

# -----------------------------------------------------------------------------
# Remnant
# -----------------------------------------------------------------------------
BLACK_HOLE_MASS_THRESHOLD = 20.0  # solar masses
NEUTRON_STAR_RADIUS = 8
BLACK_HOLE_RADIUS = 12
NEUTRON_STAR_COLOR = "#eef0ff"
NEUTRON_STAR_GLOW = "#6688cc"
BLACK_HOLE_COLOR = "#0a0a0a"
BLACK_HOLE_RING_COLOR = "#4466aa"
PULSAR_BEAM_LENGTH = 35
PULSAR_BEAM_SPEED = 4.0
ACCRETION_DISK_INNER = 15
ACCRETION_DISK_OUTER = 45

# -----------------------------------------------------------------------------
# Effects
# -----------------------------------------------------------------------------
BOUNCE_FLASH_DURATION = 0.25
BOUNCE_FLASH_COLOR = "#ffffff"
BOUNCE_FLASH_MAX_ALPHA = 0.7
HALO_PULSE_DURATION = 0.5

# -----------------------------------------------------------------------------
# Background
# -----------------------------------------------------------------------------
STARFIELD_COUNT = 120
STARFIELD_COLORS = ["#ffffff", "#ddddee", "#aaaacc", "#8888aa"]
NEBULA_HAZE_STRENGTH = 0.15
NEBULA_COLOR = "#221133"

# -----------------------------------------------------------------------------
# Simulation center (turtle coords)
# -----------------------------------------------------------------------------
CENTER_X = 0
CENTER_Y = 0

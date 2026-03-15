"""
Deep Time Earth — Central configuration.

Run: python main.py
All tunables live here. Grouped by: Mode, Simulation, Intro, Loop, Geometry,
Lighting, Atmosphere, Clouds, Events, Continents, UI, Captions, Debug.
"""

# =============================================================================
# MODE
# =============================================================================
# True = presentation (debug off, help off). False = development (debug on, slower)
PRESENTATION_MODE = True
DEBUG_INITIAL_SPEED = 0.5       # Speed multiplier when in debug mode

# =============================================================================
# SIMULATION
# =============================================================================
SIM_SPEED = 0.00010             # Deep-time advance per frame
FRAME_DELAY_MS = 33              # ~30 fps
SPEED_LEVELS = [0.5, 1, 2, 4, 8, 16, 32, 64]

# =============================================================================
# ROTATION
# =============================================================================
ROTATION_SPEED = 0.38           # Earth spin
MOON_ORBIT_SPEED = 0.009        # Moon orbit
CLOUD_DRIFT_SPEED = 0.014       # Cloud layer
LIGHT_ROTATION_SPEED = 0.018     # Day/night terminator

# =============================================================================
# INTRO
# =============================================================================
INTRO_TITLE_DURATION = 1.2       # Title alone (seconds)
INTRO_SUBTITLE_DURATION = 1.8    # Subtitle appears, then both hold

# =============================================================================
# LOOP
# =============================================================================
LOOP_HOLD_AT_END_SEC = 2.5      # Hold at "Present Day" before cycling
LOOP_HOLD_SIM_T = 0.995         # sim_t at hold (near end of timeline)

# =============================================================================
# SMOOTHING
# =============================================================================
LIFE_SMOOTH_ALPHA = 0.07
OVERLAY_SMOOTH_ALPHA = 0.09

# =============================================================================
# GEOMETRY
# =============================================================================
EARTH_RADIUS = 80
EARTH_CENTER_X = 0
EARTH_CENTER_Y = 0
MOON_RADIUS = 18
MOON_ORBIT_RADIUS = 130

# =============================================================================
# LIGHTING
# =============================================================================
NIGHT_SIDE_COLOR = "navy"
TERMINATOR_SEGMENTS = 36
STAR_COLOR = "ghostwhite"       # Earth remains focal point
MOON_COLOR = "lightgray"

# =============================================================================
# ATMOSPHERE
# =============================================================================
ATMOSPHERE_HALO_RADIUS = 8
ATMOSPHERE_BASE_COLOR = "lightcyan"

# =============================================================================
# CLOUDS
# =============================================================================
CLOUD_DOT_SIZE = 2
CLOUD_BASE_COLOR = "whitesmoke"
CLOUD_DENSITY_SCALE = 0.72

# =============================================================================
# EVENTS
# =============================================================================
EVENT_OVERLAY_MIN_VISIBLE = 0.03

# =============================================================================
# CONTINENTS
# =============================================================================
CONTINENT_DOT_SIZE = 4

# =============================================================================
# UI — Timeline, life meter
# =============================================================================
LIFE_METER_LEFT = -370
LIFE_METER_BOTTOM = -220
LIFE_METER_WIDTH = 24
LIFE_METER_HEIGHT = 200
TIMELINE_LEFT = -350
TIMELINE_RIGHT = 350
TIMELINE_Y = -280
TIMELINE_HEIGHT = 11
TIMELINE_MARKER_WIDTH = 3

# =============================================================================
# CAPTIONS
# =============================================================================
CAPTION_Y_PRIMARY = -228
CAPTION_Y_SECONDARY = -248
CAPTION_Y_TERTIARY = -264
CAPTION_LINE_SPACING = 20
CAPTION_PRIMARY_SIZE = 15
CAPTION_SECONDARY_SIZE = 11
CAPTION_TERTIARY_SIZE = 9
CAPTION_PRIMARY_COLOR = "white"
CAPTION_SECONDARY_COLOR = "gray85"
CAPTION_TERTIARY_COLOR = "gray65"

# =============================================================================
# INTRO / HELP
# =============================================================================
INTRO_TITLE = "Deep Time Earth"
INTRO_SUBTITLE = "A visualization of Earth evolving through geologic time"
HELP_OVERLAY_X = -360
HELP_OVERLAY_Y = 200
HELP_FONT_SIZE = 9

# =============================================================================
# DEBUG
# =============================================================================
DEBUG_OVERLAY_X = -380
DEBUG_OVERLAY_Y = 250
DEBUG_FONT_SIZE = 9
DEBUG_LINE_SPACING = 12

"""
Physical and simulation constants for Gravity Assist Lab.
Uses normalized units: G=1, star mass=1, length=planet orbit radius.
"""

import numpy as np

# =============================================================================
# Physical Constants (normalized units for clean simulation)
# =============================================================================

G = 1.0  # Gravitational constant (normalized)

# =============================================================================
# Simulation Defaults (override in main.py)
# =============================================================================

# Star (fixed at center)
STAR_MASS = 1.0  # Reference mass
STAR_RADIUS_VISUAL = 0.15  # Display size (arbitrary units)

# Planet (small mass so it orbits star; v = sqrt(G*M_star/r) for circular orbit)
PLANET_MASS = 1e-5  # Small compared to star
PLANET_ORBIT_RADIUS = 1.0  # Distance from star
PLANET_ORBIT_SPEED = 1.0  # Angular velocity (rad/s); v_orb = orbit_speed * orbit_radius
PLANET_RADIUS_VISUAL = 0.08  # Display size

# Spacecraft
SPACECRAFT_MASS = 1.0  # Negligible for gravity, used for energy calculation
SPACECRAFT_RADIUS_VISUAL = 0.02  # Display size

# Simulation
SIMULATION_DT = 0.001  # Time step
TRAIL_LENGTH = 800  # Number of points in trajectory trail

# View
VIEW_SCALE = 2.5  # Plot limits: ±VIEW_SCALE
GRAVITY_RING_ALPHA = 0.15  # Opacity of gravity field rings

"""
Procedural continental drift engine.

Generates smooth, blob-like continents in spherical coordinates.
Each continent has a center, irregular coastline, and evolves via drift + spin + subtle deformation.
Designed for future splitting/merging support.

Shape generation model
----------------------
Boundary radius at angle θ (around center):
  r(θ) = base_radius
       + m1*sin(θ) + m2*sin(2θ) + m3*cos(θ)   # low-freq modes
       + smooth_noise_profile(seed, θ) * roughness * base_radius
       + 0.02*sin(sim_time*0.001)*base_radius   # coastline breathing

Each (θ, r) is converted to (lat, lon) via spherical_offset(), which uses a
tangent-plane approximation: valid for angular_dist < ~30°, degrades near poles.

Tradeoffs
---------
- Tangent-plane is fast and simple; not geodesically exact for large continents.
- smooth_noise_profile uses low-frequency octaves only; no jagged coastlines.
- Splitting/merging: continent dicts are independent; clone/regenerate as needed.
"""

import math
import random

from config import (
    CONTINENT_COUNT,
    CONTINENT_SEED,
    DRIFT_SPEED_SCALE,
    CONTINENT_MIN_RADIUS_DEG,
    CONTINENT_MAX_RADIUS_DEG,
    COASTLINE_POINTS,
    CONTINENT_SURFACE_POINTS,
    MIN_CONTINENT_SEPARATION_DEG,
)
from utils import (
    wrap_longitude,
    clamp_latitude,
    deg_to_rad,
    spherical_offset,
    smooth_noise_profile,
    angular_distance_deg,
    lerp,
)


def _place_centers(seed: int, count: int) -> list[tuple[float, float]]:
    """Place continent centers with minimum separation. Returns [(lat, lon), ...]."""
    rng = random.Random(seed)
    centers = []
    attempts = 0
    max_attempts = count * 80

    while len(centers) < count and attempts < max_attempts:
        lat = (rng.random() - 0.5) * 140  # -70 to 70
        lon = (rng.random() - 0.5) * 360

        valid = True
        for clat, clon in centers:
            if angular_distance_deg(lat, lon, clat, clon) < MIN_CONTINENT_SEPARATION_DEG:
                valid = False
                break

        if valid:
            centers.append((lat, lon))
        attempts += 1

    # Fallback: spiral layout
    while len(centers) < count:
        i = len(centers)
        angle = 2 * math.pi * i / count + rng.random() * 0.3
        lat = 50 * math.sin(angle * 0.8)
        lon = 150 * math.cos(angle)
        centers.append((lat, lon))

    return centers


def generate_continent(
    name: str,
    center_lat: float,
    center_lon: float,
    seed: int,
    base_radius_deg: float | None = None,
) -> dict:
    """
    Generate a single procedural continent.

    Shape: low-frequency sinusoids + smooth noise for irregular but coherent coastlines.
    No jagged edges; smooth blob-like silhouettes.
    """
    rng = random.Random(seed)
    radius = base_radius_deg or (
        CONTINENT_MIN_RADIUS_DEG +
        rng.random() * (CONTINENT_MAX_RADIUS_DEG - CONTINENT_MIN_RADIUS_DEG)
    )

    # Low-frequency shape modes (smooth continental outline)
    mode1 = (rng.random() - 0.5) * 0.15 * radius
    mode2 = (rng.random() - 0.5) * 0.1 * radius
    mode3 = (rng.random() - 0.5) * 0.08 * radius

    c = {
        "name": name,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "base_radius_deg": radius,
        "drift_lat": (rng.random() - 0.5) * 0.002 * DRIFT_SPEED_SCALE,
        "drift_lon": (rng.random() - 0.5) * 0.012 * DRIFT_SPEED_SCALE,
        "spin": (rng.random() - 0.5) * 0.004 * DRIFT_SPEED_SCALE,
        "rotation_phase": rng.random() * 2 * math.pi,
        "roughness": 0.12 + rng.random() * 0.06,  # ~0.15 target
        "seed": seed,
        "mode1": mode1,
        "mode2": mode2,
        "mode3": mode3,
    }
    c["surface_points"] = _generate_surface_points(c)
    return c


def _radius_at_angle(continent: dict, angle: float, sim_time: float = 0.0) -> float:
    """Radius at angle (radians) for continent shape. Same logic as boundary."""
    base_r = continent["base_radius_deg"]
    m1 = continent.get("mode1", 0)
    m2 = continent.get("mode2", 0)
    m3 = continent.get("mode3", 0)
    roughness = continent["roughness"]
    seed = continent["seed"]
    breath = 0.02 * math.sin(sim_time * 0.001) * base_r
    r_modes = base_r + m1 * math.sin(angle) + m2 * math.sin(2 * angle) + m3 * math.cos(angle)
    r_noise = smooth_noise_profile(seed, angle) * roughness * base_r
    r_total = r_modes + r_noise + breath
    return max(base_r * 0.5, min(base_r * 1.4, r_total))


def _generate_surface_points(continent: dict) -> list[tuple[float, float]]:
    """
    Generate ~200–400 points inside the continent.
    Returns list of (angle, radius) in local coords. Angle in radians, radius in degrees.
    Uses rejection sampling: keep points where r < radius_at_angle.
    """
    rng = random.Random(continent["seed"] + 12345)
    points = []
    base_r = continent["base_radius_deg"]
    max_r = base_r * 1.4
    target = CONTINENT_SURFACE_POINTS
    attempts = 0
    max_attempts = target * 20

    while len(points) < target and attempts < max_attempts:
        angle = rng.random() * 2 * math.pi
        r = rng.random() * max_r
        r_bound = _radius_at_angle(continent, angle)
        if r <= r_bound:
            points.append((angle, r))
        attempts += 1

    return points


def get_continent_surface_points_latlon(
    continent: dict,
    sim_time: float = 0.0,
) -> list[tuple[float, float]]:
    """
    Convert surface points (angle, radius) to (lat, lon) in degrees.
    Points move with continent center and rotation.
    """
    lat0 = continent["center_lat"]
    lon0 = continent["center_lon"]
    phase = continent["rotation_phase"]
    result = []
    for angle, radius in continent["surface_points"]:
        azimuth = math.degrees(angle + phase)
        lat, lon = spherical_offset(lat0, lon0, azimuth, radius)
        lat = clamp_latitude(lat)
        lon = wrap_longitude(lon)
        result.append((lat, lon))
    return result


def get_continent_boundary_latlon(
    continent: dict,
    num_points: int | None = None,
    sim_time: float = 0.0,
) -> list[tuple[float, float]]:
    """
    Compute boundary (lat, lon) points for a continent.

    Uses spherical_offset for proper geometry. Shape combines:
    - base radius
    - low-frequency sinusoids (mode1, mode2, mode3)
    - smooth_noise_profile for mild irregularity
    - sim_time for subtle coastline "breathing" (very small deformation over time)

    Returns list of (lat, lon) in degrees, closed loop.
    """
    n = num_points or COASTLINE_POINTS
    lat0 = continent["center_lat"]
    lon0 = continent["center_lon"]
    base_r = continent["base_radius_deg"]
    phase = continent["rotation_phase"]
    roughness = continent["roughness"]
    seed = continent["seed"]
    m1, m2, m3 = continent.get("mode1", 0), continent.get("mode2", 0), continent.get("mode3", 0)

    # Subtle time-dependent deformation (coastline breathing)
    breath = 0.02 * math.sin(sim_time * 0.001) * base_r

    points = []
    for i in range(n):
        # Angle around the continent (0 = north)
        angle = 2 * math.pi * i / n + phase

        # Radius at this angle: base + low-freq modes + smooth noise
        r_modes = base_r + m1 * math.sin(angle) + m2 * math.sin(2 * angle) + m3 * math.cos(angle)
        r_noise = smooth_noise_profile(seed, angle) * roughness * base_r
        r_total = r_modes + r_noise + breath
        r_total = max(base_r * 0.5, min(base_r * 1.4, r_total))

        # Spherical offset: azimuth 0 = north, angle goes CCW
        azimuth = math.degrees(angle)
        new_lat, new_lon = spherical_offset(lat0, lon0, azimuth, r_total)
        new_lat = clamp_latitude(new_lat)
        new_lon = wrap_longitude(new_lon)
        points.append((new_lat, new_lon))

    return points


def update_continent(continent: dict, dt: float = 1.0):
    """
    Update continent position and phase for one time step.
    dt: simulation time step (e.g. 1.0 per frame).
    """
    continent["center_lat"] += continent["drift_lat"] * dt
    continent["center_lon"] += continent["drift_lon"] * dt
    continent["rotation_phase"] += continent["spin"] * dt

    continent["center_lat"] = clamp_latitude(continent["center_lat"])
    continent["center_lon"] = wrap_longitude(continent["center_lon"])


def update_continents(continents: list[dict], dt: float = 1.0):
    """Update all continents."""
    for c in continents:
        update_continent(c, dt)


def generate_initial_continents(
    seed: int | None = None,
    count: int | None = None,
) -> list[dict]:
    """
    Generate the initial set of procedural continents.
    Count and seed are configurable for future epoch-based regeneration.
    """
    seed = seed if seed is not None else CONTINENT_SEED
    count = count if count is not None else CONTINENT_COUNT

    centers = _place_centers(seed, count)
    continents = []
    for i, (lat, lon) in enumerate(centers):
        c = generate_continent(f"continent_{i}", lat, lon, seed + (i + 1) * 7919)
        continents.append(c)
    return continents


# --- Projection for renderer ---

def is_point_visible(lat: float, lon: float, rotation_angle: float) -> bool:
    """Hemisphere visibility test: True if point is on front hemisphere."""
    phi = deg_to_rad(lat)
    lam = deg_to_rad(lon + rotation_angle)
    return math.cos(phi) * math.cos(lam) > 0


def project_to_screen(
    lat: float,
    lon: float,
    rotation_angle: float,
    center_x: float,
    center_y: float,
    radius: float,
) -> tuple[float, float] | None:
    """
    Spherical projection: lat/lon (degrees) -> screen coords relative to Earth center.
    Pipeline:
      1. lon_rot = lon + rotation_angle
      2. x = earth_radius * cos(lat) * sin(lon_rot), y = earth_radius * sin(lat)
      3. Visibility: cos(lat) * cos(lon_rot) > 0 (skip back hemisphere)
      4. screen_x = earth_center_x + x, screen_y = earth_center_y + y
    """
    lon_rot = lon + rotation_angle
    lat_rad = deg_to_rad(lat)
    lon_rad = deg_to_rad(lon_rot)

    if math.cos(lat_rad) * math.cos(lon_rad) <= 0:
        return None

    x_globe = radius * math.cos(lat_rad) * math.sin(lon_rad)
    y_globe = radius * math.sin(lat_rad)

    screen_x = center_x + x_globe
    screen_y = center_y + y_globe

    dx = screen_x - center_x
    dy = screen_y - center_y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > radius:
        scale = radius / dist
        screen_x = center_x + dx * scale
        screen_y = center_y + dy * scale

    return (screen_x, screen_y)

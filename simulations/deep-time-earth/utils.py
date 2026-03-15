"""
Utility functions for Deep Time Earth.
Spherical geometry helpers and smooth noise for continent generation.
"""

import math
import random


# --- Angle helpers ---

def deg_to_rad(deg: float) -> float:
    """Convert degrees to radians."""
    return math.radians(deg)


def rad_to_deg(rad: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(rad)


def wrap_longitude(lon: float) -> float:
    """Wrap longitude to [-180, 180]."""
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return lon


def clamp_latitude(lat: float, lo: float = -85, hi: float = 85) -> float:
    """Clamp latitude to avoid poles (default ±85°)."""
    return max(lo, min(hi, lat))


# --- Spherical geometry ---

def spherical_offset(lat0: float, lon0: float, azimuth_deg: float,
                    angular_dist_deg: float) -> tuple[float, float]:
    """
    Compute a new (lat, lon) by moving from (lat0, lon0) along a great-circle
    direction for a given angular distance.

    Uses a tangent-plane approximation valid for angular_dist < ~30°.
    azimuth_deg: 0 = north, 90 = east, 180 = south, 270 = west.

    Returns (new_lat, new_lon) in degrees.
    """
    lat0_rad = deg_to_rad(lat0)
    lon0_rad = deg_to_rad(lon0)
    az_rad = deg_to_rad(azimuth_deg)
    d_rad = deg_to_rad(angular_dist_deg)

    # Tangent-plane offset at (lat0, lon0):
    # North component: d * cos(azimuth)
    # East component: d * sin(azimuth) / cos(lat0)
    dlat_rad = d_rad * math.cos(az_rad)
    dlon_rad = d_rad * math.sin(az_rad) / max(0.01, math.cos(lat0_rad))

    new_lat_rad = lat0_rad + dlat_rad
    new_lon_rad = lon0_rad + dlon_rad

    return rad_to_deg(new_lat_rad), wrap_longitude(rad_to_deg(new_lon_rad))


def angular_distance_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine angular distance in degrees between two points on the sphere."""
    phi1, phi2 = deg_to_rad(lat1), deg_to_rad(lat2)
    dlam = deg_to_rad(abs(lon2 - lon1))
    dphi = abs(phi2 - phi1)
    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
    return rad_to_deg(2 * math.asin(min(1, math.sqrt(a))))


# --- Smooth noise (low-frequency, no jaggedness) ---

def _hash_to_float(seed: int, *args) -> float:
    """Deterministic [0,1) from seed and args."""
    h = seed
    for a in args:
        h = (h * 31 + (int(a * 1000) if isinstance(a, float) else hash(a))) & 0x7FFFFFFF
    return (h % 10000) / 10000.0


def smooth_noise_profile(seed: int, angle: float, num_octaves: int = 3) -> float:
    """
    Low-frequency noise for coastline radius variation.
    Returns value in [0, 1]. Use for smooth, blob-like shapes.
    """
    total = 0.0
    amp = 1.0
    freq = 1.0
    max_val = 0.0
    for i in range(num_octaves):
        # Sample at low frequency
        x = angle * freq * 0.1 + i * 7.3
        n = _hash_to_float(seed, x)
        total += n * amp
        max_val += amp
        amp *= 0.5
        freq *= 2.0
    return total / max_val


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * max(0, min(1, t))


def pulse(t: float, period: float = 0.1) -> float:
    """Oscillating pulse for extinction effects. Returns 0-1."""
    return 0.5 + 0.5 * math.sin(t * 2 * math.pi / period)


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))

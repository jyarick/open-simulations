"""
Deep Time Earth — Epoch definitions, events, overlay styles, continent/cloud generation.

Epoch system: sim_t in [0,1] maps to geologic eras. Each epoch has colors, life level, captions.
Event system: events overlap epochs; event_strength() gives fade-in/peak/fade-out. Supports
wrap (e.g. K-Pg end=0.02). Overlay styles define surface appearance during events.
"""

import math
import random

# =============================================================================
# EPOCHS — Geologic eras with colors, life levels, captions
# =============================================================================
EPOCHS = [
    {
        "id": "hadean",
        "name": "Hadean",
        "start": 0.0,
        "end": 0.15,
        "earth_color": "darkblue",
        "atmosphere_color": "gray30",
        "continent_color": "gray",
        "cloud_density": 0.3,
        "base_life": 0.0,
        "climate": "hostile",
        "caption_theme": "A molten world begins to cool",
    },
    {
        "id": "archean",
        "name": "Archean",
        "start": 0.15,
        "end": 0.33,
        "earth_color": "darkblue",
        "atmosphere_color": "gray40",
        "continent_color": "darkgray",
        "cloud_density": 0.5,
        "base_life": 0.15,
        "climate": "primordial",
        "caption_theme": "First life emerges in the oceans",
    },
    {
        "id": "proterozoic",
        "name": "Proterozoic",
        "start": 0.33,
        "end": 0.55,
        "earth_color": "steelblue",
        "atmosphere_color": "lightcyan",
        "continent_color": "darkolivegreen",
        "cloud_density": 0.7,
        "base_life": 0.45,
        "climate": "transitional",
        "caption_theme": "Complex cells evolve",
    },
    {
        "id": "phanerozoic",
        "name": "Phanerozoic",
        "start": 0.55,
        "end": 0.85,
        "earth_color": "dodgerblue",
        "atmosphere_color": "lightcyan",
        "continent_color": "forestgreen",
        "cloud_density": 0.85,
        "base_life": 0.75,
        "climate": "diverse",
        "caption_theme": "Life diversifies across land and sea",
    },
    {
        "id": "cenozoic",
        "name": "Cenozoic",
        "start": 0.85,
        "end": 1.0,
        "earth_color": "dodgerblue",
        "atmosphere_color": "aliceblue",
        "continent_color": "forestgreen",
        "cloud_density": 1.0,
        "base_life": 0.95,
        "climate": "modern",
        "caption_theme": "The age of mammals",
    },
]

# =============================================================================
# EVENTS — Major geologic events with overlays and captions
# =============================================================================
EVENTS = [
    {
        "name": "Snowball Earth",
        "event_type": "glaciation",
        "start": 0.22,
        "peak": 0.26,
        "end": 0.30,
        "intensity": 0.9,
        "caption_title": "Snowball Earth",
        "caption_subtitle": "Oceans freeze nearly worldwide",
        "caption_tertiary": "Climate: severe global glaciation",
        "surface_tint": "aliceblue",
        "atmosphere_tint": "white",
        "continent_contrast": "slategray",
        "life_impact": 0.8,
        "overlay_style": "glaciation",
    },
    {
        "name": "Great Oxidation",
        "event_type": "oxidation",
        "start": 0.35,
        "peak": 0.40,
        "end": 0.45,
        "intensity": 0.7,
        "caption_title": "Great Oxidation Event",
        "caption_subtitle": "Atmospheric oxygen begins reshaping the planet",
        "caption_tertiary": "Atmosphere: oxygen rise",
        "surface_tint": None,
        "atmosphere_tint": "palegreen",
        "continent_contrast": None,
        "life_impact": 0.3,
        "overlay_style": "oxidation",
    },
    {
        "name": "Cambrian Explosion",
        "event_type": "diversification",
        "start": 0.52,
        "peak": 0.55,
        "end": 0.58,
        "intensity": 0.6,
        "caption_title": "Cambrian Explosion",
        "caption_subtitle": "Life diversifies explosively",
        "caption_tertiary": "Biosphere: rapid diversification",
        "surface_tint": None,
        "atmosphere_tint": None,
        "continent_contrast": None,
        "life_impact": -0.2,
        "overlay_style": "diversification",
    },
    {
        "name": "Permian Extinction",
        "event_type": "volcanism",
        "start": 0.68,
        "peak": 0.70,
        "end": 0.72,
        "intensity": 1.0,
        "caption_title": "Permian Extinction",
        "caption_subtitle": "Mass volcanism and collapse of life",
        "caption_tertiary": "Biosphere stress: extreme",
        "surface_tint": "dimgray",
        "atmosphere_tint": "darkgray",
        "life_impact": 0.85,
        "overlay_style": "volcanism",
    },
    {
        "name": "K-Pg Impact",
        "event_type": "impact",
        "start": 0.96,
        "peak": 0.98,
        "end": 0.02,
        "intensity": 1.0,
        "caption_title": "K-Pg Impact",
        "caption_subtitle": "A sudden catastrophe resets Earth's biosphere",
        "caption_tertiary": "Biosphere stress: extreme",
        "surface_tint": "indianred",
        "atmosphere_tint": "gray25",
        "continent_contrast": "gray25",
        "life_impact": 0.9,
        "overlay_style": "impact",
    },
]

# =============================================================================
# OVERLAY STYLES — Event-specific surface/ring appearance
# =============================================================================
OVERLAY_STYLES = {
    "glaciation": {
        "surface_color": "aliceblue",
        "ring": False,
        "ring_color": None,
    },
    "oxidation": {
        "surface_color": "honeydew",
        "ring": False,
        "ring_color": None,
    },
    "volcanism": {
        "surface_color": "dimgray",
        "ring": True,
        "ring_color": "darkred",
        "ring_size": 4,
    },
    "impact": {
        "surface_color": "indianred",
        "ring": True,
        "ring_color": "darkred",
        "ring_size": 8,
    },
    "diversification": {
        "surface_color": "mintcream",
        "ring": False,
        "ring_color": None,
    },
}

# =============================================================================
# HELPERS
# =============================================================================
def get_epoch_at(t):
    t = t % 1.0
    for e in reversed(EPOCHS):
        if e["start"] <= t < e["end"]:
            return e
    return EPOCHS[-1]


def get_active_event(t):
    t_norm = t % 1.0
    for ev in EVENTS:
        s, e = ev["start"], ev["end"]
        if s <= e:
            if s <= t_norm <= e:
                return ev
        else:
            if t_norm >= s or t_norm <= e:
                return ev
    return None


def event_strength(t, ev):
    """Fade-in, peak, fade-out. Returns 0-1. Handles wrap (e.g. K-Pg end=0.02)."""
    t_norm = t % 1.0
    s, pk, e = ev["start"], ev["peak"], ev["end"]

    if s <= e:
        if t_norm < s or t_norm > e:
            return 0.0
        t_eff = t_norm
    else:
        if t_norm > e and t_norm < s:
            return 0.0
        t_eff = t_norm + 1.0 if t_norm <= e else t_norm
        s, pk, e = s, pk, e + 1.0

    if t_eff <= pk:
        if s == pk:
            return 1.0
        return (t_eff - s) / (pk - s)
    else:
        if pk == e:
            return 1.0
        return (e - t_eff) / (e - pk)


def wrap_lon(lon):
    while lon >= 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return lon


# =============================================================================
# CONTINENT GENERATION (Step 8)
# =============================================================================
def generate_continent_offsets(angular_radius, count, seed):
    points = []
    rng = random.Random(seed)
    attempts = 0
    max_attempts = count * 8

    while len(points) < count and attempts < max_attempts:
        attempts += 1
        angle = rng.uniform(0, 2 * math.pi)
        r_norm = rng.uniform(0, 1) ** 0.6
        wobble = 0.88 + 0.28 * math.sin(angle * 3) + 0.1 * (rng.random() - 0.5)
        wobble = max(0.55, min(1.12, wobble))
        r = angular_radius * r_norm * wobble
        lat_off = r * math.sin(angle)
        lon_off = r * math.cos(angle)
        if lat_off * lat_off + lon_off * lon_off <= (angular_radius * 1.02) ** 2:
            points.append((lat_off, lon_off))

    return points


def create_continent(center_lat, center_lon, angular_radius, point_count, seed,
                     drift_lon=0.0, drift_lat=0.0):
    return {
        "center_lat": center_lat,
        "center_lon": center_lon,
        "initial_center_lat": center_lat,
        "initial_center_lon": center_lon,
        "drift_lon": drift_lon,
        "drift_lat": drift_lat,
        "angular_radius": angular_radius,
        "offsets": generate_continent_offsets(angular_radius, point_count, seed),
    }


def reset_continents(continents):
    """Reset continent positions for clean loop wrap."""
    for c in continents:
        c["center_lat"] = c["initial_center_lat"]
        c["center_lon"] = c["initial_center_lon"]


# =============================================================================
# CLOUD GENERATION
# =============================================================================
def generate_cloud_points(seed, density=1.0):
    rng = random.Random(seed)
    n = int(100 + 80 * density)
    points = []
    for _ in range(n):
        if rng.random() < 0.6:
            lat = rng.gauss(0, 30)
        else:
            lat = rng.uniform(-60, 60)
        lat = max(-75, min(75, lat))
        lon = rng.uniform(-180, 180)
        points.append((lat, lon))
    return points


# =============================================================================
# STAR POSITIONS
# =============================================================================
def generate_stars(seed, count=90):
    rng = random.Random(seed)
    return [
        (rng.randint(-400, 400), rng.randint(-300, 300), rng.randint(1, 3))
        for _ in range(count)
    ]

"""
Renders the full Deep Time Earth scene.
"""

import math
import turtle

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    EARTH_RADIUS,
    EARTH_CENTER_X,
    EARTH_CENTER_Y,
    STAR_COUNT,
    MOON_RADIUS,
    MOON_ORBIT_RADIUS,
    LIFE_METER_X,
    LIFE_METER_Y,
    TIMELINE_Y,
    TIMELINE_MARGIN,
    CONTINENT_DOT_SIZE,
)
from drift import get_continent_surface_points_latlon, project_to_screen
from palette import get_epoch_colors, rgb_to_hex
from timeline import get_timeline_eras
from life import LIFE_METER_LABELS

_stars = None


def _get_stars():
    global _stars
    if _stars is None:
        import random
        r = random.Random(42)
        _stars = [
            (
                r.uniform(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2),
                r.uniform(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2),
                r.uniform(0.4, 1.0),
                r.choice([1, 2, 3]),
            )
            for _ in range(STAR_COUNT)
        ]
    return _stars


def draw_starfield(pen):
    pen.penup()
    pen.color("white")
    for sx, sy, bright, size in _get_stars():
        pen.goto(sx, sy)
        pen.dot(size)


def draw_earth_base(pen, state: dict):
    """Draw base planet disk only. Rim highlight drawn after continents."""
    base, _, _, _, _ = get_epoch_colors(state["epoch"])
    pen.penup()
    pen.goto(EARTH_CENTER_X, EARTH_CENTER_Y - EARTH_RADIUS)
    pen.pendown()
    pen.fillcolor(rgb_to_hex(base))
    pen.color(rgb_to_hex(base))
    pen.begin_fill()
    pen.circle(EARTH_RADIUS)
    pen.end_fill()


def draw_earth_rim(pen, state: dict):
    """
    Draw rim lighting (atmosphere glow at limb).
    Called after oceans, before continents, so rim shows at horizon
    and continents render on top, keeping the lighting effect visible.
    """
    _, _, _, _, atm = get_epoch_colors(state["epoch"])
    glow = (min(255, atm[0] + 25), min(255, atm[1] + 25), min(255, atm[2] + 25))
    pen.penup()
    pen.goto(EARTH_CENTER_X, EARTH_CENTER_Y - EARTH_RADIUS - 4)
    pen.pendown()
    pen.fillcolor(rgb_to_hex(glow))
    pen.color(rgb_to_hex(glow))
    pen.begin_fill()
    pen.circle(EARTH_RADIUS + 4)
    pen.end_fill()
    # Redraw base+ocean area so rim is only at edge; continents draw on top
    base, ocean, _, _, _ = get_epoch_colors(state["epoch"])
    level = state.get("ocean_level", 0)
    if level > 0:
        r = int(ocean[0] * level + 25 * (1 - level))
        g = int(ocean[1] * level + 35 * (1 - level))
        b = int(ocean[2] * level + 45 * (1 - level))
        fill_color = rgb_to_hex((r, g, b))
    else:
        fill_color = rgb_to_hex(base)
    pen.penup()
    pen.goto(EARTH_CENTER_X, EARTH_CENTER_Y - EARTH_RADIUS * 0.94)
    pen.pendown()
    pen.fillcolor(fill_color)
    pen.color(fill_color)
    pen.begin_fill()
    pen.circle(EARTH_RADIUS * 0.94)
    pen.end_fill()


def draw_continents(pen, state: dict):
    """
    Point-based continent rendering.
    Each continent = collection of surface points in lat/lon.
    For each point: project to screen, if visible draw dot. No polygons.
    """
    rot = state["rotation_angle"]
    base, _, _, veg, _ = get_epoch_colors(state["epoch"])
    veg_level = state["vegetation_level"]
    sim_time = state.get("frame_count", 0) * 1.0

    land_darken = 0.88
    r_base = int(base[0] * land_darken)
    g_base = int(base[1] * land_darken)
    b_base = int(base[2] * land_darken)

    for continent in state["continents"]:
        points = get_continent_surface_points_latlon(continent, sim_time)

        r = int(r_base + (veg[0] * 0.9 - r_base) * veg_level)
        g = int(g_base + (veg[1] * 0.9 - g_base) * veg_level)
        b = int(b_base + (veg[2] * 0.9 - b_base) * veg_level)
        color = rgb_to_hex((max(0, r), max(0, g), max(0, b)))

        pen.penup()
        pen.pencolor(color)
        pen.fillcolor(color)

        for lat, lon in points:
            pt = project_to_screen(
                lat, lon, rot,
                EARTH_CENTER_X, EARTH_CENTER_Y,
                EARTH_RADIUS,
            )
            if pt is not None:
                pen.goto(pt[0], pt[1])
                pen.dot(CONTINENT_DOT_SIZE)


def draw_oceans(pen, state: dict):
    _, ocean, _, _, _ = get_epoch_colors(state["epoch"])
    level = state["ocean_level"]
    if level <= 0:
        return
    pen.penup()
    pen.goto(EARTH_CENTER_X, EARTH_CENTER_Y - EARTH_RADIUS * 0.94)
    pen.pendown()
    r = int(ocean[0] * level + 25 * (1 - level))
    g = int(ocean[1] * level + 35 * (1 - level))
    b = int(ocean[2] * level + 45 * (1 - level))
    pen.fillcolor(rgb_to_hex((r, g, b)))
    pen.color(rgb_to_hex((r, g, b)))
    pen.begin_fill()
    pen.circle(EARTH_RADIUS * 0.94)
    pen.end_fill()


def draw_ice(pen, state: dict):
    if state["ice_level"] <= 0:
        return
    _, _, ice, _, _ = get_epoch_colors(state["epoch"])
    cap_height = EARTH_RADIUS * 0.22 * state["ice_level"]
    pen.penup()
    pen.fillcolor(rgb_to_hex(ice))
    pen.color(rgb_to_hex(ice))
    pen.goto(EARTH_CENTER_X - EARTH_RADIUS * 0.65, EARTH_CENTER_Y + EARTH_RADIUS - cap_height)
    pen.pendown()
    pen.begin_fill()
    pen.setheading(0)
    pen.forward(EARTH_RADIUS * 1.3)
    pen.left(90)
    pen.forward(cap_height * 2)
    pen.left(90)
    pen.forward(EARTH_RADIUS * 1.3)
    pen.left(90)
    pen.forward(cap_height * 2)
    pen.end_fill()
    pen.penup()
    pen.goto(EARTH_CENTER_X - EARTH_RADIUS * 0.65, EARTH_CENTER_Y - EARTH_RADIUS - cap_height)
    pen.pendown()
    pen.begin_fill()
    pen.setheading(0)
    pen.forward(EARTH_RADIUS * 1.3)
    pen.left(90)
    pen.forward(cap_height * 2)
    pen.left(90)
    pen.forward(EARTH_RADIUS * 1.3)
    pen.left(90)
    pen.forward(cap_height * 2)
    pen.end_fill()


def draw_event_overlays(pen, state: dict):
    intensity = state.get("extinction_intensity", 0)
    if intensity <= 0:
        return
    pen.penup()
    pen.goto(EARTH_CENTER_X, EARTH_CENTER_Y - EARTH_RADIUS)
    pen.pendown()
    dark = (int(40 * intensity), int(35 * intensity), int(30 * intensity))
    pen.fillcolor(rgb_to_hex(dark))
    pen.color(rgb_to_hex(dark))
    pen.begin_fill()
    pen.circle(EARTH_RADIUS)
    pen.end_fill()


def draw_moon(pen, state: dict):
    if not state.get("moon_visible"):
        return
    angle = state.get("moon_angle", 0)
    mx = EARTH_CENTER_X + MOON_ORBIT_RADIUS * math.cos(angle)
    my = EARTH_CENTER_Y - MOON_ORBIT_RADIUS * math.sin(angle)
    pen.penup()
    pen.goto(mx, my - MOON_RADIUS)
    pen.pendown()
    pen.fillcolor("#e8e8e8")
    pen.color("#c0c0c0")
    pen.begin_fill()
    pen.circle(MOON_RADIUS)
    pen.end_fill()


def draw_life_meter(pen, state: dict):
    x, y = LIFE_METER_X, LIFE_METER_Y
    width, height = 18, 160
    label_x = x + width + 25
    spacing = 35
    base_y = y
    complexity = state["life_complexity"]

    # Bar background
    pen.penup()
    pen.goto(x, y)
    pen.setheading(0)
    pen.pendown()
    pen.color("#2a2a2a")
    pen.fillcolor("#1a1a1a")
    pen.begin_fill()
    pen.forward(width)
    pen.left(90)
    pen.forward(height)
    pen.left(90)
    pen.forward(width)
    pen.left(90)
    pen.forward(height)
    pen.end_fill()

    # Bar fill
    fill_height = height * complexity
    pen.penup()
    pen.goto(x, y)
    pen.setheading(0)
    pen.pendown()
    pen.color("#4ade80")
    pen.fillcolor("#22c55e")
    pen.begin_fill()
    pen.forward(width)
    pen.left(90)
    pen.forward(fill_height)
    pen.left(90)
    pen.forward(width)
    pen.left(90)
    pen.forward(fill_height)
    pen.end_fill()

    # Labels: base_y = meter_bottom, y = base_y + i * spacing (draw text after rectangles)
    pen.penup()
    for i, (val, label) in enumerate(LIFE_METER_LABELS):
        ly = base_y + i * spacing
        pen.goto(label_x, ly)
        pen.pencolor("#ffffff")
        pen.fillcolor("#ffffff")
        pen.write(label, font=("Arial", 10, "normal"), move=False)
    pen.goto(label_x, base_y + len(LIFE_METER_LABELS) * spacing)
    pen.write("Life", font=("Arial", 11, "bold"), move=False)


# Epoch display names (avoid floating labels in starfield)
EPOCH_DISPLAY_NAMES = {
    "formation": "Molten Earth",
    "moon_impact": "Moon Impact",
    "cooling": "Cooling",
    "oceans": "Oceans Form",
    "microbial_life": "Microbial Life",
    "oxygenation": "Oxygenation",
    "snowball_earth": "Snowball Earth",
    "complex_life": "Complex Life",
    "dinosaurs": "Dinosaurs",
    "kt_extinction": "K-T Extinction",
    "modern": "Modern",
}


def draw_timeline(pen, state: dict):
    y = TIMELINE_Y
    x_start = -SCREEN_WIDTH // 2 + TIMELINE_MARGIN
    bar_width = SCREEN_WIDTH - 2 * TIMELINE_MARGIN
    sim_t = state["sim_t"]

    pen.penup()
    pen.goto(x_start, y)
    pen.pendown()
    pen.color("#2a2a2a")
    pen.fillcolor("#151515")
    pen.begin_fill()
    pen.forward(bar_width)
    pen.left(90)
    pen.forward(22)
    pen.left(90)
    pen.forward(bar_width)
    pen.left(90)
    pen.forward(22)
    pen.end_fill()

    eras = get_timeline_eras()
    for t0, t1, name in eras:
        pen.penup()
        pen.goto(x_start + bar_width * (t0 + t1) / 2 - len(name) * 3, y - 16)
        pen.pencolor("#ffffff")
        pen.write(name, font=("Arial", 10, "normal"), move=False)

    marker_x = x_start + bar_width * sim_t
    pen.penup()
    pen.goto(marker_x, y)
    pen.pendown()
    pen.color("#f59e0b")
    pen.pensize(3)
    pen.setheading(270)
    pen.forward(28)
    pen.pensize(1)

    # Epoch label near timeline (not floating in starfield)
    epoch = state["epoch"]
    display_name = EPOCH_DISPLAY_NAMES.get(epoch, epoch.replace("_", " ").title())
    pen.penup()
    pen.goto(0, y - 42)
    pen.pencolor("#ffffff")
    pen.write(display_name, align="center", font=("Arial", 14, "bold"), move=False)


def draw_spin_indicator(pen, state: dict):
    if not state.get("spinning", True):
        pen.penup()
        pen.goto(SCREEN_WIDTH // 2 - 90, TIMELINE_Y - 42)
        pen.pencolor("#ffffff")
        pen.write("(paused spin)", font=("Arial", 10, "normal"), move=False)


def render_frame(pen, state: dict):
    pen.clear()
    draw_starfield(pen)
    draw_earth_base(pen, state)
    draw_oceans(pen, state)
    draw_earth_rim(pen, state)
    draw_continents(pen, state)
    draw_ice(pen, state)
    draw_event_overlays(pen, state)
    draw_moon(pen, state)
    draw_life_meter(pen, state)
    draw_timeline(pen, state)
    draw_spin_indicator(pen, state)

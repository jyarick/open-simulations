"""
Deep Time Earth — Rendering: projection, globe, atmosphere, overlays, continents, clouds.

Projection: Equirectangular lat/lon → screen (x,y). Points with cos(lat)*cos(lon_rot) > 0
are on the front hemisphere and visible. Render order: stars → moon → earth → atmosphere
→ terminator → event overlay → continents → clouds.
"""

import math
import config
from data import OVERLAY_STYLES, wrap_lon


# =============================================================================
# PROJECTION
# =============================================================================
def project_point(lat_deg, lon_deg, rot_deg, earth_radius=None):
    """Map (lat, lon) to screen. Returns (x, y, visible). Visible = front hemisphere."""
    if earth_radius is None:
        earth_radius = config.EARTH_RADIUS
    # Equirectangular: x = R*cos(lat)*sin(lon), y = R*sin(lat)
    # Visible = front hemisphere (cos(lat)*cos(lon_rot) > 0)
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    rot = math.radians(rot_deg)
    lon_rot = lon + rot
    x = earth_radius * math.cos(lat) * math.sin(lon_rot)
    y = earth_radius * math.sin(lat)
    visible = math.cos(lat) * math.cos(lon_rot) > 0
    return config.EARTH_CENTER_X + x, config.EARTH_CENTER_Y + y, visible


# =============================================================================
# DRAW HELPERS
# =============================================================================
def draw_filled_circle(pen, cx, cy, radius, fill_color, outline_color=None):
    pen.penup()
    pen.goto(cx, cy - radius)
    pen.setheading(0)
    pen.pendown()
    pen.fillcolor(fill_color)
    if outline_color is not None:
        pen.pencolor(outline_color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()


def draw_star(pen, x, y, size=2):
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    pen.dot(size, config.STAR_COLOR)


# =============================================================================
# GLOBE LAYERS
# =============================================================================
def draw_earth_disk(pen, state):
    draw_filled_circle(
        pen, config.EARTH_CENTER_X, config.EARTH_CENTER_Y, config.EARTH_RADIUS,
        state.earth_color
    )


def draw_atmosphere(pen, state):
    cx, cy = config.EARTH_CENTER_X, config.EARTH_CENTER_Y
    r = config.EARTH_RADIUS
    r_outer = r + config.ATMOSPHERE_HALO_RADIUS

    halo_color = state.atmosphere_tint or state.atmosphere_color
    pen.penup()
    pen.goto(cx, cy - r_outer)
    pen.setheading(0)
    pen.pendown()
    pen.fillcolor(halo_color)
    pen.begin_fill()
    pen.circle(r_outer)
    pen.end_fill()
    pen.fillcolor(state.earth_color)
    pen.penup()
    pen.goto(cx, cy - r)
    pen.setheading(0)
    pen.pendown()
    pen.begin_fill()
    pen.circle(r)
    pen.end_fill()


def draw_day_night_terminator(pen, state):
    """Softer night side; smooth terminator; faint visibility preserved."""
    cx, cy = config.EARTH_CENTER_X, config.EARTH_CENTER_Y
    r = config.EARTH_RADIUS
    la = math.radians(state.light_angle)
    n = config.TERMINATOR_SEGMENTS

    pen.fillcolor(config.NIGHT_SIDE_COLOR)
    pen.penup()
    pen.goto(cx, cy - r)
    pen.setheading(0)
    pen.pendown()
    pen.begin_fill()
    pen.circle(r)
    pen.end_fill()

    points = [(cx, cy)]
    for i in range(n + 1):
        a = la - math.pi / 2 + (math.pi * i / n)
        px = cx + r * math.cos(a)
        py = cy + r * math.sin(a)
        points.append((px, py))
    points.append((cx, cy))

    pen.fillcolor(state.earth_color)
    pen.penup()
    pen.goto(points[0])
    pen.pendown()
    pen.begin_fill()
    for px, py in points[1:]:
        pen.goto(px, py)
    pen.end_fill()


def draw_event_overlay(pen, state):
    if not state.active_event or state.smoothed_overlay_intensity < config.EVENT_OVERLAY_MIN_VISIBLE:
        return
    ev = state.active_event
    style_name = ev.get("overlay_style", ev["event_type"])
    style = OVERLAY_STYLES.get(style_name, {})
    if not style or not style.get("surface_color"):
        return

    cx, cy = config.EARTH_CENTER_X, config.EARTH_CENTER_Y
    r = config.EARTH_RADIUS

    draw_filled_circle(pen, cx, cy, r, style["surface_color"])

    if style.get("ring") and style.get("ring_color"):
        ring_size = style.get("ring_size", 6)
        pen.penup()
        pen.goto(cx, cy - r - ring_size)
        pen.setheading(0)
        pen.pencolor(style["ring_color"])
        pen.pensize(max(2, int(ring_size * 0.5)))
        pen.pendown()
        pen.circle(r + ring_size)
        pen.pensize(1)


def draw_continents(pen, state, continents):
    """Use continent_contrast during events so land stays readable on overlays."""
    if state.continent_contrast and state.smoothed_overlay_intensity > 0.1:
        color = state.continent_contrast
    else:
        color = state.surface_tint or state.continent_color

    dot_size = config.CONTINENT_DOT_SIZE
    total_visible = 0
    for c in continents:
        for lat_off, lon_off in c["offsets"]:
            lat = max(-89, min(89, c["center_lat"] + lat_off))
            lon = wrap_lon(c["center_lon"] + lon_off)
            sx, sy, visible = project_point(lat, lon, state.rotation_angle)
            if visible:
                total_visible += 1
                pen.penup()
                pen.goto(sx, sy)
                pen.pendown()
                pen.dot(dot_size, color)
    return total_visible


def draw_clouds(pen, state, clouds):
    """Softer, subtler cloud layer; density and color vary by epoch."""
    base = config.CLOUD_BASE_COLOR
    if state.cloud_density < 0.4:
        cloud_color = "gainsboro"
    elif state.cloud_density < 0.7:
        cloud_color = "whitesmoke"
    else:
        cloud_color = base
    if state.atmosphere_tint and state.smoothed_overlay_intensity > 0.3:
        cloud_color = "ghostwhite"

    n = max(15, int(len(clouds) * state.cloud_density * config.CLOUD_DENSITY_SCALE))
    dot_size = config.CLOUD_DOT_SIZE
    for lat, lon in clouds[:n]:
        lat = max(-89, min(89, lat))
        lon = wrap_lon(lon)
        sx, sy, visible = project_point(lat, lon, state.cloud_angle)
        if visible:
            pen.penup()
            pen.goto(sx, sy)
            pen.pendown()
            pen.dot(dot_size, cloud_color)


# =============================================================================
# SCENE — Render order: stars → moon → earth disk → atmosphere → terminator → overlay → continents → clouds
# =============================================================================
def get_moon_position(state):
    mx = config.EARTH_CENTER_X + config.MOON_ORBIT_RADIUS * math.cos(state.moon_angle)
    my = config.EARTH_CENTER_Y + config.MOON_ORBIT_RADIUS * math.sin(state.moon_angle)
    return mx, my


def draw_scene(pen, screen, state, stars, continents, clouds):
    pen.clear()

    for x, y, size in stars:
        draw_star(pen, x, y, size)

    mx, my = get_moon_position(state)
    draw_filled_circle(pen, mx, my, config.MOON_RADIUS, config.MOON_COLOR)

    draw_earth_disk(pen, state)
    draw_atmosphere(pen, state)
    draw_day_night_terminator(pen, state)
    draw_event_overlay(pen, state)

    total_visible = draw_continents(pen, state, continents)
    draw_clouds(pen, state, clouds)

    return total_visible

"""
Deep Time Earth — UI: life meter, timeline, captions, intro, help, debug overlay.
"""

import config


# =============================================================================
# INTRO — Startup title/subtitle overlay
# =============================================================================
def draw_intro_overlay(pen, state):
    """Staged title then subtitle; fades into sim when intro_phase reaches 2."""
    pen.penup()
    pen.goto(0, 20)
    pen.pencolor("white")
    pen.write(
        config.INTRO_TITLE,
        font=("Courier", 22, "bold"),
        align="center",
    )
    if state.intro_phase >= 1:
        pen.sety(pen.ycor() - 28)
        pen.pencolor("gray85")
        pen.write(
            config.INTRO_SUBTITLE,
            font=("Courier", 12, "normal"),
            align="center",
        )


# =============================================================================
# LIFE METER
# =============================================================================
def draw_life_meter(pen, life_complexity):
    x = config.LIFE_METER_LEFT
    y_bottom = config.LIFE_METER_BOTTOM
    w = config.LIFE_METER_WIDTH
    h = config.LIFE_METER_HEIGHT

    pen.penup()
    pen.goto(x, y_bottom)
    pen.pendown()
    pen.pencolor("gray40")
    pen.pensize(1)
    for dx, dy in [(w, 0), (0, h), (-w, 0), (0, -h)]:
        pen.goto(pen.xcor() + dx, pen.ycor() + dy)

    fill_h = (h - 4) * max(0, min(1, life_complexity))
    if fill_h > 0:
        pen.penup()
        pen.goto(x + 2, y_bottom + 2)
        pen.pendown()
        pen.fillcolor("limegreen")
        pen.begin_fill()
        pen.goto(x + w - 2, y_bottom + 2)
        pen.goto(x + w - 2, y_bottom + 2 + fill_h)
        pen.goto(x + 2, y_bottom + 2 + fill_h)
        pen.goto(x + 2, y_bottom + 2)
        pen.end_fill()

    stages = ["none", "microbes", "simple", "complex", "modern"]
    pen.penup()
    pen.pencolor("gray55")
    for i, label in enumerate(stages):
        ly = y_bottom + (i + 0.5) * (h / 5)
        pen.goto(x - 52, ly - 4)
        pen.write(label, font=("Courier", 7, "normal"))


# =============================================================================
# TIMELINE — Clear current-time marker, epoch segments
# =============================================================================
def draw_timeline(pen, state):
    x_left = config.TIMELINE_LEFT
    x_right = config.TIMELINE_RIGHT
    y = config.TIMELINE_Y
    h = config.TIMELINE_HEIGHT
    t = state.sim_t % 1.0
    full_w = x_right - x_left
    bar_w = full_w - 4

    pen.penup()
    pen.goto(x_left, y)
    pen.pendown()
    pen.pencolor("gray40")
    pen.pensize(1)
    for dx, dy in [(full_w, 0), (0, h), (-full_w, 0), (0, -h)]:
        pen.goto(pen.xcor() + dx, pen.ycor() + dy)

    fill_w = bar_w * t
    if fill_w > 0:
        pen.penup()
        pen.goto(x_left + 2, y + 2)
        pen.pendown()
        pen.fillcolor("gray35")
        pen.begin_fill()
        pen.goto(x_left + 2 + fill_w, y + 2)
        pen.goto(x_left + 2 + fill_w, y + h - 2)
        pen.goto(x_left + 2, y + h - 2)
        pen.goto(x_left + 2, y + 2)
        pen.end_fill()

    marker_x = x_left + 2 + min(fill_w, bar_w - 1)
    pen.penup()
    pen.goto(marker_x, y + 2)
    pen.pendown()
    pen.pencolor("white")
    pen.pensize(config.TIMELINE_MARKER_WIDTH)
    pen.goto(marker_x, y + h - 2)
    pen.pensize(1)

    # Era labels — key divisions (Hadean, Proterozoic, Cenozoic)
    pen.penup()
    pen.pencolor("gray60")
    labels = [(0.075, "Hadean"), (0.44, "Proterozoic"), (0.925, "Cenozoic")]
    for frac, label in labels:
        lx = x_left + 2 + bar_w * frac
        pen.goto(lx - len(label) * 3, y - 22)
        pen.write(label, font=("Courier", 7, "normal"))


# =============================================================================
# CAPTIONS — Clear hierarchy, stable placement
# =============================================================================
def draw_captions(pen, state):
    """Caption hierarchy: primary (epoch/event), secondary (theme), tertiary (detail)."""
    pen.penup()
    pen.goto(0, config.CAPTION_Y_PRIMARY)
    pen.pencolor(config.CAPTION_PRIMARY_COLOR)
    pen.write(
        state.caption_primary,
        font=("Courier", config.CAPTION_PRIMARY_SIZE, "bold"),
        align="center",
    )
    pen.sety(pen.ycor() - config.CAPTION_LINE_SPACING)
    pen.pencolor(config.CAPTION_SECONDARY_COLOR)
    pen.write(
        state.caption_secondary,
        font=("Courier", config.CAPTION_SECONDARY_SIZE, "normal"),
        align="center",
    )
    pen.sety(pen.ycor() - config.CAPTION_LINE_SPACING)
    pen.pencolor(config.CAPTION_TERTIARY_COLOR)
    pen.write(
        state.caption_tertiary,
        font=("Courier", config.CAPTION_TERTIARY_SIZE, "normal"),
        align="center",
    )


# =============================================================================
# HELP OVERLAY — Toggleable legend
# =============================================================================
def draw_paused_indicator(pen):
    """Subtle 'Paused' badge when simulation is paused."""
    pen.penup()
    pen.goto(0, 260)
    pen.pencolor("gray60")
    pen.write("Paused", font=("Courier", 10, "normal"), align="center")


def draw_help_overlay(pen):
    """Legend: what the simulation shows and keyboard controls."""
    x, y = config.HELP_OVERLAY_X, config.HELP_OVERLAY_Y
    pen.penup()
    pen.goto(x, y)
    pen.pencolor("gray70")
    lines = [
        "Deep Time Earth",
        "────────────────",
        "Shows Earth evolving through",
        "4.5 billion years of geologic time.",
        "",
        "Timeline  — Geologic eras (Hadean → Cenozoic)",
        "Life meter — Biosphere complexity",
        "Captions   — Current epoch or event",
        "",
        "Controls",
        "  Space   Pause / Resume",
        "  r       Restart",
        "  s       Cycle speed",
        "  + / -   Speed up / down",
        "  d       Debug overlay",
        "  h       This help",
    ]
    for line in lines:
        pen.write(line, font=("Courier", config.HELP_FONT_SIZE, "normal"))
        pen.sety(pen.ycor() - config.HELP_FONT_SIZE - 2)


# =============================================================================
# DEBUG OVERLAY — Expanded for development
# =============================================================================
def draw_debug_overlay(pen, state, total_visible, total_points):
    pen.penup()
    pen.goto(config.DEBUG_OVERLAY_X, config.DEBUG_OVERLAY_Y)
    pen.pencolor("gray50")
    ev_name = state.active_event["name"] if state.active_event else "none"
    status = []
    if state.intro_phase < 2:
        status.append("intro")
    if state.paused:
        status.append("paused")
    if state.loop_holding:
        status.append("loop_hold")
    status_str = ", ".join(status) if status else "running"

    lines = [
        f"sim_t: {state.sim_t:.3f}",
        f"status: {status_str}",
        f"epoch: {state.epoch['name']}",
        f"event: {ev_name}",
        f"life: {state.smoothed_life:.2f}",
        f"overlay: {state.smoothed_overlay_intensity:.2f}",
        f"light: {state.light_angle:.1f}°",
        f"pts: {total_points} vis: {total_visible}",
        f"speed: {state.speed_multiplier}x [s]",
    ]
    for line in lines:
        pen.write(line, font=("Courier", config.DEBUG_FONT_SIZE, "normal"))
        pen.sety(pen.ycor() - config.DEBUG_LINE_SPACING)

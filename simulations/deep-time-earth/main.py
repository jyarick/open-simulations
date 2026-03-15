"""
Deep Time Earth — Main entry point.

Run: python main.py
Flow: main() → setup screen/pen → draw_frame (timer loop)
Each frame: update_simulation → update_visual_state → update_smoothed_state → draw_scene → draw UI
"""

import random
import turtle

import config
from data import create_continent, generate_cloud_points, generate_stars, reset_continents
from simulation import SimulationState, update_simulation, update_visual_state, update_smoothed_state
from render import draw_scene
from ui import (
    draw_life_meter,
    draw_timeline,
    draw_captions,
    draw_intro_overlay,
    draw_help_overlay,
    draw_paused_indicator,
    draw_debug_overlay,
)

# =============================================================================
# GLOBAL RUNTIME (minimal)
# =============================================================================
state = SimulationState()
continents = []
clouds = []
stars = []
debug_mode = not config.PRESENTATION_MODE
help_mode = False

# Apply debug-mode defaults (slower initial speed)
if not config.PRESENTATION_MODE:
    state.speed_multiplier = config.DEBUG_INITIAL_SPEED


def cycle_speed():
    levels = config.SPEED_LEVELS
    try:
        idx = levels.index(state.speed_multiplier)
    except ValueError:
        idx = 0
    state.speed_multiplier = levels[(idx + 1) % len(levels)]


def speed_up():
    levels = config.SPEED_LEVELS
    try:
        idx = levels.index(state.speed_multiplier)
    except ValueError:
        idx = 0
    state.speed_multiplier = levels[min(idx + 1, len(levels) - 1)]


def speed_down():
    levels = config.SPEED_LEVELS
    try:
        idx = levels.index(state.speed_multiplier)
    except ValueError:
        idx = 0
    state.speed_multiplier = levels[max(idx - 1, 0)]


def toggle_debug():
    global debug_mode
    debug_mode = not debug_mode


def toggle_help():
    global help_mode
    help_mode = not help_mode


def toggle_pause():
    state.paused = not state.paused


def restart_sim():
    """Reset to intro and beginning of timeline."""
    state.intro_phase = 0
    state.intro_timer = 0.0
    state.sim_t = 0.0
    state.loop_holding = False
    state.loop_hold_timer = 0.0
    state.paused = False
    state.smoothed_life = 0.0
    state.smoothed_overlay_intensity = 0.0
    reset_continents(continents)


def draw_frame(pen, screen):
    update_simulation(state, continents)
    update_visual_state(state)
    update_smoothed_state(state)

    total_visible = draw_scene(pen, screen, state, stars, continents, clouds)

    draw_life_meter(pen, state.smoothed_life)
    draw_timeline(pen, state)
    if state.intro_phase < 2:
        draw_intro_overlay(pen, state)
    else:
        draw_captions(pen, state)

    if state.paused:
        draw_paused_indicator(pen)
    if help_mode:
        draw_help_overlay(pen)
    if debug_mode:
        total_points = sum(len(c["offsets"]) for c in continents)
        draw_debug_overlay(pen, state, total_visible, total_points)

    screen.update()
    screen.ontimer(lambda: draw_frame(pen, screen), config.FRAME_DELAY_MS)


def main():
    global state, continents, clouds, stars

    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.bgcolor("black")
    screen.title("Deep Time Earth")
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)

    random.seed(42)
    stars = generate_stars(42, 90)

    continents = [
        create_continent(10, 0, 14, 300, 1, drift_lon=0.008, drift_lat=0.001),
        create_continent(-15, 120, 12, 260, 2, drift_lon=-0.006, drift_lat=-0.0005),
        create_continent(25, -90, 10, 220, 3, drift_lon=0.01, drift_lat=0.002),
        create_continent(-30, 45, 8, 180, 4, drift_lon=-0.007, drift_lat=0.001),
        create_continent(5, 170, 11, 220, 5, drift_lon=0.005, drift_lat=-0.001),
    ]

    clouds = generate_cloud_points(100, 0.8)

    update_visual_state(state)

    screen.onkey(cycle_speed, "s")
    screen.onkey(speed_up, "plus")
    screen.onkey(speed_up, "equal")
    screen.onkey(speed_down, "minus")
    screen.onkey(toggle_debug, "d")
    screen.onkey(toggle_help, "h")
    screen.onkey(toggle_pause, "p")
    screen.onkey(toggle_pause, "space")
    screen.onkey(restart_sim, "r")
    screen.listen()

    screen.ontimer(lambda: draw_frame(pen, screen), 0)
    turtle.done()


if __name__ == "__main__":
    main()

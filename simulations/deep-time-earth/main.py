"""
Deep Time Earth — Planetary Evolution Time-Lapse

Main simulation loop. Two clocks: planet rotation and deep time.
"""

import time
import turtle

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FRAME_TIME,
    ROTATION_SPEED,
    MIN_V_SIM,
    MAX_V_SIM,
    MOON_ORBIT_SPEED,
)
from state import create_initial_state, reset_state
from timeline import get_current_epoch, get_epoch_progress
from earth import create_continents, update_continent_drift, update_epoch_state
from life import get_target_complexity, update_life_complexity
from events import update_events, get_extinction_dip
from palette import get_epoch_colors
from renderer import render_frame


def setup_screen():
    screen = turtle.Screen()
    screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.setworldcoordinates(
        -SCREEN_WIDTH // 2, -SCREEN_HEIGHT // 2,
        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
    )
    screen.bgcolor("#0a0a12")
    screen.tracer(0)
    screen.title("Deep Time Earth")
    return screen


def setup_pen():
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()
    return pen


def update_simulation_time(state: dict):
    if state["paused"]:
        return
    state["sim_t"] += state["v_sim"]
    state["sim_t"] = min(1.0, state["sim_t"])
    state["frame_count"] += 1


def update_rotation(state: dict):
    if not state.get("spinning", True):
        return
    state["rotation_angle"] += ROTATION_SPEED
    if state["rotation_angle"] >= 360:
        state["rotation_angle"] -= 360
    if state["moon_visible"]:
        state["moon_angle"] += MOON_ORBIT_SPEED


def update_epoch_from_time(state: dict):
    state["epoch"] = get_current_epoch(state["sim_t"])
    state["epoch_progress"] = get_epoch_progress(state["sim_t"])
    _, _, _, _, atm = get_epoch_colors(state["epoch"])
    state["atmosphere_tint"] = atm


def update_life(state: dict):
    target = get_target_complexity(state["sim_t"])
    dip = get_extinction_dip(state)
    state["life_complexity"] = update_life_complexity(
        state["life_complexity"], target, 1.0, dip
    )


def main():
    screen = setup_screen()
    pen = setup_pen()

    state = create_initial_state()
    state["continents"] = create_continents()

    def on_up():
        state["v_sim"] = min(MAX_V_SIM, state["v_sim"] * 1.5)

    def on_down():
        state["v_sim"] = max(MIN_V_SIM, state["v_sim"] / 1.5)

    def on_space():
        state["paused"] = not state["paused"]

    def on_s():
        state["spinning"] = not state.get("spinning", True)

    screen.onkey(on_up, "Up")
    screen.onkey(on_down, "Down")
    screen.onkey(on_space, "space")
    screen.onkey(on_s, "s")
    screen.onkey(on_s, "S")

    def on_r():
        reset_state(state)
        state["continents"] = create_continents()
        render_frame(pen, state)

    screen.onkey(on_r, "r")
    screen.listen()

    running = True
    while running:
        update_simulation_time(state)
        update_rotation(state)
        update_epoch_from_time(state)
        update_epoch_state(state)
        update_continent_drift(state)
        update_events(state)
        update_life(state)

        render_frame(pen, state)

        try:
            screen.update()
        except turtle.Terminator:
            running = False

        time.sleep(FRAME_TIME)

    turtle.bye()


if __name__ == "__main__":
    main()

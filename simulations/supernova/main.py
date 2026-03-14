"""
Entry point: create screen, initialize simulation, start update loop.
"""
from turtle import Screen

import config
from engine import Simulation


def main() -> None:
    screen = Screen()
    screen.setup(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    screen.bgcolor(config.BACKGROUND_COLOR)
    screen.title("Supernova — Core Collapse Simulation")
    screen.tracer(0, 0)

    sim = Simulation(screen)
    sim.run()

    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    main()

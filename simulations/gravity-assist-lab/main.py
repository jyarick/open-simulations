"""
Gravity Assist Lab - Main entry point.
Simulates gravitational slingshot (gravity assist) mechanics.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from config.constants import (
    G,
    STAR_MASS,
    PLANET_MASS,
    PLANET_ORBIT_RADIUS,
    PLANET_ORBIT_SPEED,
    SPACECRAFT_MASS,
    SIMULATION_DT,
    TRAIL_LENGTH,
    VIEW_SCALE,
)

from simulation.universe import Universe
from visuals.renderer import Renderer
from visuals.trails import TrailManager

# =============================================================================
# TUNABLE PARAMETERS - Change these to explore different scenarios
# =============================================================================

# Planet
planet_mass = 1e-5
planet_orbit_radius = 1.0
planet_orbit_speed = 1.0

# Spacecraft initial conditions
# Entry angle: degrees from +x axis (0 = right, 90 = up)
# Speed relative to orbital velocity scale
spacecraft_initial_speed = 0.85
spacecraft_entry_angle = 15.0  # degrees - slight upward angle for good assist
spacecraft_start_x = -2.0  # Start far left
spacecraft_start_y = -0.3  # Slightly below center

# Simulation
simulation_dt = 0.002  # Smaller = more accurate, slower
frames_per_second = 60
trail_length = TRAIL_LENGTH

# =============================================================================
# Setup
# =============================================================================


def make_initial_velocity() -> np.ndarray:
    """Compute initial velocity from speed and entry angle."""
    angle_rad = math.radians(spacecraft_entry_angle)
    return spacecraft_initial_speed * np.array([np.cos(angle_rad), np.sin(angle_rad)])


def main() -> None:
    # Initial conditions
    spacecraft_position = np.array([spacecraft_start_x, spacecraft_start_y])
    spacecraft_velocity = make_initial_velocity()

    # Create universe and visuals
    universe = Universe(
        star_mass=STAR_MASS,
        planet_mass=planet_mass,
        planet_orbit_radius=planet_orbit_radius,
        planet_orbit_speed=planet_orbit_speed,
        spacecraft_position=spacecraft_position,
        spacecraft_velocity=spacecraft_velocity,
        dt=simulation_dt,
    )
    trail = TrailManager(max_length=trail_length)
    renderer = Renderer(
        view_scale=VIEW_SCALE,
        show_velocity_arrows=True,
        show_gravity_rings=True,
        velocity_arrow_scale=0.12,
    )

    # Track speeds for reporting and visualization
    encounter_radius = 1.5  # Distance threshold for "in encounter"
    initial_speed = universe.spacecraft.speed
    max_speed = initial_speed
    incoming_speed = initial_speed
    outgoing_speed = None
    in_encounter = False
    had_encounter = False

    renderer.setup_figure()

    def init_anim() -> None:
        trail.add(universe.spacecraft.position.copy(), universe.spacecraft.speed)

    def update(frame: int) -> None:
        nonlocal incoming_speed, outgoing_speed, in_encounter, had_encounter, max_speed

        # Run multiple physics steps per frame for smoother motion
        steps_per_frame = max(1, int(1.0 / (frames_per_second * simulation_dt)))
        steps_per_frame = min(steps_per_frame, 10)

        for _ in range(steps_per_frame):
            dist = np.linalg.norm(
                universe.spacecraft.position - universe.planet.position
            )
            if dist < encounter_radius:
                if not in_encounter:
                    incoming_speed = universe.spacecraft.speed
                in_encounter = True
                had_encounter = True
            else:
                if in_encounter:
                    outgoing_speed = universe.spacecraft.speed
                in_encounter = False

            universe.step()
            max_speed = max(max_speed, universe.spacecraft.speed)
            trail.add(universe.spacecraft.position.copy(), universe.spacecraft.speed)

        trail_points, trail_speeds = trail.get_points_and_speeds()
        speed_min = initial_speed
        speed_max = max(max_speed, initial_speed * 1.01)

        # Render
        renderer.render_frame(
            star_pos=universe.star.position,
            planet_pos=universe.planet.position,
            spacecraft_pos=universe.spacecraft.position,
            spacecraft_vel=universe.spacecraft.velocity,
            trail_points=trail_points,
            trail_speeds=trail_speeds,
            speed_min=speed_min,
            speed_max=speed_max,
            current_speed=universe.spacecraft.speed,
            initial_speed=initial_speed,
            max_speed=max_speed,
        )
        return []

    # Run animation
    anim = FuncAnimation(
        renderer.fig,
        update,
        init_func=init_anim,
        frames=2000,
        interval=1000 / frames_per_second,
        blit=False,
    )

    plt.tight_layout()
    plt.show()

    # Print results after window closes
    final_speed = universe.spacecraft.speed
    if outgoing_speed is None:
        outgoing_speed = final_speed if had_encounter else initial_speed

    print("\n" + "=" * 50)
    print("GRAVITY ASSIST LAB - Results")
    print("=" * 50)
    print(f"Incoming speed:  {incoming_speed:.4f}")
    print(f"Outgoing speed: {outgoing_speed:.4f}")
    print(f"Speed change:    {outgoing_speed - incoming_speed:+.4f}")
    ke_in = 0.5 * SPACECRAFT_MASS * incoming_speed**2
    ke_out = 0.5 * SPACECRAFT_MASS * outgoing_speed**2
    print(f"Energy change:   {ke_out - ke_in:+.4f}")
    print("=" * 50)


if __name__ == "__main__":
    main()

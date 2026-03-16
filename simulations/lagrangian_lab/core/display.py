"""
Display utilities for Lagrangian Mechanics Lab.

Provides helpers for plotting and animation (used by the notebook).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle


def animate_pendulum(ax, t, theta, l, x_pivot=0.0, y_pivot=0.0):
    """
    Create a matplotlib animation of a pendulum.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to draw on.
    t : array-like
        Time array.
    theta : array-like
        Angular displacement (rad) at each time.
    l : float
        Pendulum length.
    x_pivot, y_pivot : float
        Pivot position (default 0, 0).

    Returns
    -------
    matplotlib.animation.FuncAnimation
    """
    theta = np.asarray(theta)
    t = np.asarray(t)

    # Bob position: x = l*sin(theta), y = -l*cos(theta) (y down from pivot)
    x_bob = x_pivot + l * np.sin(theta)
    y_bob = y_pivot - l * np.cos(theta)

    # Set axis limits with padding
    margin = l * 0.2
    ax.set_xlim(x_pivot - l - margin, x_pivot + l + margin)
    ax.set_ylim(y_pivot - l - margin, y_pivot + margin)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Pivot point
    pivot = ax.plot(x_pivot, y_pivot, "ko", markersize=10)[0]

    # Rod (line from pivot to bob)
    rod_line, = ax.plot([], [], "b-", linewidth=2)

    # Bob (circle)
    bob_radius = l * 0.05
    bob = Circle((0, 0), bob_radius, color="red", zorder=10)
    ax.add_patch(bob)

    def init():
        rod_line.set_data([], [])
        bob.center = (0, 0)
        return rod_line, bob

    def update(frame):
        xb, yb = x_bob[frame], y_bob[frame]
        rod_line.set_data([x_pivot, xb], [y_pivot, yb])
        bob.center = (xb, yb)
        return rod_line, bob

    anim = FuncAnimation(
        ax.get_figure(),
        update,
        frames=len(t),
        init_func=init,
        blit=True,
        interval=1000 * (t[-1] - t[0]) / len(t) if len(t) > 1 else 50,
    )
    return anim


def animate_mass_spring(ax, t, x, x_wall=0.0):
    """
    Create a matplotlib animation of a mass-spring oscillator.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to draw on.
    t : array-like
        Time array.
    x : array-like
        Mass position at each time.
    x_wall : float
        Wall position (default 0).

    Returns
    -------
    matplotlib.animation.FuncAnimation
    """
    x = np.asarray(x)
    t = np.asarray(t)

    # Mass position: (x, 0)
    x_mass = x
    y_mass = np.zeros_like(x)

    # Axis limits
    x_min = min(x_wall, x.min()) - 0.5
    x_max = max(x_wall, x.max()) + 0.5
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Wall (vertical line at x_wall)
    ax.axvline(x=x_wall, color="k", linewidth=3)

    # Spring (line from wall to mass)
    spring_line, = ax.plot([], [], "b-", linewidth=2)

    # Mass (circle)
    mass_radius = 0.08
    mass = Circle((0, 0), mass_radius, color="red", zorder=10)
    ax.add_patch(mass)

    def init():
        spring_line.set_data([], [])
        mass.center = (0, 0)
        return spring_line, mass

    def update(frame):
        xm, ym = x_mass[frame], y_mass[frame]
        spring_line.set_data([x_wall, xm], [0, ym])
        mass.center = (xm, ym)
        return spring_line, mass

    anim = FuncAnimation(
        ax.get_figure(),
        update,
        frames=len(t),
        init_func=init,
        blit=True,
        interval=1000 * (t[-1] - t[0]) / len(t) if len(t) > 1 else 50,
    )
    return anim


def animate_double_pendulum(ax, t, theta_1, theta_2, l1, l2, x_pivot=0.0, y_pivot=0.0):
    """
    Create a matplotlib animation of a double pendulum.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to draw on.
    t : array-like
        Time array.
    theta_1, theta_2 : array-like
        Angular displacements (rad) at each time.
    l1, l2 : float
        Rod lengths.
    x_pivot, y_pivot : float
        Pivot position (default 0, 0).

    Returns
    -------
    matplotlib.animation.FuncAnimation
    """
    theta_1 = np.asarray(theta_1)
    theta_2 = np.asarray(theta_2)
    t = np.asarray(t)

    # Positions from angles
    x1 = x_pivot + l1 * np.sin(theta_1)
    y1 = y_pivot - l1 * np.cos(theta_1)
    x2 = x1 + l2 * np.sin(theta_2)
    y2 = y1 - l2 * np.cos(theta_2)

    # Axis limits
    total_l = l1 + l2
    margin = total_l * 0.2
    ax.set_xlim(x_pivot - total_l - margin, x_pivot + total_l + margin)
    ax.set_ylim(y_pivot - total_l - margin, y_pivot + margin)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Pivot
    ax.plot(x_pivot, y_pivot, "ko", markersize=10)

    # Rods
    rod1_line, = ax.plot([], [], "b-", linewidth=2)
    rod2_line, = ax.plot([], [], "b-", linewidth=2)

    # Masses
    r1, r2 = total_l * 0.04, total_l * 0.035
    mass1 = Circle((0, 0), r1, color="red", zorder=10)
    mass2 = Circle((0, 0), r2, color="darkred", zorder=10)
    ax.add_patch(mass1)
    ax.add_patch(mass2)

    def init():
        rod1_line.set_data([], [])
        rod2_line.set_data([], [])
        mass1.center = (0, 0)
        mass2.center = (0, 0)
        return rod1_line, rod2_line, mass1, mass2

    def update(frame):
        x1f, y1f = x1[frame], y1[frame]
        x2f, y2f = x2[frame], y2[frame]
        rod1_line.set_data([x_pivot, x1f], [y_pivot, y1f])
        rod2_line.set_data([x1f, x2f], [y1f, y2f])
        mass1.center = (x1f, y1f)
        mass2.center = (x2f, y2f)
        return rod1_line, rod2_line, mass1, mass2

    anim = FuncAnimation(
        ax.get_figure(),
        update,
        frames=len(t),
        init_func=init,
        blit=True,
        interval=1000 * (t[-1] - t[0]) / len(t) if len(t) > 1 else 50,
    )
    return anim

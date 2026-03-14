"""
3D plotting: 3D trajectory, time series, optional projections.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def _state_labels_3d(system):
    keys = list(system.initial_condition_info.keys())
    return (
        keys[0] if len(keys) > 0 else "x",
        keys[1] if len(keys) > 1 else "y",
        keys[2] if len(keys) > 2 else "z",
    )


def plot_trajectory_3d(t, y, system, equilibria=None, ax=None):
    """3D trajectory with optional equilibria."""
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
    ax.plot(y[:, 0], y[:, 1], y[:, 2], color="C0", linewidth=1)
    ax.scatter(y[0, 0], y[0, 1], y[0, 2], color="C0", s=50, label="start")
    if equilibria:
        for y_eq, stability in equilibria:
            color = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
            ax.scatter(y_eq[0], y_eq[1], y_eq[2], color=color, s=80, edgecolors="k")
    xl, yl, zl = _state_labels_3d(system)
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_zlabel(zl)
    ax.set_title(f"{system.name}: 3D trajectory")
    return ax


def plot_time_series_3d(t, y, system, ax=None):
    """Time series for all three state components."""
    if ax is None:
        ax = plt.gca()
    xl, yl, zl = _state_labels_3d(system)
    ax.plot(t, y[:, 0], label=xl, color="C0")
    ax.plot(t, y[:, 1], label=yl, color="C1")
    ax.plot(t, y[:, 2], label=zl, color="C2")
    ax.set_xlabel("t")
    ax.set_ylabel("state")
    ax.set_title(f"{system.name}: time series")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax


def plot_projections(t, y, system, equilibria=None, figsize=(12, 4)):
    """Three 2D projections: xy, xz, yz."""
    xl, yl, zl = _state_labels_3d(system)
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    axes[0].plot(y[:, 0], y[:, 1], "C0")
    axes[0].plot(y[0, 0], y[0, 1], "o", color="C0", markersize=8)
    if equilibria:
        for y_eq, stability in equilibria:
            c = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
            axes[0].plot(y_eq[0], y_eq[1], "o", color=c, markersize=8, markeredgecolor="k")
    axes[0].set_xlabel(xl)
    axes[0].set_ylabel(yl)
    axes[0].set_title(f"{xl}-{yl} projection")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(y[:, 0], y[:, 2], "C0")
    axes[1].plot(y[0, 0], y[0, 2], "o", color="C0", markersize=8)
    if equilibria:
        for y_eq, stability in equilibria:
            c = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
            axes[1].plot(y_eq[0], y_eq[2], "o", color=c, markersize=8, markeredgecolor="k")
    axes[1].set_xlabel(xl)
    axes[1].set_ylabel(zl)
    axes[1].set_title(f"{xl}-{zl} projection")
    axes[1].set_aspect("equal", adjustable="box")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(y[:, 1], y[:, 2], "C0")
    axes[2].plot(y[0, 1], y[0, 2], "o", color="C0", markersize=8)
    if equilibria:
        for y_eq, stability in equilibria:
            c = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
            axes[2].plot(y_eq[1], y_eq[2], "o", color=c, markersize=8, markeredgecolor="k")
    axes[2].set_xlabel(yl)
    axes[2].set_ylabel(zl)
    axes[2].set_title(f"{yl}-{zl} projection")
    axes[2].set_aspect("equal", adjustable="box")
    axes[2].grid(True, alpha=0.3)
    plt.suptitle(f"{system.name}: projections")
    plt.tight_layout()
    return fig


def plot_3d(system, params, t, y, equilibria=None, show_projections=True, figsize=(14, 5)):
    """
    Combined 3D figure: 3D trajectory + time series; optionally projections in a second figure.
    """
    fig = plt.figure(figsize=figsize)
    ax3d = fig.add_subplot(121, projection="3d")
    plot_trajectory_3d(t, y, system, equilibria=equilibria, ax=ax3d)
    ax_ts = fig.add_subplot(122)
    plot_time_series_3d(t, y, system, ax=ax_ts)
    plt.tight_layout()
    if show_projections:
        plot_projections(t, y, system, equilibria=equilibria, figsize=(12, 4))
    return fig

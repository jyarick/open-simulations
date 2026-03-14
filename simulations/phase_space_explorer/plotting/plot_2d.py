"""
2D plotting: phase plane trajectory, vector field (quiver/streamplot), time series.
"""

import numpy as np
import matplotlib.pyplot as plt


def _state_labels(system):
    keys = list(system.initial_condition_info.keys())
    return keys[0] if keys else "x", keys[1] if len(keys) > 1 else "y"


def plot_phase_plane(t, y, system, equilibria=None, ax=None):
    """Phase plane: y[:,1] vs y[:,0] with optional equilibria."""
    if ax is None:
        ax = plt.gca()
    ax.plot(y[:, 0], y[:, 1], color="C0", linewidth=1.5)
    ax.plot(y[0, 0], y[0, 1], "o", color="C0", markersize=8, label="start")
    if equilibria:
        for y_eq, stability in equilibria:
            color = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
            ax.plot(y_eq[0], y_eq[1], "o", markersize=10, color=color, markeredgecolor="k")
    xlabel, ylabel = _state_labels(system)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{system.name}: phase plane")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    return ax


def plot_vector_field_2d(system, params, x_min, x_max, y_min, y_max, n=20, ax=None):
    """Quiver plot of (f0, f1) on a grid."""
    if ax is None:
        ax = plt.gca()
    X = np.linspace(x_min, x_max, n)
    Y = np.linspace(y_min, y_max, n)
    XX, YY = np.meshgrid(X, Y)
    U = np.zeros_like(XX)
    V = np.zeros_like(YY)
    for i in range(n):
        for j in range(n):
            f = system.rhs(0, np.array([XX[i, j], YY[i, j]]), params)
            U[i, j], V[i, j] = f[0], f[1]
    ax.quiver(XX, YY, U, V, alpha=0.7, scale=None)
    xlabel, ylabel = _state_labels(system)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{system.name}: vector field")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    return ax


def plot_time_series(t, y, system, ax=None):
    """Two panels: y0(t) and y1(t)."""
    if ax is None:
        ax = plt.gca()
    xlabel, ylabel = _state_labels(system)
    ax.plot(t, y[:, 0], label=xlabel, color="C0")
    ax.plot(t, y[:, 1], label=ylabel, color="C1")
    ax.set_xlabel("t")
    ax.set_ylabel("state")
    ax.set_title(f"{system.name}: time series")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax


def plot_2d(system, params, t, y, equilibria=None, phase_lim=None, figsize=(14, 5)):
    """
    Combined 2D figure: phase plane, vector field, time series.
    phase_lim: (x_min, x_max, y_min, y_max) for phase plane and vector field.
    """
    if phase_lim is None:
        margin = 0.1 * (y.max() - y.min()) or 1
        x_min = y[:, 0].min() - margin
        x_max = y[:, 0].max() + margin
        y_min = y[:, 1].min() - margin
        y_max = y[:, 1].max() + margin
        phase_lim = (x_min, x_max, y_min, y_max)
    x_min, x_max, y_min, y_max = phase_lim
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    plot_phase_plane(t, y, system, equilibria=equilibria, ax=axes[0])
    axes[0].set_xlim(x_min, x_max)
    axes[0].set_ylim(y_min, y_max)
    plot_vector_field_2d(system, params, x_min, x_max, y_min, y_max, ax=axes[1])
    plot_time_series(t, y, system, ax=axes[2])
    plt.tight_layout()
    return fig

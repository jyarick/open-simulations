"""
1D plotting: trajectory x(t), vector field f(x), phase line.
"""

import numpy as np
import matplotlib.pyplot as plt


def _state_label(system, index=0):
    keys = list(system.initial_condition_info.keys())
    return keys[index] if index < len(keys) else f"y{index}"


def plot_trajectory(t, y, system, ax=None):
    """Plot state x(t) vs time."""
    if ax is None:
        ax = plt.gca()
    ax.plot(t, y[:, 0], color="C0")
    ax.set_xlabel("t")
    ax.set_ylabel(_state_label(system, 0))
    ax.set_title(f"{system.name}: trajectory")
    ax.grid(True, alpha=0.3)
    return ax


def plot_vector_field(system, params, x_min, x_max, n_pts=50, ax=None):
    """Plot f(x) vs x (rate of change on the phase line)."""
    if ax is None:
        ax = plt.gca()
    x = np.linspace(x_min, x_max, n_pts)
    f = np.array([system.rhs(0, np.array([xi]), params)[0] for xi in x])
    ax.plot(x, f, color="C1")
    ax.axhline(0, color="k", linewidth=0.5)
    ax.set_xlabel(_state_label(system, 0))
    ax.set_ylabel(f"d{_state_label(system, 0)}/dt")
    ax.set_title(f"{system.name}: vector field f(x)")
    ax.grid(True, alpha=0.3)
    return ax


def plot_phase_line(system, params, x_min, x_max, equilibria=None, ax=None):
    """
    Phase line: horizontal line with equilibria marked and flow direction.
    equilibria: list of (state, stability) from get_equilibria_with_stability.
    """
    if ax is None:
        ax = plt.gca()
    n_pts = 100
    x = np.linspace(x_min, x_max, n_pts)
    f = np.array([system.rhs(0, np.array([xi]), params)[0] for xi in x])
    ax.plot(x, np.zeros_like(x), "k-", linewidth=2)
    # Flow arrows: where f > 0 rightward, f < 0 leftward
    step = max(1, n_pts // 15)
    for i in range(0, n_pts, step):
        xi = x[i]
        fi = f[i]
        if abs(fi) < 1e-12:
            continue
        dx = 0.02 * (x_max - x_min)
        ax.annotate("", xy=(xi + dx if fi > 0 else xi - dx, 0), xytext=(xi, 0),
                    arrowprops=dict(arrowstyle="->", color="C0", lw=1.5))
    if equilibria:
        for y_eq, stability in equilibria:
            x_eq = y_eq[0]
            if x_min <= x_eq <= x_max:
                color = "green" if stability == "stable" else "red" if stability == "unstable" else "gray"
                ax.plot(x_eq, 0, "o", markersize=10, color=color, markeredgecolor="k")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel(_state_label(system, 0))
    ax.set_yticks([])
    ax.set_title(f"{system.name}: phase line")
    ax.grid(True, alpha=0.3, axis="x")
    return ax


def plot_1d(system, params, t, y, equilibria=None, x_lim=None, figsize=(12, 4)):
    """
    Combined 1D figure: trajectory, vector field, phase line.
    x_lim: (x_min, x_max) for phase line and vector field; defaults to trajectory range with padding.
    """
    if x_lim is None:
        x_min = max(0, y[:, 0].min() - 1)
        x_max = y[:, 0].max() + 1
        x_lim = (x_min, x_max)
    x_min, x_max = x_lim
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    plot_trajectory(t, y, system, ax=axes[0])
    plot_vector_field(system, params, x_min, x_max, ax=axes[1])
    plot_phase_line(system, params, x_min, x_max, equilibria=equilibria, ax=axes[2])
    plt.tight_layout()
    return fig

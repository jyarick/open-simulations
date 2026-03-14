"""
Artistic visualization of the Schrödinger's cat thought experiment.

Dark, atmospheric aesthetic with glowing box and translucent silhouettes.
All rendering is procedural using matplotlib — no external assets.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _draw_cat_silhouette(
    ax: plt.Axes,
    center_x: float,
    center_y: float,
    scale: float,
    facecolor: str,
    alpha: float,
) -> None:
    """
    Draw a simple, stylized cat silhouette using ellipses and polygons.
    Abstract and minimal — not cartoonish.
    """
    cx, cy = center_x, center_y
    # Body: elongated ellipse
    body = mpatches.Ellipse(
        (cx, cy), 0.35 * scale, 0.5 * scale,
        facecolor=facecolor, edgecolor="none", alpha=alpha,
    )
    ax.add_patch(body)
    # Head: circle offset upward
    head = mpatches.Circle(
        (cx, cy + 0.6 * scale), 0.25 * scale,
        facecolor=facecolor, edgecolor="none", alpha=alpha,
    )
    ax.add_patch(head)
    # Ears: two triangles
    head_cy = cy + 0.6 * scale
    left_ear = mpatches.Polygon(
        [(cx - 0.12 * scale, head_cy + 0.2 * scale),
         (cx - 0.2 * scale, head_cy + 0.35 * scale),
         (cx - 0.05 * scale, head_cy + 0.22 * scale)],
        facecolor=facecolor, edgecolor="none", alpha=alpha,
    )
    right_ear = mpatches.Polygon(
        [(cx + 0.05 * scale, head_cy + 0.22 * scale),
         (cx + 0.2 * scale, head_cy + 0.35 * scale),
         (cx + 0.12 * scale, head_cy + 0.2 * scale)],
        facecolor=facecolor, edgecolor="none", alpha=alpha,
    )
    ax.add_patch(left_ear)
    ax.add_patch(right_ear)


def draw_cat_box(
    ax: plt.Axes,
    probabilities: dict[str, float],
    measured_outcome: str | None = None,
) -> None:
    """
    Draw a sealed box with cat silhouettes. Dark, atmospheric aesthetic.

    Before measurement: two translucent silhouettes with opacity ∝ probability.
    After measurement: one clear silhouette (the measured state).

    Args:
        ax: Matplotlib axes
        probabilities: {"alive": p_alive, "dead": p_dead}
        measured_outcome: None (pre-measurement) or "alive" or "dead"
    """
    # Dark background
    ax.set_facecolor("#0a0a0f")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Box: rectangle with subtle glow
    box = mpatches.FancyBboxPatch(
        (-0.9, -0.9), 1.8, 1.8,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor="#12121a",
        edgecolor="#3a4a6a",
        linewidth=2,
        alpha=0.95,
    )
    ax.add_patch(box)

    # Glow effect: outer halo
    for glow_alpha, glow_lw in [(0.08, 12), (0.04, 6)]:
        glow_patch = mpatches.FancyBboxPatch(
            (-0.92, -0.92), 1.84, 1.84,
            boxstyle="round,pad=0.02,rounding_size=0.09",
            facecolor="none",
            edgecolor="#5a7aaa",
            linewidth=glow_lw,
            alpha=glow_alpha,
        )
        ax.add_patch(glow_patch)

    # Determine what to draw
    if measured_outcome is not None:
        # Post-measurement: one clear silhouette (definite state)
        if measured_outcome == "alive":
            x, y = -0.15, 0.0
        else:
            x, y = 0.15, 0.0
        _draw_cat_silhouette(ax, x, y, 0.7, "#c8d4e8", 0.85)
    else:
        # Pre-measurement: two silhouettes with opacity ∝ probability
        p_alive = probabilities.get("alive", 0.5)
        p_dead = probabilities.get("dead", 0.5)

        # Subtle haze/glow in center to suggest superposition (behind silhouettes)
        haze = mpatches.Ellipse(
            (0, 0), 0.8, 0.9,
            facecolor="#2a3a5a",
            alpha=0.15,
        )
        ax.add_patch(haze)

        # Alive silhouette (left, slightly up) — warmer tone
        alpha_alive = 0.4 + 0.5 * p_alive
        _draw_cat_silhouette(ax, -0.2, 0.05, 0.65, "#8a9cc8", min(alpha_alive, 0.9))

        # Dead silhouette (right, slightly down) — cooler, subdued tone
        alpha_dead = 0.4 + 0.5 * p_dead
        _draw_cat_silhouette(ax, 0.2, -0.05, 0.65, "#6a7a98", min(alpha_dead, 0.9))


def plot_probabilities(ax: plt.Axes, probabilities: dict[str, float]) -> None:
    """
    Bar chart of alive and dead probabilities.
    """
    ax.set_facecolor("#0a0a0f")
    ax.tick_params(colors="#8a9aaa")
    for spine in ax.spines.values():
        spine.set_color("#2a3a5a")

    labels = ["alive", "dead"]
    values = [probabilities.get("alive", 0), probabilities.get("dead", 0)]
    colors = ["#6a9a8a", "#8a6a7a"]

    ax.bar(labels, values, color=colors, edgecolor="#3a4a6a", linewidth=1)
    ax.set_ylabel("Probability", color="#8a9aaa")
    ax.set_ylim(0, 1.1)
    ax.set_xticks(range(len(labels)), labels, color="#8a9aaa")


def plot_histogram(ax: plt.Axes, counts: dict[str, int]) -> None:
    """
    Histogram of outcomes from repeated trials.
    """
    ax.set_facecolor("#0a0a0f")
    ax.tick_params(colors="#8a9aaa")
    for spine in ax.spines.values():
        spine.set_color("#2a3a5a")

    labels = ["alive", "dead"]
    values = [counts.get("alive", 0), counts.get("dead", 0)]
    colors = ["#6a9a8a", "#8a6a7a"]

    ax.bar(labels, values, color=colors, edgecolor="#3a4a6a", linewidth=1)
    ax.set_ylabel("Count", color="#8a9aaa")
    ax.set_xticks(range(len(labels)), labels, color="#8a9aaa")

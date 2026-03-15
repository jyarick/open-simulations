"""
Matplotlib-based renderer for the gravity assist simulation.
Dark space background, star, planet, spacecraft, speed-colored trails, velocity arrows.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcollections
import matplotlib.colors as mcolors

from config.constants import (
    STAR_RADIUS_VISUAL,
    PLANET_RADIUS_VISUAL,
    SPACECRAFT_RADIUS_VISUAL,
    VIEW_SCALE,
    GRAVITY_RING_ALPHA,
)


class Renderer:
    """
    Renders the simulation with matplotlib.
    Dark background, celestial bodies, trails, velocity vectors, gravity rings.
    """

    def __init__(
        self,
        view_scale: float = VIEW_SCALE,
        show_velocity_arrows: bool = True,
        show_gravity_rings: bool = True,
        velocity_arrow_scale: float = 0.15,
    ):
        self.view_scale = view_scale
        self.show_velocity_arrows = show_velocity_arrows
        self.show_gravity_rings = show_gravity_rings
        self.velocity_arrow_scale = velocity_arrow_scale
        self.fig: plt.Figure | None = None
        self.ax: plt.Axes | None = None
        self._colorbar = None

    def setup_figure(self) -> None:
        """Create figure with dark space background."""
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_facecolor("#0a0a12")
        self.fig.patch.set_facecolor("#0a0a12")
        self.ax.set_xlim(-self.view_scale, self.view_scale)
        self.ax.set_ylim(-self.view_scale, self.view_scale)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        # Subtle grid for scale reference
        self.ax.grid(True, alpha=0.1, color="white")
        self.ax.tick_params(colors="gray", labelsize=8)

    def draw_star(self, position: np.ndarray) -> None:
        """Draw the star (yellow circle)."""
        circle = plt.Circle(
            (position[0], position[1]),
            STAR_RADIUS_VISUAL,
            color="#ffdd44",
            ec="#ffaa00",
            lw=1,
            zorder=10,
        )
        self.ax.add_patch(circle)
        # Glow effect
        glow = plt.Circle(
            (position[0], position[1]),
            STAR_RADIUS_VISUAL * 1.5,
            color="#ffdd44",
            alpha=0.2,
            zorder=9,
        )
        self.ax.add_patch(glow)

    def draw_planet(self, position: np.ndarray) -> None:
        """Draw the planet (blue circle) with optional gravity rings."""
        if self.show_gravity_rings:
            for r in [1.5, 2.5, 3.5]:
                ring = plt.Circle(
                    (position[0], position[1]),
                    PLANET_RADIUS_VISUAL * r,
                    fill=False,
                    ec="#4488ff",
                    alpha=GRAVITY_RING_ALPHA,
                    lw=0.5,
                    zorder=5,
                )
                self.ax.add_patch(ring)
        circle = plt.Circle(
            (position[0], position[1]),
            PLANET_RADIUS_VISUAL,
            color="#4488ff",
            ec="#2266cc",
            lw=1,
            zorder=8,
        )
        self.ax.add_patch(circle)

    def draw_spacecraft(self, position: np.ndarray) -> None:
        """Draw the spacecraft (white dot)."""
        circle = plt.Circle(
            (position[0], position[1]),
            SPACECRAFT_RADIUS_VISUAL,
            color="#ffffff",
            ec="#aaaaaa",
            lw=0.5,
            zorder=12,
        )
        self.ax.add_patch(circle)

    def draw_trail(
        self,
        points: np.ndarray,
        speeds: np.ndarray,
        speed_min: float,
        speed_max: float,
        colormap: str = "plasma",
    ) -> None:
        """Draw trajectory trail with color by speed (cool=slow, warm=fast)."""
        if points is None or len(points) < 2 or speeds is None or len(speeds) < 2:
            return
        n = len(points)
        segments = np.array([[points[i], points[i + 1]] for i in range(n - 1)])
        # Color each segment by average speed for smoother gradient
        seg_speeds = 0.5 * (speeds[:-1] + speeds[1:])
        if speed_max <= speed_min:
            speed_max = speed_min + 1e-6
        norm = mcolors.Normalize(vmin=speed_min, vmax=speed_max)
        cmap = plt.get_cmap(colormap)
        colors = cmap(norm(seg_speeds))
        # Fade older segments (lower index = older)
        alphas = np.linspace(0.35, 0.95, len(segments))
        colors[:, 3] *= alphas
        lc = mcollections.LineCollection(
            segments,
            colors=colors,
            linewidths=1.8,
            zorder=6,
        )
        self.ax.add_collection(lc)

    def draw_speed_readout(
        self,
        current_speed: float,
        initial_speed: float,
        max_speed: float,
    ) -> None:
        """Draw small speed readout in corner."""
        text = (
            f"current: {current_speed:.3f}\n"
            f"initial: {initial_speed:.3f}\n"
            f"max:     {max_speed:.3f}"
        )
        self.ax.text(
            0.02,
            0.98,
            text,
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            fontfamily="monospace",
            color="#aaaaaa",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#0a0a12", edgecolor="#333", alpha=0.9),
            zorder=20,
        )

    def draw_velocity_arrow(
        self, position: np.ndarray, velocity: np.ndarray, color: str = "cyan"
    ) -> None:
        """Draw velocity vector as arrow."""
        if not self.show_velocity_arrows or np.linalg.norm(velocity) < 1e-6:
            return
        scale = self.velocity_arrow_scale
        dx, dy = velocity[0] * scale, velocity[1] * scale
        self.ax.annotate(
            "",
            xy=(position[0] + dx, position[1] + dy),
            xytext=(position[0], position[1]),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
            zorder=11,
        )

    def render_frame(
        self,
        star_pos: np.ndarray,
        planet_pos: np.ndarray,
        spacecraft_pos: np.ndarray,
        spacecraft_vel: np.ndarray,
        trail_points: np.ndarray,
        trail_speeds: np.ndarray,
        speed_min: float,
        speed_max: float,
        current_speed: float,
        initial_speed: float,
        max_speed: float,
    ) -> None:
        """Draw one complete frame. Clears and redraws."""
        self.ax.clear()
        self.ax.set_facecolor("#0a0a12")
        self.ax.set_xlim(-self.view_scale, self.view_scale)
        self.ax.set_ylim(-self.view_scale, self.view_scale)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.grid(True, alpha=0.1, color="white")

        self.draw_trail(trail_points, trail_speeds, speed_min, speed_max)
        self.draw_star(star_pos)
        self.draw_planet(planet_pos)
        self.draw_spacecraft(spacecraft_pos)
        self.draw_velocity_arrow(spacecraft_pos, spacecraft_vel, "cyan")
        self.draw_speed_readout(current_speed, initial_speed, max_speed)

        # Speed colorbar (create once, update each frame)
        if len(trail_points) >= 2 and len(trail_speeds) >= 2:
            sm = plt.cm.ScalarMappable(
                norm=mcolors.Normalize(vmin=speed_min, vmax=speed_max),
                cmap=plt.get_cmap("plasma"),
            )
            sm.set_array([])
            if self._colorbar is None:
                self._colorbar = self.fig.colorbar(
                    sm, ax=self.ax, shrink=0.5, pad=0.02
                )
                self._colorbar.set_label("Speed", color="#aaaaaa", fontsize=9)
                self._colorbar.ax.tick_params(colors="#888", labelsize=7)
            else:
                self._colorbar.update_normal(sm)

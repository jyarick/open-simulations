"""
Pygame renderer: draws bodies, trails, velocity arrows, HUD.
Speed-colored trail: cool (slow) -> warm (fast).
"""

import math
import random
import pygame
import numpy as np

from config import (
    STAR_RADIUS_VISUAL,
    SPACECRAFT_RADIUS_VISUAL,
    COLOR_BG,
    COLOR_STAR,
    COLOR_STAR_GLOW,
    COLOR_SPACECRAFT,
    COLOR_VELOCITY_ARROW,
    COLOR_PLANET_VELOCITY,
    COLOR_HUD_TEXT,
    COLOR_STARFIELD,
    COLOR_ESCAPE,
    COLOR_BOUND,
    TRAIL_COLOR_SLOW,
    TRAIL_COLOR_FAST,
    VELOCITY_ARROW_SCALE,
    PLANET_VELOCITY_ARROW_SCALE,
    GRAVITY_RING_ALPHA,
    GRAVITY_RING_MULTIPLIERS,
    STAR_GLOW_RADIUS_MULT,
    NUM_STARS_BACKDROP,
)
from utils import world_to_screen, world_scale_to_screen, interpolate_color


class Renderer:
    """
    Renders the simulation with Pygame.
    Dark space, starfield, celestial bodies, speed-colored trails, HUD.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        show_trails: bool = True,
        show_velocity_arrows: bool = True,
        show_gravity_rings: bool = True,
        show_hud: bool = True,
    ):
        self.screen = screen
        self.show_trails = show_trails
        self.show_velocity_arrows = show_velocity_arrows
        self.show_gravity_rings = show_gravity_rings
        self.show_hud = show_hud
        self._starfield: list[tuple[int, int, int]] = []
        self._starfield_size: tuple[int, int] = (0, 0)
        self._viewport = (0, 0, 800, 600)  # updated each frame
        self._view_scale = 3.0

    def _init_starfield(self, vw: int, vh: int) -> None:
        """Generate random star positions for viewport backdrop."""
        random.seed(42)
        self._starfield = [
            (
                random.randint(0, max(1, vw - 1)),
                random.randint(0, max(1, vh - 1)),
                random.randint(1, 3),  # brightness/size
            )
            for _ in range(NUM_STARS_BACKDROP)
        ]

    def _set_viewport(self, x: int, y: int, w: int, h: int, view_scale: float) -> None:
        self._viewport = (x, y, w, h)
        self._view_scale = view_scale

    def _to_screen(self, world_pos: np.ndarray) -> tuple[int, int]:
        vx, vy, vw, vh = self._viewport
        return world_to_screen(world_pos, vw, vh, self._view_scale, vx, vy)

    def _scale(self, world_length: float) -> float:
        _, _, vw, vh = self._viewport
        return world_scale_to_screen(world_length, vw, vh, self._view_scale)

    def draw_starfield(self) -> None:
        """Draw faint starfield backdrop in viewport."""
        vx, vy, _, _ = self._viewport
        for sx, sy, b in self._starfield:
            c = min(255, COLOR_STARFIELD[0] + b * 20)
            pygame.draw.circle(self.screen, (c, c, c + 10), (vx + sx, vy + sy), b)

    def draw_star(self, position: np.ndarray) -> None:
        """Draw star with glow effect."""
        sx, sy = self._to_screen(position)
        r_screen = max(2, int(self._scale(STAR_RADIUS_VISUAL)))
        glow_r = max(3, int(r_screen * STAR_GLOW_RADIUS_MULT))

        # Glow: faint outer circle
        glow_color = (
            min(255, COLOR_STAR_GLOW[0] // 3),
            min(255, COLOR_STAR_GLOW[1] // 3),
            min(255, COLOR_STAR_GLOW[2] // 3),
        )
        pygame.draw.circle(self.screen, glow_color, (sx, sy), glow_r)

        # Core
        pygame.draw.circle(self.screen, COLOR_STAR, (sx, sy), r_screen)
        pygame.draw.circle(
            self.screen,
            (255, 255, 200),
            (sx, sy),
            r_screen,
            1,
        )

    def draw_planet(self, planet) -> None:
        """Draw planet with optional gravity rings. planet has position, radius_visual, color, ring_color."""
        px, py = self._to_screen(planet.position)
        r_screen = max(2, int(self._scale(planet.radius_visual)))

        if self.show_gravity_rings:
            for mult in GRAVITY_RING_MULTIPLIERS:
                ring_r = max(1, int(r_screen * mult))
                alpha_surf = pygame.Surface((ring_r * 2, ring_r * 2))
                alpha_surf.set_alpha(int(255 * GRAVITY_RING_ALPHA))
                pygame.draw.circle(
                    alpha_surf,
                    planet.ring_color,
                    (ring_r, ring_r),
                    ring_r,
                    1,
                )
                self.screen.blit(alpha_surf, (px - ring_r, py - ring_r))

        pygame.draw.circle(self.screen, planet.color, (px, py), r_screen)
        edge = tuple(min(255, c + 40) for c in planet.color)
        pygame.draw.circle(self.screen, edge, (px, py), r_screen, 1)

    def draw_spacecraft(self, position: np.ndarray) -> None:
        """Draw spacecraft as bright dot."""
        cx, cy = self._to_screen(position)
        r = max(2, int(self._scale(SPACECRAFT_RADIUS_VISUAL)))
        pygame.draw.circle(self.screen, COLOR_SPACECRAFT, (cx, cy), r)
        pygame.draw.circle(
            self.screen,
            (200, 200, 220),
            (cx, cy),
            r,
            1,
        )

    def draw_trail(
        self,
        points: np.ndarray,
        speeds: np.ndarray,
        speed_min: float,
        speed_max: float,
    ) -> None:
        """
        Draw trajectory trail with color by speed.
        Lower speed -> darker/cooler. Higher speed -> brighter/warmer.
        """
        if not self.show_trails or points is None or len(points) < 2:
            return
        if speeds is None or len(speeds) < 2:
            return

        if speed_max <= speed_min:
            speed_max = speed_min + 1e-6

        n = len(points)
        for i in range(n - 1):
            p0 = points[i]
            p1 = points[i + 1]
            s_avg = 0.5 * (speeds[i] + speeds[i + 1])
            t = (s_avg - speed_min) / (speed_max - speed_min)
            color = interpolate_color(t, TRAIL_COLOR_SLOW, TRAIL_COLOR_FAST)

            x0, y0 = self._to_screen(p0)
            x1, y1 = self._to_screen(p1)
            thickness = max(1, min(3, int(2 + t)))
            pygame.draw.line(self.screen, color, (x0, y0), (x1, y1), thickness)

    def draw_velocity_arrow(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        color: tuple[int, int, int],
        scale: float,
    ) -> None:
        """Draw velocity vector as arrow."""
        if not self.show_velocity_arrows or np.linalg.norm(velocity) < 1e-6:
            return

        end_pos = position + velocity * scale
        x0, y0 = self._to_screen(position)
        x1, y1 = self._to_screen(end_pos)

        dx_screen = x1 - x0
        dy_screen = y1 - y0
        angle = math.atan2(-dy_screen, dx_screen)

        pygame.draw.line(self.screen, color, (x0, y0), (x1, y1), 2)
        head_len = 8
        pygame.draw.line(
            self.screen,
            color,
            (x1, y1),
            (
                int(x1 - head_len * math.cos(angle - 0.4)),
                int(y1 + head_len * math.sin(angle - 0.4)),
            ),
            2,
        )
        pygame.draw.line(
            self.screen,
            color,
            (x1, y1),
            (
                int(x1 - head_len * math.cos(angle + 0.4)),
                int(y1 + head_len * math.sin(angle + 0.4)),
            ),
            2,
        )

    def draw_hud(
        self,
        preset_name: str,
        current_speed: float,
        initial_speed: float,
        max_speed: float,
        epsilon: float,
        is_escape: bool,
        incoming_speed: float | None,
        outgoing_speed: float | None,
        energy_change: float | None,
        sim_time: float,
        time_scale: float,
        paused: bool,
    ) -> None:
        """Draw info overlay in corner."""
        if not self.show_hud:
            return

        try:
            font = pygame.font.Font(None, 24)
        except OSError:
            font = pygame.font.SysFont("monospace", 18)
        lines = [
            f"[{preset_name}]",
            "",
            f"Speed:     {current_speed:.3f}",
            f"Initial:   {initial_speed:.3f}",
            f"Max:       {max_speed:.3f}",
            "",
            f"ε (energy): {epsilon:.4f}",
            ">>> ESCAPE <<<" if is_escape else "Bound to star",
            "",
        ]
        if incoming_speed is not None:
            lines.append(f"Incoming:  {incoming_speed:.3f}")
        if outgoing_speed is not None:
            lines.append(f"Outgoing:  {outgoing_speed:.3f}")
        if energy_change is not None:
            lines.append(f"ΔEnergy:   {energy_change:+.4f}")
        lines.extend([
            "",
            f"Time:      {sim_time:.2f}",
            f"Scale:     {time_scale:.1f}x",
            "PAUSED" if paused else "",
        ])

        # Background panel
        padding = 10
        line_height = 22
        panel_width = 200
        panel_height = len(lines) * line_height + padding * 2
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(220)
        panel.fill((12, 12, 24))
        pygame.draw.rect(panel, (40, 40, 60), (0, 0, panel_width, panel_height), 1)

        y = padding
        for line in lines:
            if line:
                color = COLOR_ESCAPE if (line == ">>> ESCAPE <<<") else COLOR_BOUND if (line == "Bound to star") else COLOR_HUD_TEXT
                text = font.render(line, True, color)
                panel.blit(text, (padding, y))
            y += line_height

        self.screen.blit(panel, (10, 10))

    def render_frame(
        self,
        sim,
        viewport: tuple[int, int, int, int],
        view_scale: float,
    ) -> None:
        """Draw one complete frame. viewport = (x, y, width, height)."""
        vx, vy, vw, vh = viewport
        self._set_viewport(vx, vy, vw, vh, view_scale)
        if self._starfield_size != (vw, vh):
            self._init_starfield(vw, vh)
            self._starfield_size = (vw, vh)
        self.screen.fill(COLOR_BG)
        # Fill viewport with dark bg
        pygame.draw.rect(self.screen, COLOR_BG, (vx, vy, vw, vh))
        self.draw_starfield()

        # Trail (behind bodies)
        points, speeds = sim.trail.get_points_and_speeds()
        speed_min = sim.initial_speed
        speed_max = max(sim.max_speed, sim.initial_speed * 1.01)
        self.draw_trail(points, speeds, speed_min, speed_max)

        # Bodies
        self.draw_star(sim.star.position)
        for planet in sim.planets:
            self.draw_planet(planet)
        self.draw_spacecraft(sim.spacecraft.position)

        # Velocity arrows
        self.draw_velocity_arrow(
            sim.spacecraft.position,
            sim.spacecraft.velocity,
            COLOR_VELOCITY_ARROW,
            VELOCITY_ARROW_SCALE,
        )
        for planet in sim.planets:
            self.draw_velocity_arrow(
                planet.position,
                planet.velocity,
                COLOR_PLANET_VELOCITY,
                PLANET_VELOCITY_ARROW_SCALE,
            )

        # HUD
        self.draw_hud(
            preset_name=sim.preset["name"],
            current_speed=sim.spacecraft.speed,
            initial_speed=sim.initial_speed,
            max_speed=sim.max_speed,
            epsilon=sim.heliocentric_energy(),
            is_escape=sim.is_escape_trajectory(),
            incoming_speed=sim.incoming_speed,
            outgoing_speed=sim.outgoing_speed,
            energy_change=sim.energy_change(),
            sim_time=sim.time,
            time_scale=sim.time_scale,
            paused=sim.paused,
        )

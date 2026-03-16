"""
Utility functions: coordinate conversion, trail management, etc.
"""

from collections import deque
from typing import Deque, Tuple

import numpy as np


def world_to_screen(
    world_pos: np.ndarray,
    viewport_width: int,
    viewport_height: int,
    view_scale: float,
    viewport_x: int = 0,
    viewport_y: int = 0,
) -> Tuple[int, int]:
    """
    Convert world coordinates (physics) to screen coordinates (Pygame).
    World: origin at center, +y up. Screen: origin top-left, +y down.
    Maps world ±view_scale to viewport edges.
    """
    x = viewport_x + viewport_width / 2 + world_pos[0] / view_scale * (viewport_width / 2)
    y = viewport_y + viewport_height / 2 - world_pos[1] / view_scale * (viewport_height / 2)
    return int(x), int(y)


def screen_to_world(
    screen_x: int,
    screen_y: int,
    viewport_width: int,
    viewport_height: int,
    view_scale: float,
    viewport_x: int = 0,
    viewport_y: int = 0,
) -> np.ndarray:
    """Convert screen coordinates to world coordinates."""
    cx = viewport_x + viewport_width / 2
    cy = viewport_y + viewport_height / 2
    x = (screen_x - cx) / (viewport_width / 2) * view_scale
    y = (cy - screen_y) / (viewport_height / 2) * view_scale
    return np.array([x, y])


def world_scale_to_screen(
    world_length: float,
    viewport_width: int,
    viewport_height: int,
    view_scale: float,
) -> float:
    """Convert a world-space length to screen pixels."""
    return world_length / view_scale * min(viewport_width, viewport_height) / 2


class TrailManager:
    """Stores trajectory points and speeds for speed-colored trail rendering."""

    def __init__(self, max_length: int = 800):
        self._points: Deque[np.ndarray] = deque(maxlen=max_length)
        self._speeds: Deque[float] = deque(maxlen=max_length)
        self.max_length = max_length

    def add(self, position: np.ndarray, speed: float) -> None:
        self._points.append(position.copy())
        self._speeds.append(speed)

    def get_points_and_speeds(self) -> Tuple[np.ndarray, np.ndarray]:
        if not self._points:
            return np.zeros((0, 2)), np.zeros(0)
        return np.array(list(self._points)), np.array(list(self._speeds))

    def clear(self) -> None:
        self._points.clear()
        self._speeds.clear()

    def set_max_length(self, new_max: int) -> None:
        """Resize trail, keeping most recent points."""
        new_max = max(10, new_max)
        if new_max == self.max_length:
            return
        old_points = list(self._points)
        old_speeds = list(self._speeds)
        self._points = deque(maxlen=new_max)
        self._speeds = deque(maxlen=new_max)
        keep = min(len(old_points), new_max)
        for i in range(-keep, 0):
            self._points.append(old_points[i].copy())
            self._speeds.append(old_speeds[i])
        self.max_length = new_max


def interpolate_color(
    t: float,
    color_slow: Tuple[int, int, int],
    color_fast: Tuple[int, int, int],
) -> Tuple[int, int, int]:
    """
    Interpolate between two RGB colors. t=0 -> color_slow, t=1 -> color_fast.
    """
    t = max(0, min(1, t))
    return (
        int(color_slow[0] + (color_fast[0] - color_slow[0]) * t),
        int(color_slow[1] + (color_fast[1] - color_slow[1]) * t),
        int(color_slow[2] + (color_fast[2] - color_slow[2]) * t),
    )

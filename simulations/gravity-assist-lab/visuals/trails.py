"""
Trail management for spacecraft trajectory visualization.
Maintains a rolling history of positions and speeds for speed-colored rendering.
"""

from collections import deque
from typing import Deque, Tuple

import numpy as np


class TrailManager:
    """Stores and manages trajectory trail points and speeds for a body."""

    def __init__(self, max_length: int = 500):
        self._points: Deque[np.ndarray] = deque(maxlen=max_length)
        self._speeds: Deque[float] = deque(maxlen=max_length)
        self.max_length = max_length

    def add(self, position: np.ndarray, speed: float) -> None:
        """Add a new position and speed to the trail."""
        self._points.append(position.copy())
        self._speeds.append(speed)

    def get_points_and_speeds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return trail as (points, speeds). points: (N, 2), speeds: (N,)."""
        if not self._points:
            return np.zeros((0, 2)), np.zeros(0)
        return np.array(list(self._points)), np.array(list(self._speeds))

    def clear(self) -> None:
        """Clear the trail."""
        self._points.clear()
        self._speeds.clear()

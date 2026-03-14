"""Dimension-aware plotting."""

from .plot_1d import plot_1d, plot_trajectory, plot_vector_field, plot_phase_line
from .plot_2d import (
    plot_2d,
    plot_phase_plane,
    plot_vector_field_2d,
    plot_time_series as plot_time_series_2d,
)
from .plot_3d import (
    plot_3d,
    plot_trajectory_3d,
    plot_time_series_3d,
    plot_projections,
)


def plot_system(system, params, t, y, equilibria=None, **kwargs):
    """
    Dispatch to the right plot by system.dimension.
    kwargs: passed to plot_1d / plot_2d / plot_3d (e.g. figsize, x_lim, phase_lim).
    """
    if system.dimension == 1:
        return plot_1d(system, params, t, y, equilibria=equilibria, **kwargs)
    if system.dimension == 2:
        return plot_2d(system, params, t, y, equilibria=equilibria, **kwargs)
    if system.dimension == 3:
        return plot_3d(system, params, t, y, equilibria=equilibria, **kwargs)
"""Dimension-aware plotting."""

from .plot_1d import plot_1d, plot_trajectory, plot_vector_field, plot_phase_line
from .plot_2d import (
    plot_2d,
    plot_phase_plane,
    plot_vector_field_2d,
    plot_time_series as plot_time_series_2d,
)
from .plot_3d import (
    plot_3d,
    plot_trajectory_3d,
    plot_time_series_3d,
    plot_projections,
)


def plot_system(system, params, t, y, equilibria=None, **kwargs):
    """
    Dispatch to the right plot by system.dimension.
    kwargs: passed to plot_1d / plot_2d / plot_3d (e.g. figsize, x_lim, phase_lim).
    """
    if system.dimension == 1:
        return plot_1d(system, params, t, y, equilibria=equilibria, **kwargs)
    if system.dimension == 2:
        return plot_2d(system, params, t, y, equilibria=equilibria, **kwargs)
    if system.dimension == 3:
        return plot_3d(system, params, t, y, equilibria=equilibria, **kwargs)
    raise ValueError(f"No plotting implemented for dimension {system.dimension}")


__all__ = [
    "plot_system",
    "plot_1d",
    "plot_2d",
    "plot_3d",
    "plot_trajectory",
    "plot_vector_field",
    "plot_phase_line",
    "plot_phase_plane",
    "plot_vector_field_2d",
    "plot_time_series_2d",
    "plot_trajectory_3d",
    "plot_time_series_3d",
    "plot_projections",
]

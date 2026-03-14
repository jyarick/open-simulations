"""Dynamical systems definitions."""

from .base import DynamicalSystem
from .logistic import LOGISTIC
from .predator_prey import PREDATOR_PREY
from .oscillator import DAMPED_OSCILLATOR
from .lorenz import LORENZ

__all__ = [
    "DynamicalSystem",
    "LOGISTIC",
    "PREDATOR_PREY",
    "DAMPED_OSCILLATOR",
    "LORENZ",
]

ALL_SYSTEMS = [LOGISTIC, PREDATOR_PREY, DAMPED_OSCILLATOR, LORENZ]

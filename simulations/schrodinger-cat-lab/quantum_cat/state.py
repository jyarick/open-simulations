"""
Quantum state preparation and probability calculation for the Schrödinger's cat model.
"""

import numpy as np


def prepare_state(a: float, phi: float) -> np.ndarray:
    """
    Prepare a normalized two-state quantum state.

    Args:
        a: Amplitude magnitude for |alive> state (0 <= a <= 1)
        phi: Relative phase in radians

    Returns:
        Normalized state vector psi = [alpha, beta]
        where alpha = a, beta = sqrt(1 - a^2) * exp(i * phi)
    """
    a = np.clip(a, 0.0, 1.0)
    alpha = a
    beta = np.sqrt(1.0 - a**2) * np.exp(1j * phi)
    psi = np.array([alpha, beta], dtype=complex)
    return normalize_state(psi)


def normalize_state(psi: np.ndarray) -> np.ndarray:
    """
    Normalize a state vector so that |psi|^2 sums to 1.

    Args:
        psi: State vector as complex array

    Returns:
        Normalized state vector
    """
    norm = np.sqrt(np.sum(np.abs(psi) ** 2))
    if norm < 1e-12:
        # Fallback to equal superposition if zero
        return np.array([1.0 / np.sqrt(2), 1.0 / np.sqrt(2)], dtype=complex)
    return psi / norm


def get_probabilities(psi: np.ndarray) -> dict[str, float]:
    """
    Compute measurement probabilities via the Born rule.

    Args:
        psi: State vector [alpha, beta]

    Returns:
        Dictionary with keys "alive" and "dead" and probabilities as values
    """
    p_alive = float(np.abs(psi[0]) ** 2)
    p_dead = float(np.abs(psi[1]) ** 2)
    return {"alive": p_alive, "dead": p_dead}

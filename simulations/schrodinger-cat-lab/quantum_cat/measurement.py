"""
Born rule measurement process for the Schrödinger's cat model.
"""

import numpy as np

from quantum_cat.state import get_probabilities


def measure_state(psi: np.ndarray, rng: np.random.Generator | None = None) -> tuple[str, np.ndarray]:
    """
    Perform a measurement on the quantum state according to the Born rule.

    Steps:
    1. Compute probabilities P(alive) = |alpha|^2, P(dead) = |beta|^2
    2. Sample outcome using those probabilities
    3. Collapse state to the measured basis vector

    Args:
        psi: State vector [alpha, beta]
        rng: Optional random number generator for reproducibility

    Returns:
        Tuple of (outcome, collapsed_state)
        outcome is "alive" or "dead"
        collapsed_state is [1,0] or [0,1] respectively
    """
    if rng is None:
        rng = np.random.default_rng()

    probs = get_probabilities(psi)
    outcome = rng.choice(["alive", "dead"], p=[probs["alive"], probs["dead"]])

    if outcome == "alive":
        collapsed = np.array([1.0, 0.0], dtype=complex)
    else:
        collapsed = np.array([0.0, 1.0], dtype=complex)

    return outcome, collapsed

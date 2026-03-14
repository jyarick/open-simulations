"""
Repeated measurement experiments for the Schrödinger's cat model.
"""

import numpy as np

from quantum_cat.measurement import measure_state


def run_trials(psi: np.ndarray, n: int, rng: np.random.Generator | None = None) -> list[str]:
    """
    Run n independent measurements from the same prepared state.

    Each measurement starts from the original psi — we do NOT repeatedly
    measure the collapsed state. This simulates preparing many identical
    copies of the system and measuring each once.

    Args:
        psi: Prepared state vector
        n: Number of trials
        rng: Optional random number generator for reproducibility

    Returns:
        List of outcomes: ["alive", "dead", "alive", ...]
    """
    if rng is None:
        rng = np.random.default_rng()

    results = []
    for _ in range(n):
        outcome, _ = measure_state(psi, rng=rng)
        results.append(outcome)

    return results


def count_outcomes(results: list[str]) -> dict[str, int]:
    """
    Count occurrences of each outcome in a list of trial results.

    Args:
        results: List of "alive" and "dead" outcomes

    Returns:
        Dictionary with keys "alive" and "dead" and counts as values
    """
    alive_count = sum(1 for r in results if r == "alive")
    dead_count = len(results) - alive_count
    return {"alive": alive_count, "dead": dead_count}

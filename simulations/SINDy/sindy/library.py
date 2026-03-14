import numpy as np
from itertools import combinations_with_replacement


def polynomial_library(y, degree=3, include_constant=True):
    """
    Build a polynomial feature library with cross terms.

    Parameters
    ----------
    y : ndarray, shape (n_samples, n_states)
        State data.
    degree : int
        Maximum polynomial degree.
    include_constant : bool
        Whether to include a constant term.

    Returns
    -------
    Theta : ndarray
        Feature matrix.
    feature_names : list
        Names of the features.
    """
    y = np.asarray(y)

    if y.ndim == 1:
        y = y[:, None]

    n_samples, n_states = y.shape

    features = []
    feature_names = []

    if include_constant:
        features.append(np.ones(n_samples))
        feature_names.append("1")

    # degree 1 up to degree d
    for d in range(1, degree + 1):
        for combo in combinations_with_replacement(range(n_states), d):
            term = np.ones(n_samples)
            counts = {}

            for idx in combo:
                term *= y[:, idx]
                counts[idx] = counts.get(idx, 0) + 1

            name_parts = []
            for idx in sorted(counts):
                power = counts[idx]
                if power == 1:
                    name_parts.append(f"x{idx}")
                else:
                    name_parts.append(f"x{idx}^{power}")

            features.append(term)
            feature_names.append("*".join(name_parts))

    Theta = np.column_stack(features)
    return Theta, feature_names
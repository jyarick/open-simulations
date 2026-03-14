import numpy as np

from sindy.metrics import coefficient_error


def scale_states(X):
    """
    Scale state data to zero mean and unit variance per state (column).

    Useful before building the feature library and regression when state
    variables have very different scales (e.g. Lorenz z vs x, y). Return
    mean and std so coefficients can be rescaled later if needed.

    Parameters
    ----------
    X : ndarray, shape (n_samples,) or (n_samples, n_states)
        State data.

    Returns
    -------
    X_scaled : ndarray, same shape as X
        Scaled data: (X - mean) / std per column.
    mean : ndarray, shape (n_states,) or scalar
        Mean of each state column.
    std : ndarray, shape (n_states,) or scalar
        Std of each state column (zeros replaced by 1 to avoid div-by-zero).
    """
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std = np.where(std < 1e-14, 1.0, std)
    X_scaled = (X - mean) / std
    if X_scaled.shape[1] == 1:
        mean = mean[0]
        std = std[0]
    return X_scaled, mean, std


def print_equations(Xi, feature_names, state_names=None):
    """
    Print discovered SINDy equations.

    Parameters
    ----------
    Xi : ndarray (n_features, n_states)
        Sparse coefficient matrix.
    feature_names : list
        Names of library features.
    state_names : list or None
        Names of state variables.
    """

    n_features, n_states = Xi.shape

    if state_names is None:
        state_names = [f"x{i}" for i in range(n_states)]

    for i in range(n_states):

        terms = []

        for j in range(n_features):

            coef = Xi[j, i]

            if abs(coef) > 1e-8:
                name = feature_names[j]
                # Substitute state names (x0, x1, ...) for display when provided
                if state_names is not None:
                    for k in range(n_states):
                        name = name.replace(f"x{k}", state_names[k])
                term = f"{coef:.3f}*{name}"
                terms.append(term)

        equation = " + ".join(terms) if terms else "0"

        print(f"d{state_names[i]}/dt = {equation}")


def print_coefficient_comparison(Xi, Xi_true, feature_names, state_names=None):
    """
    Print true vs recovered coefficients and relative error.

    Coefficients must be in the same order as feature_names (library order).
    Easy to call from experiments when true coefficients are available.

    Parameters
    ----------
    Xi : ndarray (n_features, n_states)
        Recovered coefficient matrix.
    Xi_true : ndarray (n_features, n_states)
        True coefficient matrix (same shape and library order as Xi).
    feature_names : list
        Names of library features (must match column order of Xi).
    state_names : list or None
        Names of state variables for display.

    Returns
    -------
    rel_error : float
        Relative coefficient error (Frobenius).
    """
    Xi = np.asarray(Xi)
    Xi_true = np.asarray(Xi_true)
    if Xi.shape != Xi_true.shape:
        raise ValueError("Xi and Xi_true must have the same shape")
    n_features, n_states = Xi.shape
    if state_names is None:
        state_names = [f"x{i}" for i in range(n_states)]

    rel_err = coefficient_error(Xi, Xi_true)
    print(f"\n--- True vs recovered coefficients (relative error = {rel_err:.6e}) ---")
    for i in range(n_states):
        print(f"  State {state_names[i]}:")
        for j in range(n_features):
            if abs(Xi_true[j, i]) > 1e-14 or abs(Xi[j, i]) > 1e-8:
                print(f"    {feature_names[j]:12s}  true = {Xi_true[j, i]:+10.4f}  recovered = {Xi[j, i]:+10.4f}")
    return rel_err
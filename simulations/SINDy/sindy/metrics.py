import numpy as np


def coefficient_error(Xi, Xi_true):
    """
    Compute error between learned and true SINDy coefficients.

    Uses relative Frobenius error: ||Xi - Xi_true||_F / (||Xi_true||_F + eps)
    so that the result is scale-invariant. If true coefficients are zero,
    returns absolute Frobenius norm of the difference.

    Parameters
    ----------
    Xi : ndarray (n_features, n_states)
        Learned coefficient matrix.
    Xi_true : ndarray (n_features, n_states)
        True coefficient matrix (same shape as Xi).

    Returns
    -------
    rel_error : float
        Relative coefficient error (Frobenius norm).
    """
    Xi = np.asarray(Xi)
    Xi_true = np.asarray(Xi_true)
    if Xi.shape != Xi_true.shape:
        raise ValueError("Xi and Xi_true must have the same shape")

    diff = Xi - Xi_true
    norm_diff = np.linalg.norm(diff, ord="fro")
    norm_true = np.linalg.norm(Xi_true, ord="fro")
    eps = 1e-14
    if norm_true < eps:
        return norm_diff  # absolute error when true is zero
    return norm_diff / norm_true


def trajectory_reconstruction_error(Theta, Xi, dydt_true):
    """
    Compute error between true dx/dt and SINDy-predicted dx/dt.

    Predicted derivative is Theta @ Xi. Uses relative Frobenius error:
    ||dydt_true - Theta @ Xi||_F / (||dydt_true||_F + eps).

    Parameters
    ----------
    Theta : ndarray (n_samples, n_features)
        Feature library matrix.
    Xi : ndarray (n_features, n_states)
        Learned coefficient matrix.
    dydt_true : ndarray (n_samples, n_states)
        True time derivatives (e.g. from finite difference or known ODE).

    Returns
    -------
    rel_error : float
        Relative trajectory reconstruction error.
    """
    Theta = np.asarray(Theta)
    Xi = np.asarray(Xi)
    dydt_true = np.asarray(dydt_true)

    dydt_pred = Theta @ Xi
    diff = dydt_true - dydt_pred
    norm_diff = np.linalg.norm(diff, ord="fro")
    norm_true = np.linalg.norm(dydt_true, ord="fro")
    eps = 1e-14
    if norm_true < eps:
        return norm_diff
    return norm_diff / norm_true

"""
Jacobian utilities: evaluate system Jacobian or compute numerically.
"""

import numpy as np


def evaluate_jacobian(system, y, params):
    """
    Return the Jacobian matrix J_ij = ∂f_i/∂y_j at state y.

    Uses the system's analytical jacobian(y, params) if available.
    """
    return np.asarray(system.jacobian(y, params))


def numerical_jacobian(system, y, params, eps=1e-7):
    """
    Approximate Jacobian via central differences. Use when analytical form is missing.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    f0 = np.asarray(system.rhs(0.0, y, params))
    J = np.zeros((n, n))
    for j in range(n):
        y_plus = y.copy()
        y_plus[j] += eps
        y_minus = y.copy()
        y_minus[j] -= eps
        J[:, j] = (system.rhs(0.0, y_plus, params) - system.rhs(0.0, y_minus, params)) / (2 * eps)
    return J

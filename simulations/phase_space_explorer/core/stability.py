"""
Stability classification of equilibria using eigenvalues of the Jacobian.
"""

import numpy as np
from .jacobian import evaluate_jacobian


def classify_equilibrium_1d(system, x_star, params):
    """
    Classify equilibrium for 1D system: f'(x*) < 0 => stable, > 0 => unstable, = 0 => borderline.
    """
    y = np.array([float(x_star)])
    J = evaluate_jacobian(system, y, params)
    lam = float(J[0, 0])
    if lam < 0:
        return "stable"
    if lam > 0:
        return "unstable"
    return "borderline"


def classify_equilibrium_nd(system, y_star, params):
    """
    Classify equilibrium for 2D or 3D using eigenvalues of the Jacobian at y_star.
    Returns one of: stable, unstable, saddle, borderline.
    """
    y_star = np.asarray(y_star, dtype=float)
    J = evaluate_jacobian(system, y_star, params)
    eigs = np.linalg.eigvals(J)
    re = np.real(eigs)
    im = np.imag(eigs)
    tol = 1e-10
    if np.all(re < -tol):
        return "stable"
    if np.any(re > tol):
        if np.any(re < -tol):
            return "saddle"
        return "unstable"
    return "borderline"


def classify_equilibrium(system, y_star, params):
    """
    Dimension-aware classification. y_star is the equilibrium state array.
    """
    y_star = np.asarray(y_star).ravel()
    if system.dimension == 1:
        return classify_equilibrium_1d(system, y_star[0], params)
    return classify_equilibrium_nd(system, y_star, params)


def equilibrium_eigenvalues(system, y_star, params):
    """Return eigenvalues of the Jacobian at the equilibrium y_star."""
    y_star = np.asarray(y_star, dtype=float)
    J = evaluate_jacobian(system, y_star, params)
    return np.linalg.eigvals(J)

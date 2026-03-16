"""
Euler–Lagrange equation derivation for Lagrangian mechanics.

Provides symbolic computation of the Euler–Lagrange residual:
    d/dt(∂L/∂q̇) - ∂L/∂q = 0
"""

from sympy import diff, symbols, solve, Eq, Function


def derive_euler_lagrange(L, coords, t):
    """
    Compute the Euler–Lagrange residual(s) for a Lagrangian L.

    For each generalized coordinate q in coords, returns:
        d/dt(∂L/∂q̇) - ∂L/∂q

    Parameters
    ----------
    L : sympy.Expr
        The Lagrangian (scalar expression).
    coords : list of (sympy.Symbol, sympy.Symbol)
        Pairs (q, q_dot) for each generalized coordinate and its time derivative.
        e.g. [(theta, theta_dot)] for pendulum.
    t : sympy.Symbol
        Symbolic time variable.

    Returns
    -------
    list of sympy.Expr
        One residual expression per coordinate. At equilibrium, each equals 0.
    """
    residuals = []
    for q, q_dot in coords:
        dL_dqdot = diff(L, q_dot)
        dL_dq = diff(L, q)

        # d/dt(∂L/∂q̇) requires substituting q_dot -> q_ddot, q -> q_dot in chain rule
        # We need q_ddot symbols. Assume naming: if q is theta, q_dot is theta_dot,
        # then we need theta_ddot. We derive this from the expression dL_dqdot
        # which may contain q, q_dot. So:
        # d/dt(dL_dqdot) = ∂(dL_dqdot)/∂q * q_dot + ∂(dL_dqdot)/∂q_dot * q_ddot
        d_dt_dL_dqdot = diff(dL_dqdot, q) * q_dot + diff(dL_dqdot, q_dot) * diff(q_dot, t)
        # diff(q_dot, t) won't work if q_dot is a Symbol. We need q_ddot.

        # Create q_ddot symbol: e.g. theta -> theta_ddot
        q_ddot_name = str(q) + "_ddot"
        q_ddot = symbols(q_ddot_name)

        # Actually: d/dt(dL_dqdot) = (∂/∂q)(dL_dqdot) * dq/dt + (∂/∂q_dot)(dL_dqdot) * d²q/dt²
        #                              = diff(dL_dqdot, q) * q_dot + diff(dL_dqdot, q_dot) * q_ddot
        d_dt_dL_dqdot = diff(dL_dqdot, q) * q_dot + diff(dL_dqdot, q_dot) * q_ddot

        residual = d_dt_dL_dqdot - dL_dq
        residuals.append(residual)

    return residuals


def solve_for_accelerations(residuals, coords, t):
    """
    Solve the Euler–Lagrange residuals for the second derivatives (accelerations).

    Parameters
    ----------
    residuals : list of sympy.Expr
        The residual expressions (each should equal 0).
    coords : list of (sympy.Symbol, sympy.Symbol)
        Pairs (q, q_dot). Second derivatives q_ddot are inferred by name.
    t : sympy.Symbol
        Symbolic time variable (unused but kept for API consistency).

    Returns
    -------
    dict
        Mapping from each q_ddot symbol to its solved expression.
    """
    q_ddots = []
    for q, q_dot in coords:
        q_ddot_name = str(q) + "_ddot" if "_dot" in str(q) else str(q) + "_ddot"
        q_ddot = symbols(q_ddot_name)
        q_ddots.append(q_ddot)

    equations = [Eq(r, 0) for r in residuals]
    solution = solve(equations, q_ddots, dict=True)

    if not solution:
        return {}
    # Return first solution (typically unique for non-degenerate systems)
    return solution[0]

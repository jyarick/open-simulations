"""
Numerical ODE solver for second-order dynamical systems.

Wraps scipy.integrate.solve_ivp for systems written as first-order ODEs:
    state = [q, q_dot]  ->  d(state)/dt = [q_dot, q_ddot]
"""

import numpy as np
from scipy.integrate import solve_ivp


def solve_second_order(rhs_func, t_span, y0, t_eval=None, **kwargs):
    """
    Solve a second-order ODE system rewritten as first-order.

    The state vector is [q1, q2, ..., qn, q1_dot, q2_dot, ..., qn_dot].
    rhs_func(t, state) should return [q1_dot, ..., qn_dot, q1_ddot, ..., qn_ddot].

    Parameters
    ----------
    rhs_func : callable
        Signature (t, y) -> dy/dt. y has shape (2*n,) for n generalized coordinates.
    t_span : tuple (t0, tf)
        Integration time span.
    y0 : array-like
        Initial state [q0, q_dot0] of shape (2*n,).
    t_eval : array-like, optional
        Times at which to store the solution.
    **kwargs
        Passed to scipy.integrate.solve_ivp.

    Returns
    -------
    Bunch
        Result from solve_ivp with attributes: t, y, success, message, etc.
    """
    return solve_ivp(
        rhs_func,
        t_span,
        np.asarray(y0, dtype=float),
        t_eval=t_eval,
        **kwargs
    )

"""
Numerical simulation using SciPy solve_ivp.
"""

import numpy as np
from scipy.integrate import solve_ivp


def simulate(system, y0, params, t_span, t_eval=None, **solve_ivp_kwargs):
    """
    Integrate dy/dt = system.rhs(t, y, params) from t_span[0] to t_span[1].

    Parameters
    ----------
    system : DynamicalSystem
        Must have .rhs(t, y, params) returning array of shape (dimension,).
    y0 : array-like
        Initial state, length system.dimension.
    params : dict
        Parameter values keyed by system.parameter_info.
    t_span : (float, float)
        (t_start, t_end).
    t_eval : array-like, optional
        Times at which to return the solution. If None, solver chooses.
    **solve_ivp_kwargs
        Passed to solve_ivp (e.g. method, rtol, atol).

    Returns
    -------
    t : ndarray
        Time points (from t_eval or solver output).
    y : ndarray
        Trajectory, shape (len(t), dimension).
    """
    y0 = np.asarray(y0, dtype=float)
    if y0.size != system.dimension:
        raise ValueError(f"y0 length {y0.size} != system dimension {system.dimension}")

    def rhs(t, y):
        return system.rhs(t, y, params)

    kwargs = {"dense_output": False, "method": "RK45"}
    kwargs.update(solve_ivp_kwargs)
    if t_eval is not None:
        kwargs["t_eval"] = np.asarray(t_eval)

    sol = solve_ivp(rhs, t_span, y0, **kwargs)
    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")

    t = sol.t
    y = sol.y.T  # (n_time, dimension)
    return t, y

"""Compute general (symbolic) solution of ODEs and systems. No initial/boundary values."""

import sympy as sp

from intuition_engine.ode.schemas import ParsedEquation


def _short_error(exc: Exception, max_len: int = 200) -> str:
    """Turn exception into a short user-facing message."""
    msg = str(exc).strip() or type(exc).__name__
    if "\n" in msg:
        msg = msg.split("\n")[0].strip()
    if len(msg) > max_len:
        msg = msg[: max_len - 3] + "..."
    return msg or "Unknown error"


def solve_ode(parsed: ParsedEquation) -> tuple:
    """Return (solution, error_message). solution is Eq or list of Eq, or None; error_message is None on success."""
    try:
        t = parsed.independent_variable
        func = parsed.dependent_function(t)
        sol = sp.dsolve(parsed.canonical_expr, func)
        if sol is not None:
            return (sol, None)
    except Exception as e:
        return (None, _short_error(e))
    return (None, None)


def solve_system(parsed_system) -> tuple:
    """Return (solution, error_message). solution is list of Eq or None; error_message is None on success."""
    try:
        t = parsed_system.independent_variable
        eqs = [
            sp.Eq(sp.diff(f(t), t), rhs)
            for f, rhs in parsed_system.equations
        ]
        funcs = [f(t) for f in parsed_system.state_vars]
        try:
            from sympy.solvers.ode.systems import dsolve_system
            sol_list = dsolve_system(eqs, funcs=funcs, t=t)
        except ImportError:
            sol_list = sp.dsolve(eqs, funcs)
        if sol_list is not None and len(sol_list) > 0:
            first = sol_list[0]
            sol = first if isinstance(first, (list, tuple)) else sol_list
            return (sol, None)
    except Exception as e:
        return (None, _short_error(e))
    return (None, None)

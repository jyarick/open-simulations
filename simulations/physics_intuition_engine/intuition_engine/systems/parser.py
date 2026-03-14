"""Parse systems of ODEs in normal form: d(x_i)/dt = rhs_i."""

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from intuition_engine.systems.schemas import ParsedSystem


def _normalize_equation_string(equation_str: str) -> str:
    return equation_str.replace("tdiff", "t*diff")


def _parse_side(expr_str: str, local_dict: dict) -> sp.Expr:
    try:
        expr = parse_expr(expr_str, local_dict=local_dict, evaluate=True)
    except Exception as e:
        raise ValueError(f"Could not parse expression: {expr_str}\nOriginal error: {e}")
    return sp.simplify(expr)


def build_symbol_dict_system_both():
    """Return (lhs_dict, rhs_dict) sharing the same t, x, y, z."""
    t = sp.symbols("t", real=True)
    x = sp.Function("x")
    y = sp.Function("y")
    z = sp.Function("z")
    a, b, c, k, m, r, alpha, beta = sp.symbols("a b c k m r alpha beta", real=True)
    base = {
        "sp": sp, "t": t, "a": a, "b": b, "c": c, "k": k, "m": m, "r": r, "alpha": alpha, "beta": beta,
        "diff": sp.diff, "cos": sp.cos, "sin": sp.sin,
        "exp": sp.exp, "sqrt": sp.sqrt, "pi": sp.pi,
        "Integer": sp.Integer, "Float": sp.Float, "Symbol": sp.Symbol,
    }
    lhs_dict = {**base, "x": x, "y": y, "z": z}
    rhs_dict = {**base, "x": x(t), "y": y(t), "z": z(t)}
    return lhs_dict, rhs_dict


def split_system_equations(equation_str: str) -> list:
    """Split input into equation strings by semicolon or newline."""
    equation_str = equation_str.strip()
    if not equation_str:
        raise ValueError("Empty input.")
    equation_str = equation_str.replace("\n", ";")
    parts = [p.strip() for p in equation_str.split(";") if p.strip()]
    if len(parts) < 2:
        raise ValueError("System must contain at least two equations (separate by ; or newline).")
    return parts


def parse_system(equation_str: str) -> ParsedSystem:
    """Parse a system of ODEs in normal form: d(x_i)/dt = rhs_i."""
    equation_str = _normalize_equation_string(equation_str.strip())
    local_dict_lhs, local_dict_rhs = build_symbol_dict_system_both()
    eq_strings = split_system_equations(equation_str)
    equations = []
    state_vars_ordered = []
    t = local_dict_lhs["t"]

    for eq_str in eq_strings:
        if eq_str.count("=") != 1:
            raise ValueError(f"Each equation must contain exactly one '='. Got: {eq_str}")
        lhs_str, rhs_str = eq_str.split("=", 1)
        lhs_str, rhs_str = lhs_str.strip(), rhs_str.strip()
        if not lhs_str or not rhs_str:
            raise ValueError(f"Empty side in equation: {eq_str}")
        lhs = _parse_side(lhs_str, local_dict_lhs)
        rhs = _parse_side(rhs_str, local_dict_rhs)
        rhs = sp.simplify(rhs)
        derivs = lhs.atoms(sp.Derivative)
        if not derivs:
            raise ValueError(f"LHS must be a first-order derivative (e.g. diff(x(t),t)). Got: {lhs_str}")
        d = next(iter(derivs))
        if d.derivative_count != 1 or len(d.variables) != 1:
            raise ValueError(f"LHS must be first derivative w.r.t. one variable. Got: {lhs_str}")
        if d.variables[0] != t:
            raise ValueError(f"Independent variable must be t. Got: {d.variables[0]}")
        state_func = d.expr.func
        state_vars_ordered.append(state_func)
        equations.append((state_func, rhs))

    state_vars_unique = []
    for sf, _ in equations:
        if sf not in state_vars_unique:
            state_vars_unique.append(sf)

    return ParsedSystem(
        raw_input=equation_str,
        equations=equations,
        state_vars=state_vars_unique,
        independent_variable=t,
    )

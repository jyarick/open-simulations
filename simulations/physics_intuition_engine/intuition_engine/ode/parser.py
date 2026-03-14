import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from intuition_engine.ode.schemas import ParsedEquation


def build_symbol_dict():
    t = sp.symbols("t", real=True)
    x = sp.Function("x")
    m, b, k, F0, omega, c = sp.symbols("m b k F0 omega c", real=True)
    local_dict = {
        "sp": sp, "t": t, "x": x, "m": m, "b": b, "k": k, "c": c,
        "F0": F0, "omega": omega, "diff": sp.diff, "cos": sp.cos, "sin": sp.sin,
        "exp": sp.exp, "sqrt": sp.sqrt, "pi": sp.pi,
        "Integer": sp.Integer, "Float": sp.Float, "Symbol": sp.Symbol,
    }
    return local_dict


def _normalize_equation_string(equation_str: str) -> str:
    """Fix common input so ODE is recognized (e.g. 'tdiff' -> 't*diff')."""
    return equation_str.replace("tdiff", "t*diff")


def split_equation(equation_str: str) -> tuple[str, str]:
    if equation_str.count("=") != 1:
        raise ValueError("Equation must contain exactly one '=' sign.")
    lhs_str, rhs_str = equation_str.split("=")
    lhs_str, rhs_str = lhs_str.strip(), rhs_str.strip()
    if not lhs_str or not rhs_str:
        raise ValueError("Both left-hand side and right-hand side must be non-empty.")
    return lhs_str, rhs_str


def parse_side(expr_str: str, local_dict: dict) -> sp.Expr:
    try:
        expr = parse_expr(expr_str, local_dict=local_dict, evaluate=True)
    except Exception as e:
        raise ValueError(f"Could not parse expression: {expr_str}\nOriginal error: {e}")
    return sp.simplify(expr)


def parse_equation(equation_str: str) -> ParsedEquation:
    equation_str = _normalize_equation_string(equation_str.strip())
    local_dict = build_symbol_dict()
    lhs_str, rhs_str = split_equation(equation_str)
    lhs = parse_side(lhs_str, local_dict)
    rhs = parse_side(rhs_str, local_dict)
    canonical_expr = sp.simplify(lhs - rhs)
    return ParsedEquation(
        raw_input=equation_str,
        lhs=lhs, rhs=rhs, canonical_expr=canonical_expr,
        dependent_function=local_dict["x"],
        independent_variable=local_dict["t"],
    )

import sympy as sp

from intuition_engine.ode.schemas import ParsedEquation, ExtractedFeatures
from intuition_engine.ode.classifier import get_derivatives


def extract_coefficients(parsed: ParsedEquation):
    expr = sp.expand(parsed.canonical_expr)
    t = parsed.independent_variable
    x = parsed.dependent_function(t)
    derivatives = sorted(get_derivatives(parsed), key=lambda d: d.derivative_count)
    x2 = next((d for d in derivatives if d.derivative_count == 2), None)
    x1 = next((d for d in derivatives if d.derivative_count == 1), None)
    a = expr.coeff(x2) if x2 else 0
    b = expr.coeff(x1) if x1 else 0
    c = expr.coeff(x)
    return a, b, c


def extract_forcing(parsed: ParsedEquation, a, b, c):
    expr = sp.expand(parsed.canonical_expr)
    t = parsed.independent_variable
    x = parsed.dependent_function(t)
    derivatives = sorted(get_derivatives(parsed), key=lambda d: d.derivative_count)
    dependent_part = a * next((d for d in derivatives if d.derivative_count == 2), 0) + b * next((d for d in derivatives if d.derivative_count == 1), 0) + c * x
    return sp.simplify(-sp.simplify(expr - dependent_part))


def extract_forcing_frequency(forcing):
    if forcing is None:
        return None
    if forcing.has(sp.cos) or forcing.has(sp.sin):
        args = list(forcing.atoms(sp.cos, sp.sin))
        if args:
            symbols = list(args[0].args[0].free_symbols)
            if symbols:
                return symbols[0]
    return None


def extract_features(parsed: ParsedEquation) -> ExtractedFeatures:
    a, b, c = extract_coefficients(parsed)
    forcing = extract_forcing(parsed, a, b, c)
    discriminant = sp.simplify(b**2 - 4*a*c)
    natural_frequency = sp.sqrt(c/a) if (a != 0 and c != 0) else None
    damping_ratio = (b / (2 * sp.sqrt(a*c))) if (a != 0 and c != 0) else None
    damping_timescale = (a / b) if b != 0 else None
    forcing_frequency = extract_forcing_frequency(forcing)
    r = sp.symbols("r")
    poly = a * r**2 + b * r + c
    try:
        roots = sp.solve(poly, r)
    except Exception:
        roots = None
    return ExtractedFeatures(a=a, b=b, c=c, forcing=forcing, discriminant=discriminant, natural_frequency=natural_frequency, damping_ratio=damping_ratio, damping_timescale=damping_timescale, forcing_frequency=forcing_frequency, characteristic_polynomial=poly, roots=roots)

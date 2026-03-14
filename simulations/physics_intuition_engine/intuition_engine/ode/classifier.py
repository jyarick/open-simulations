import sympy as sp

from intuition_engine.ode.schemas import ParsedEquation, EquationClassification


def get_derivatives(parsed: ParsedEquation):
    expr = parsed.canonical_expr
    dep_func = parsed.dependent_function(parsed.independent_variable)
    return [d for d in expr.atoms(sp.Derivative) if d.expr == dep_func]


def get_order(parsed: ParsedEquation) -> int:
    derivatives = get_derivatives(parsed)
    if not derivatives:
        return 0
    return max(d.derivative_count for d in derivatives)


def is_linear_in_function(parsed: ParsedEquation) -> bool:
    expr = sp.expand(parsed.canonical_expr)
    t = parsed.independent_variable
    x_t = parsed.dependent_function(t)
    replacements = {}
    dummy_symbols = [sp.Symbol("X0")]
    replacements[x_t] = dummy_symbols[0]
    for d in sorted(get_derivatives(parsed), key=lambda d: d.derivative_count):
        dn = sp.Symbol(f"X{d.derivative_count}")
        replacements[d] = dn
        dummy_symbols.append(dn)
    expr_sub = expr.subs(replacements)
    try:
        return sp.Poly(expr_sub, *dummy_symbols).total_degree() <= 1
    except sp.PolynomialError:
        return False


def has_constant_coefficients(parsed: ParsedEquation) -> bool:
    expr = sp.expand(parsed.canonical_expr)
    t = parsed.independent_variable
    x_t = parsed.dependent_function(t)
    basis_terms = [x_t] + sorted(get_derivatives(parsed), key=lambda d: d.derivative_count)
    for term in basis_terms:
        if expr.coeff(term).has(t):
            return False
    return True


def is_forced(parsed: ParsedEquation) -> bool:
    expr = sp.expand(parsed.canonical_expr)
    t = parsed.independent_variable
    x_t = parsed.dependent_function(t)
    basis_terms = [x_t] + sorted(get_derivatives(parsed), key=lambda d: d.derivative_count)
    dependent_part = sum(expr.coeff(term) * term for term in basis_terms)
    return sp.simplify(expr - dependent_part) != 0


def classify_equation(parsed: ParsedEquation) -> EquationClassification:
    notes = []
    order = get_order(parsed)
    linear = is_linear_in_function(parsed)
    const_coeffs = has_constant_coefficients(parsed) if linear else False
    if not linear:
        notes.append("Equation is not linear in the dependent function and its derivatives.")
    forced = is_forced(parsed)
    family = None
    if linear:
        if order == 2:
            if const_coeffs:
                family = "second_order_linear_constant_coeff_ode"
                notes.append("Equation matches the recognized second-order linear constant-coefficient family and includes forcing/input." if forced else "Equation matches the recognized second-order linear constant-coefficient family and is homogeneous.")
            else:
                family = "second_order_linear_time_varying_coeff_ode"
                notes.append("Equation is second-order linear but has coefficients that depend on time.")
        elif order == 1:
            if const_coeffs:
                family = "first_order_linear_constant_coeff_ode"
                notes.append("Equation is first-order linear with constant coefficients and includes forcing/input." if forced else "Equation is first-order linear with constant coefficients and is homogeneous.")
            else:
                family = "first_order_linear_time_varying_coeff_ode"
                notes.append("Equation is first-order linear but has coefficients that depend on time.")
    else:
        if order == 1:
            family = "first_order_nonlinear_ode"
            notes.append("Equation is first-order and nonlinear in the dependent function or its derivatives.")
        elif order == 2:
            family = "second_order_nonlinear_ode"
            notes.append("Equation is second-order and nonlinear in the dependent function or its derivatives.")
    if family is None:
        notes.append("Equation does not fully match any of the current recognized families.")
    return EquationClassification(order=order, is_linear=linear, has_constant_coefficients=const_coeffs, is_forced=forced, family=family, notes=notes)

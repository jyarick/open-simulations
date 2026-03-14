import pytest
import sympy as sp

from intuition_engine.pipeline import analyze_equation
from intuition_engine.examples import EXAMPLES, SYSTEM_EXAMPLES


def test_driven_damped_oscillator_supported():
    eq = EXAMPLES["Driven damped oscillator"]

    report = analyze_equation(eq)

    assert report.validation.is_supported is True
    assert report.validation.support_level == "full"
    assert report.classification.order == 2
    assert report.classification.is_linear is True
    assert report.classification.has_constant_coefficients is True


def test_undamped_oscillator_features():
    eq = EXAMPLES["Undamped oscillator"]

    report = analyze_equation(eq)
    features = report.features

    m, k = sp.symbols("m k", real=True)

    assert features.a == m
    assert features.c == k
    assert features.b == 0

    assert sp.simplify(features.natural_frequency - sp.sqrt(k / m)) == 0

def test_first_order_equation_supported():
    eq = "diff(x(t), t) + x(t) = 0"

    report = analyze_equation(eq)

    assert report.validation.is_supported is True
    assert report.validation.support_level == "partial"
    assert report.classification.order == 1
    assert report.classification.family == "first_order_linear_constant_coeff_ode"


def test_nonlinear_equation_warning():
    eq = "diff(x(t), t, 2) + x(t)**2 = 0"

    report = analyze_equation(eq)

    assert report.validation.is_supported is True
    assert report.validation.support_level == "partial"
    assert report.classification.is_linear is False
    assert report.classification.family == "second_order_nonlinear_ode"


def test_time_dependent_coeff_warning():
    eq = "diff(x(t), t, 2) + t*diff(x(t), t) + x(t) = 0"

    report = analyze_equation(eq)

    assert report.validation.is_supported is True
    assert report.validation.support_level == "partial"
    assert report.classification.has_constant_coefficients is False
    assert report.classification.family == "second_order_linear_time_varying_coeff_ode"


def test_linear_system_eigenvalues():
    eq = SYSTEM_EXAMPLES["Linear 2D (stable node)"]

    report = analyze_equation(eq)

    assert report.system_info is not None
    assert report.validation.support_level == "full"
    assert report.parsed_system is not None
    assert len(report.system_info.eigenvalues) == 2
    assert "Stable" in report.system_info.stability_summary
    assert report.classification.family == "linear_system_constant_coeff_ode"


def test_linear_system_eigenvectors_correct():
    """Eigenvectors must satisfy A*v = lambda*v."""
    eq = SYSTEM_EXAMPLES["Linear 2D (stable node)"]
    report = analyze_equation(eq)
    si = report.system_info
    A = si.matrix_A
    assert len(si.eigenvectors) == 2
    for ev, vects in si.eigenvectors:
        for v in vects:
            diff = sp.simplify(A * v - ev * v)
            assert diff == sp.zeros(*v.shape), "A*v should equal lambda*v"
    assert si.trace == -3
    assert si.determinant == 1


def test_empty_input_raises():
    """Empty or invalid input should raise ValueError."""
    with pytest.raises(ValueError):
        analyze_equation("")


def test_nonlinear_solution_may_be_none():
    """Nonlinear ODE may not have a computed solution; report should not crash."""
    eq = "diff(x(t), t, 2) + x(t)**2 = 0"
    report = analyze_equation(eq)
    assert report.validation.is_supported is True
    assert report.parsed is not None


def test_solution_error_none_when_solution_computed():
    """When a solution is computed, solution_error should be None."""
    eq = "diff(x(t), t) + x(t) = 0"
    report = analyze_equation(eq)
    assert report.solution is not None
    assert report.solution_error is None


def test_simple_linear_ode_has_solution():
    """Simple first-order linear ODE should have a general solution."""
    eq = "diff(x(t), t) + x(t) = 0"
    report = analyze_equation(eq)
    assert report.solution is not None
    assert report.validation.is_supported is True


def test_unrecognized_support_level():
    """Third-order ODE has no recognized family and should be unrecognized."""
    eq = "diff(x(t), t, 3) + diff(x(t), t) + x(t) = 0"
    report = analyze_equation(eq)
    assert report.validation.support_level == "unrecognized"
    assert report.validation.is_supported is False
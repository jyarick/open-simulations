"""
ODE subpackage: parse, classify, and explain ordinary differential equations.
Supports single ODEs and systems of first-order linear ODEs.
"""

import sympy as sp

from intuition_engine.ode.schemas import (
    ParsedEquation,
    EquationClassification,
    ExtractedFeatures,
    RegimeInsight,
    ValidationResult,
    ScalingFeatures,
    AnalysisReport,
)
from intuition_engine.ode.parser import parse_equation
from intuition_engine.ode.classifier import classify_equation
from intuition_engine.ode.validation import validate_classification
from intuition_engine.ode.extractors import extract_features
from intuition_engine.ode.regimes import build_regime_insights
from intuition_engine.ode.explain import build_full_summaries, build_physical_systems, build_physical_systems_for_system
from intuition_engine.ode.scaling import extract_scaling_features
from intuition_engine.systems import parse_system, extract_system_info
from intuition_engine.ode.solution import solve_ode, solve_system


def _is_system_input(equation_str: str) -> bool:
    """True if input looks like multiple equations (separated by ; or newline)."""
    s = equation_str.strip().replace("\n", ";")
    parts = [p.strip() for p in s.split(";") if p.strip()]
    return len(parts) >= 2


def analyze_equation(equation_str: str) -> AnalysisReport:
    """End-to-end analysis: single ODE or system of ODEs."""
    equation_str = equation_str.strip()
    if not equation_str:
        raise ValueError("Empty input.")

    if _is_system_input(equation_str):
        try:
            parsed_sys = parse_system(equation_str)
            sys_info = extract_system_info(parsed_sys)
            # Build a report with system_info; use first equation for parsed and minimal single-ode fields
            t = parsed_sys.independent_variable
            first_func, first_rhs = parsed_sys.equations[0]
            first_lhs = sp.diff(first_func(t), t)
            parsed = ParsedEquation(
                raw_input=parsed_sys.raw_input,
                lhs=first_lhs,
                rhs=first_rhs,
                canonical_expr=sp.simplify(first_lhs - first_rhs),
                dependent_function=first_func,
                independent_variable=t,
            )
            classification = EquationClassification(
                order=1,
                is_linear=True,
                has_constant_coefficients=sys_info.is_linear_constant,
                is_forced=any(sys_info.vector_b[i, 0] != 0 for i in range(sys_info.vector_b.rows)),
                family="linear_system_constant_coeff_ode",
                notes=["System of first-order linear ODEs in normal form."],
            )
            validation = ValidationResult(is_supported=True, support_level="full", warnings=[])
            features = ExtractedFeatures()
            scaling = ScalingFeatures()
            regimes = [RegimeInsight("System insight", insight, insight) for insight in sys_info.regime_insights]
            if not regimes:
                regimes = [RegimeInsight("Stability", sys_info.stability_summary, sys_info.stability_summary)]
            math_summary = f"System: d(state)/dt = A state + b. Eigenvalues: {sys_info.eigenvalues}. {sys_info.stability_summary}"
            physics_summary = sys_info.stability_summary + "\n" + "\n".join(sys_info.regime_insights)
            physical_systems = build_physical_systems_for_system()
            solution, solution_error = solve_system(parsed_sys)
            return AnalysisReport(
                parsed=parsed,
                classification=classification,
                validation=validation,
                features=features,
                scaling=scaling,
                regimes=regimes,
                physical_systems=physical_systems,
                math_summary=math_summary,
                physics_summary=physics_summary,
                parsed_system=parsed_sys,
                system_info=sys_info,
                solution=solution,
                solution_error=solution_error,
            )
        except ValueError:
            # Fall through to single-equation parsing
            pass

    # Single ODE
    parsed = parse_equation(equation_str)
    classification = classify_equation(parsed)
    validation = validate_classification(classification)
    features = extract_features(parsed)
    scaling = extract_scaling_features(features)
    regimes = build_regime_insights(features, classification)
    math_summary, physics_summary = build_full_summaries(parsed, classification, features, regimes)
    physical_systems = build_physical_systems(classification)
    solution, solution_error = solve_ode(parsed)
    return AnalysisReport(
        parsed=parsed,
        classification=classification,
        validation=validation,
        features=features,
        scaling=scaling,
        regimes=regimes,
        physical_systems=physical_systems,
        math_summary=math_summary,
        physics_summary=physics_summary,
        solution=solution,
        solution_error=solution_error,
    )


__all__ = [
    "analyze_equation",
    "parse_equation",
    "classify_equation",
    "ParsedEquation",
    "EquationClassification",
    "ExtractedFeatures",
    "RegimeInsight",
    "ValidationResult",
    "ScalingFeatures",
    "AnalysisReport",
]

from intuition_engine.ode.schemas import EquationClassification, ValidationResult

_FULL_SUPPORT_FAMILIES = frozenset({
    "second_order_linear_constant_coeff_ode",
    "linear_system_constant_coeff_ode",
})


def validate_classification(classification: EquationClassification) -> ValidationResult:
    family = classification.family
    if family is None:
        warnings = []
        if classification.order not in (1, 2):
            warnings.append(f"Expected a first- or second-order equation, but detected order {classification.order}.")
        if not classification.is_linear:
            warnings.append("Equation is nonlinear in the dependent function or its derivatives.")
        if not classification.has_constant_coefficients:
            warnings.append("Equation does not have constant coefficients with respect to the independent variable.")
        warnings.append("Equation is outside the currently recognized families of the engine.")
        return ValidationResult(is_supported=False, support_level="unrecognized", warnings=warnings)
    if family in _FULL_SUPPORT_FAMILIES:
        return ValidationResult(is_supported=True, support_level="full", warnings=[])
    return ValidationResult(is_supported=True, support_level="partial", warnings=[])

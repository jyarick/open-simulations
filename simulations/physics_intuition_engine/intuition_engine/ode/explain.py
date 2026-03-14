import sympy as sp

from intuition_engine.ode.schemas import (
    ParsedEquation,
    EquationClassification,
    ExtractedFeatures,
    RegimeInsight,
)


def _fmt(expr) -> str:
    if expr is None:
        return "None"
    return sp.sstr(expr)


def build_math_summary(parsed: ParsedEquation, classification: EquationClassification, features: ExtractedFeatures, regimes: list[RegimeInsight]) -> str:
    lines = [
        "Mathematical Summary", "--------------------",
        f"Canonical form: {_fmt(parsed.canonical_expr)} = 0",
        f"Order: {classification.order}", f"Linear: {classification.is_linear}",
        f"Constant coefficients: {classification.has_constant_coefficients}", f"Forced: {classification.is_forced}",
        f"Recognized family: {classification.family}",
        "", "Extracted coefficients:",
        f"  a = {_fmt(features.a)}", f"  b = {_fmt(features.b)}", f"  c = {_fmt(features.c)}", f"  forcing = {_fmt(features.forcing)}",
        "", "Derived quantities:",
        f"  discriminant = {_fmt(features.discriminant)}", f"  natural_frequency = {_fmt(features.natural_frequency)}",
        f"  damping_ratio = {_fmt(features.damping_ratio)}", f"  damping_timescale = {_fmt(features.damping_timescale)}",
        f"  forcing_frequency = {_fmt(features.forcing_frequency)}", f"  characteristic_polynomial = {_fmt(features.characteristic_polynomial)}", f"  roots = {_fmt(features.roots)}",
    ]
    if classification.notes:
        lines.extend(["", "Classifier notes:"] + [f"  - {n}" for n in classification.notes])
    if regimes:
        lines.extend(["", "Regime map:"] + [f"  - {r.label}: if {r.condition}" for r in regimes])
    return "\n".join(lines)


def build_physics_summary(parsed: ParsedEquation, classification: EquationClassification, features: ExtractedFeatures, regimes: list[RegimeInsight]) -> str:
    lines = ["Physics / Intuition Summary", "---------------------------"]
    if classification.family == "second_order_linear_constant_coeff_ode":
        a, b, c = features.a, features.b, features.c
        forcing, wn, zeta, tau_d, wf = features.forcing, features.natural_frequency, features.damping_ratio, features.damping_timescale, features.forcing_frequency
        lines.append("The equation has the archetypal second-order balance between an inertial-like term, a dissipative term, a restoring term, and an optional external drive.")
        lines.extend(["", "Term roles:", f"  - {_fmt(a)} * x''  -> inertial-like contribution", f"  - {_fmt(b)} * x'   -> damping / dissipation-like contribution", f"  - {_fmt(c)} * x    -> restoring / stiffness-like contribution"])
        lines.append(f"  - {_fmt(forcing)} -> external input / drive" if forcing and forcing != 0 else "  - No external forcing term detected")
        if wn: lines.extend(["", f"The natural oscillation scale is set by omega_n = {_fmt(wn)}."])
        if zeta: lines.append(f"The damping ratio zeta = {_fmt(zeta)} compares dissipation against oscillatory tendency.")
        if tau_d: lines.append(f"A transient decay timescale is roughly tau_d ~ {_fmt(tau_d)}.")
        if forcing and forcing != 0:
            lines.extend(["", "Because the system is driven, the long-time behavior is generally a competition between transient decay and forced steady-state response."])
            if wf and wn: lines.extend([f"When the drive frequency {_fmt(wf)} is far below {_fmt(wn)}, the system tends to follow the drive quasi-statically.", f"When the drive frequency {_fmt(wf)} is near {_fmt(wn)}, response enhancement becomes possible.", f"When the drive frequency {_fmt(wf)} is far above {_fmt(wn)}, inertia tends to suppress the displacement response."])
        lines.extend(["", "Behavioral interpretation:"] + [f"  - {r.label}: {r.meaning}" for r in regimes])
        return "\n".join(lines)
    if classification.family == "second_order_linear_time_varying_coeff_ode":
        a, b, c = features.a, features.b, features.c
        forcing, wn, zeta, tau_d, wf = features.forcing, features.natural_frequency, features.damping_ratio, features.damping_timescale, features.forcing_frequency
        lines.append("The equation is second-order and linear in x and its derivatives, but the inertial, damping, or restoring coefficients may change with time.")
        lines.extend(["", "Term roles (with possibly time-dependent coefficients):", f"  - {_fmt(a)} * x''  -> inertial-like contribution", f"  - {_fmt(b)} * x'   -> damping / dissipation-like contribution", f"  - {_fmt(c)} * x    -> restoring / stiffness-like contribution"])
        lines.append(f"  - {_fmt(forcing)} -> external input / drive" if forcing and forcing != 0 else "  - No external forcing term detected")
        if wn: lines.extend(["", "A natural oscillation scale omega_n(t) = sqrt(c/a) can be formed, but it generally varies with time."])
        if zeta: lines.append("A damping ratio zeta(t) = b / (2*sqrt(a*c)) compares dissipation against oscillatory tendency in a time-dependent way.")
        if tau_d: lines.append("A characteristic damping timescale tau_d(t) ~ a/b can also vary with time, so transient decay is not tied to a single fixed timescale.")
        if forcing and forcing != 0: lines.extend(["", "Because the system is driven and its parameters can vary, long-time behavior reflects a competition between evolving transient scales and the drive."])
        if regimes: lines.extend(["", "Behavioral interpretation (using instantaneous parameter values):"] + [f"  - {r.label}: {r.meaning}" for r in regimes])
        return "\n".join(lines)
    if classification.family == "first_order_linear_constant_coeff_ode":
        b, c, forcing = features.b, features.c, features.forcing
        lines.append("The equation describes a first-order balance between a rate-of-change term and a restoring / relaxation term, possibly with an external input.")
        lines.extend(["", "Term roles:", f"  - {_fmt(b)} * x'  -> relaxation / flow of the quantity", f"  - {_fmt(c)} * x   -> tendency to relax toward equilibrium"])
        lines.append(f"  - {_fmt(forcing)} -> external input / drive" if forcing and forcing != 0 else "  - No external forcing term detected")
        if b not in (0, None) and c not in (0, None): lines.extend(["", f"A characteristic relaxation timescale is roughly tau ~ {_fmt(b/c)}, set by the ratio of the rate coefficient to the restoring coefficient."])
        if forcing and forcing != 0: lines.extend(["", "Because the system is driven, the long-time behavior reflects a balance between transient relaxation and a forced steady state."])
        if regimes: lines.extend(["", "Behavioral interpretation:"] + [f"  - {r.label}: {r.meaning}" for r in regimes])
        return "\n".join(lines)
    if classification.family == "first_order_linear_time_varying_coeff_ode":
        b, c, forcing = features.b, features.c, features.forcing
        lines.append("The equation describes a first-order linear balance where the rate and restoring coefficients may change with time.")
        lines.extend(["", "Term roles (with possibly time-dependent coefficients):", f"  - {_fmt(b)} * x'  -> time-varying relaxation / flow of the quantity", f"  - {_fmt(c)} * x   -> time-varying tendency to relax toward (or away from) equilibrium"])
        lines.append(f"  - {_fmt(forcing)} -> external input / drive" if forcing and forcing != 0 else "  - No external forcing term detected")
        if b not in (0, None) and c not in (0, None): lines.extend(["", f"A local relaxation timescale tau(t) ~ {_fmt(b/c)} can be formed; as coefficients vary, this timescale changes in time."])
        if forcing and forcing != 0: lines.extend(["", "With forcing and time-dependent parameters, the system relaxes toward a moving steady state rather than a single fixed equilibrium."])
        if regimes: lines.extend(["", "Behavioral interpretation (using instantaneous parameter values):"] + [f"  - {r.label}: {r.meaning}" for r in regimes])
        return "\n".join(lines)
    lines.append("This equation is not fully inside the currently supported families, so the physical interpretation may be incomplete.")
    return "\n".join(lines)


def build_full_summaries(parsed: ParsedEquation, classification: EquationClassification, features: ExtractedFeatures, regimes: list[RegimeInsight]) -> tuple[str, str]:
    return build_math_summary(parsed, classification, features, regimes), build_physics_summary(parsed, classification, features, regimes)


def build_physical_systems(classification: EquationClassification) -> list[str]:
    """Return example physical systems that match this ODE form (by family)."""
    family = classification.family or ""
    if family == "second_order_linear_constant_coeff_ode":
        return [
            "Mass–spring oscillator (or spring–damper)",
            "Simple pendulum (small angle)",
            "LC circuit (inductor–capacitor)",
            "RLC circuit (with resistance)",
            "Mechanical vibrations (e.g. suspension, seismometer)",
        ]
    if family == "first_order_linear_constant_coeff_ode":
        return [
            "RC circuit (resistor–capacitor)",
            "RL circuit (resistor–inductor)",
            "Cooling/heating (Newton’s law)",
            "Radioactive decay",
            "Population growth or decay (linear rate)",
        ]
    if family == "second_order_linear_time_varying_coeff_ode":
        return [
            "Parametric oscillator (e.g. pendulum with varying length)",
            "Time-dependent mass or stiffness systems",
            "Mathieu-type equations (stability of periodic systems)",
        ]
    if family == "first_order_linear_time_varying_coeff_ode":
        return [
            "Systems with time-dependent rate or relaxation (e.g. varying resistance or conductance)",
            "Growth/decay with time-varying rate",
        ]
    if "nonlinear" in family:
        return [
            "Pendulum (large angle)",
            "Duffing oscillator (nonlinear spring)",
            "Population models (e.g. logistic)",
            "Nonlinear circuits or oscillators",
        ]
    return ["This equation does not match a known physical system in the engine."]


def build_physical_systems_for_system() -> list[str]:
    """Physical systems that can be described by linear first-order systems dx/dt = A x + b."""
    return [
        "Coupled oscillators (e.g. two masses and springs)",
        "Predator–prey (linearized Lotka–Volterra)",
        "Chemical reaction kinetics (linearized)",
        "Two-species competition or cooperation (linearized)",
        "RLC / LC circuits (state-space form)",
        "Damped harmonic oscillator (state-space: position and velocity)",
    ]

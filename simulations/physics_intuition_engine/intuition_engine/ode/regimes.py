import sympy as sp

from intuition_engine.ode.schemas import ExtractedFeatures, RegimeInsight, EquationClassification


def build_regime_insights(features: ExtractedFeatures, classification: EquationClassification) -> list[RegimeInsight]:
    insights: list[RegimeInsight] = []
    a, b, c = features.a, features.b, features.c
    forcing = features.forcing
    disc = features.discriminant
    wn = features.natural_frequency
    zeta = features.damping_ratio
    tau_d = features.damping_timescale
    wf = features.forcing_frequency
    family = classification.family or ""

    # Second-order oscillators
    if disc is not None and a not in (0, None) and c not in (0, None):
        insights.append(RegimeInsight("Overdamped regime", disc > 0, "Two distinct real characteristic roots; motion returns without oscillating."))
        insights.append(RegimeInsight("Critical damping", sp.Eq(disc, 0), "Repeated real root; fastest return to equilibrium without oscillation."))
        insights.append(RegimeInsight("Underdamped regime", disc < 0, "Complex-conjugate roots; decaying oscillations occur."))
    if wn is not None and a not in (0, None) and c not in (0, None):
        insights.append(RegimeInsight("Natural timescale", sp.Eq(sp.Symbol("omega_n"), wn), "Sets the system's intrinsic oscillation scale when damping and forcing do not dominate."))
    if zeta is not None and a not in (0, None) and c not in (0, None):
        insights.append(RegimeInsight("Weak damping", sp.Symbol("zeta") < 1, "Oscillations persist for many cycles before decaying significantly."))
        insights.append(RegimeInsight("Strong damping", sp.Symbol("zeta") > 1, "Dissipation dominates over oscillatory behavior."))
    if tau_d is not None and a not in (0, None) and c not in (0, None):
        t = sp.Symbol("t", real=True)
        insights.append(RegimeInsight("Transient decay", t > tau_d, "Initial-condition-driven transients are strongly suppressed at late times."))
    if forcing and forcing != 0 and wn and wf and a not in (0, None) and c not in (0, None):
        insights.append(RegimeInsight("Low-frequency forcing", wf < wn, "Response tends to track the drive quasi-statically."))
        insights.append(RegimeInsight("Near resonance (weak damping)", sp.Eq(wf, wn), "Response amplitude is enhanced because the drive matches the system's natural scale."))
        insights.append(RegimeInsight("High-frequency forcing", wf > wn, "Inertia suppresses displacement response; the system cannot follow the drive efficiently."))
    if forcing and forcing != 0 and tau_d and a not in (0, None) and c not in (0, None):
        t = sp.Symbol("t", real=True)
        insights.append(RegimeInsight("Steady-state dominance", t > tau_d, "The long-time behavior is dominated by the driven steady-state response rather than the transient homogeneous solution."))

    # First-order linear (constant or time-varying): b*x' + c*x = f(t)
    if a in (0, None) and b not in (0, None) and c not in (0, None) and "nonlinear" not in family:
        t = sp.Symbol("t", real=True)
        try:
            tau_relax = sp.Abs(b / c)
            insights.append(RegimeInsight("Relaxation timescale", t > tau_relax, "Initial-condition effects are strongly suppressed; the solution has largely relaxed toward its steady behavior."))
        except Exception:
            pass
        try:
            ratio = c / b
            insights.append(RegimeInsight("Stable relaxation", ratio > 0, "Solutions tend to decay toward an equilibrium configuration rather than grow without bound."))
            insights.append(RegimeInsight("Runaway tendency", ratio < 0, "The linear balance favors exponential growth away from equilibrium if the sign pattern of coefficients is realized."))
        except Exception:
            pass
        # Time-varying: add a generic insight so we always have at least one
        if "time_varying" in family:
            insights.append(RegimeInsight("Time-varying coefficients", "b(t), c(t)", "Relaxation rate and restoring strength depend on time; local behavior is still relaxation- or growth-like."))

    # Nonlinear
    if "nonlinear" in family and forcing is not None:
        A = sp.Symbol("A", real=True)
        try:
            nonlinear_terms = [p for p in forcing.atoms(sp.Pow) if isinstance(getattr(p, "exp", None), (int, sp.Integer)) and p.exp > 1]
            if nonlinear_terms:
                insights.append(RegimeInsight("Small-amplitude (weakly nonlinear) regime", sp.Lt(sp.Abs(A), 1), "When the effective amplitude A is small, nonlinear contributions are subdominant and the dynamics are close to the linearized equation."))
                insights.append(RegimeInsight("Strongly nonlinear regime", sp.Gt(sp.Abs(A), 1), "At large amplitudes, nonlinear terms dominate and the behavior can differ qualitatively from the linear prediction (e.g. amplitude-dependent frequencies or runaways)."))
        except Exception:
            pass

    return insights

import sympy as sp

from intuition_engine.ode.schemas import ExtractedFeatures, ScalingFeatures


def extract_scaling_features(features: ExtractedFeatures) -> ScalingFeatures:
    wn, zeta, wf = features.natural_frequency, features.damping_ratio, features.forcing_frequency
    notes = []
    if wn: notes.append("Natural frequency sets the intrinsic oscillation scale.")
    if zeta: notes.append("Damping ratio compares dissipative strength to oscillatory tendency.")
    forcing_ratio = sp.simplify(wf / wn) if (wf and wn) else None
    if forcing_ratio is not None:
        notes.extend(["Forcing ratio compares the drive frequency to the system's natural frequency.", "If forcing_ratio << 1, response is quasi-static.", "If forcing_ratio ~ 1, the system is in the resonance region.", "If forcing_ratio >> 1, inertia suppresses the displacement response."])
    return ScalingFeatures(natural_frequency=wn, damping_ratio=zeta, forcing_ratio=forcing_ratio, notes=notes)

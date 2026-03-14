"""Extract matrix A, vector b, eigenvalues, and stability from a parsed linear system."""

import sympy as sp

from intuition_engine.systems.schemas import ParsedSystem, SystemInfo


def _extract_A_and_b(parsed: ParsedSystem) -> tuple:
    t = parsed.independent_variable
    state_vars = parsed.state_vars
    state_exprs = [f(t) for f in state_vars]
    n_rows = len(parsed.equations)
    n_cols = len(state_vars)
    A = sp.Matrix(n_rows, n_cols, lambda i, j: 0)
    b = sp.Matrix(n_rows, 1, lambda i, _: 0)

    for i, (state_func, rhs) in enumerate(parsed.equations):
        rhs = sp.expand(rhs)
        for j, xj in enumerate(state_exprs):
            A[i, j] = sp.simplify(rhs.coeff(xj))
        linear_part = sum(A[i, j] * state_exprs[j] for j in range(n_cols))
        b[i, 0] = sp.simplify(rhs - linear_part)

    return A, b


def _is_linear_constant(parsed: ParsedSystem, A: sp.Matrix, b: sp.Matrix) -> bool:
    t = parsed.independent_variable
    for i in range(A.rows):
        for j in range(A.cols):
            if A[i, j].has(t):
                return False
        if b[i, 0].has(t):
            return False
    return True


def _eigenvalues_list(A: sp.Matrix) -> list:
    try:
        evals = A.eigenvals()
        result = []
        for ev, mult in evals.items():
            for _ in range(mult):
                result.append(ev)
        return result
    except Exception:
        return []


def _eigenvectors_list(A: sp.Matrix) -> list:
    """Return [(eigenvalue, [v1, v2, ...]), ...] for each eigenvalue.
    Each v is a column Matrix satisfying A*v = eigenvalue*v (standard sympy eigenvects format).
    """
    try:
        eigens = A.eigenvects()
        result = [(ev, list(vects)) for ev, _mult, vects in eigens]
        return result
    except Exception:
        return []


def _stability_summary(eigenvalues: list) -> str:
    if not eigenvalues:
        return "Could not compute eigenvalues (matrix may be symbolic or defective)."
    re_vals = []
    im_vals = []
    for ev in eigenvalues:
        try:
            re_ev = sp.re(ev).simplify()
            im_ev = sp.im(ev).simplify()
            re_vals.append(re_ev)
            im_vals.append(im_ev)
        except Exception:
            re_vals.append(None)
            im_vals.append(None)
    all_neg = all(r is not None and r.is_negative for r in re_vals)
    any_pos = any(r is not None and r.is_positive for r in re_vals)
    any_zero = any(r is not None and r.is_zero for r in re_vals)
    has_imag = any(im is not None and im != 0 for im in im_vals)
    if any_pos:
        return "Unstable: at least one eigenvalue has positive real part."
    if all_neg and has_imag:
        return "Stable spiral/focus: all eigenvalues have negative real part and nonzero imaginary part (decaying oscillations)."
    if all_neg:
        return "Stable node: all eigenvalues have negative real part (no oscillation)."
    if any_zero:
        return "Marginally stable / critical: at least one eigenvalue has zero real part."
    return "Stability depends on parameter values (eigenvalues are symbolic)."


def _regime_insights_from_eigenvalues(eigenvalues: list) -> list:
    insights = []
    if not eigenvalues:
        return insights
    re_vals = [sp.re(ev).simplify() for ev in eigenvalues]
    im_vals = [sp.im(ev).simplify() for ev in eigenvalues]
    if len(eigenvalues) == 2:
        r1, r2 = re_vals[0], re_vals[1]
        i1, i2 = im_vals[0], im_vals[1]
        try:
            if r1.is_negative and r2.is_negative and (i1 != 0 or i2 != 0):
                insights.append("Two eigenvalues with negative real part and nonzero imaginary part → stable spiral (decaying oscillations in the phase plane).")
            elif r1.is_negative and r2.is_negative and i1 == 0 and i2 == 0:
                insights.append("Two real negative eigenvalues → stable node (all trajectories approach equilibrium without oscillation).")
            elif (r1.is_positive and r2.is_negative) or (r1.is_negative and r2.is_positive):
                insights.append("Eigenvalues of opposite sign → saddle point (unstable; one direction grows, one decays).")
            elif r1.is_positive and r2.is_positive:
                insights.append("Two positive real eigenvalues → unstable node (trajectories diverge from equilibrium).")
        except Exception:
            insights.append("Eigenvalue structure determines phase portrait (node, spiral, saddle, or center).")
    else:
        try:
            if all(r.is_negative for r in re_vals):
                insights.append("All eigenvalues have negative real part → stable equilibrium.")
            elif any(r.is_positive for r in re_vals):
                insights.append("At least one eigenvalue has positive real part → unstable equilibrium.")
        except Exception:
            insights.append("Stability and phase portrait depend on the sign of eigenvalue real parts.")
    return insights


def extract_system_info(parsed: ParsedSystem) -> SystemInfo:
    """Compute matrix A, vector b, eigenvalues, and stability for a linear system."""
    notes = []
    A, b = _extract_A_and_b(parsed)
    is_linear_constant = _is_linear_constant(parsed, A, b)
    if not is_linear_constant:
        notes.append("Coefficients depend on t; eigenvalues and stability refer to the frozen coefficient matrix.")

    eigenvalues = _eigenvalues_list(A)
    eigenvectors = _eigenvectors_list(A)
    try:
        trace_A = sp.simplify(A.trace())
    except Exception:
        trace_A = None
    try:
        det_A = sp.simplify(A.det())
    except Exception:
        det_A = None
    stability_summary = _stability_summary(eigenvalues)
    regime_insights = _regime_insights_from_eigenvalues(eigenvalues)
    state_names = [str(f.name) for f in parsed.state_vars]

    return SystemInfo(
        matrix_A=A,
        vector_b=b,
        state_names=state_names,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        trace=trace_A,
        determinant=det_A,
        stability_summary=stability_summary,
        regime_insights=regime_insights,
        is_linear_constant=is_linear_constant,
        notes=notes,
    )

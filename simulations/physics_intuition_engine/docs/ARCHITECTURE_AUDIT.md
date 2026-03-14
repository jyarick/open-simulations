# Physics Intuition Engine — Architecture Audit

**Date:** 2025-03-08  
**Scope:** Repo hygiene, parsers, classification, feature extraction, regime logic, validation honesty, scalar vs system architecture, error handling, tests, README.  
**Constraint:** Preserve current shipped behavior; staged fixes only; no full rewrite.

---

## Executive summary

The codebase is coherent and the split between **ode/** (scalar ODEs) and **systems/** (linear systems) is clear. The main gaps are: **(1)** validation conflates “recognized” with “fully supported”; **(2)** one overloaded report schema for both scalar and system; **(3)** parsers and feature extraction are hard-coded to specific names and forms; **(4)** silent exception swallowing in solution and some extractors; **(5)** missing tests for edge cases and partial analysis; **(6)** minor hygiene (requirements.txt, .gitignore, leftover “v1” wording). The engine’s identity as a **physics-interpretation** tool (regimes, physical systems, summaries) is well preserved; recommendations below keep that focus and add clarity about support levels.

---

## A. Repo / package hygiene

| Check | Status | Notes |
|-------|--------|--------|
| venv / __pycache__ / .ipynb_checkpoints / .DS_Store tracked? | **Confirmed OK** | `.gitignore` lists them; `git ls-files` shows none of these tracked. |
| .pytest_cache | **Confirmed issue** | `.gitignore` does **not** include `.pytest_cache/`; directory exists and should be ignored. |
| requirements.txt | **Confirmed issue** | File is **empty**. Code uses `sympy` only (and notebook uses `ipywidgets`, `jupyter`). Dependencies should be pinned. |
| Naming / layout | **Likely OK** | `assets/` exists with `demo.png`; `intuition_engine/` is the package; `ode/` and `systems/` subpackages are clear. Root `intuition_engine/schemas.py` re-exports from `ode.schemas` — redundant but harmless. |

**Recommendations:**
- **Phase 1:** Add `.pytest_cache/` to `.gitignore`. Populate `requirements.txt` with at least `sympy` (and optional: `jupyter`, `ipywidgets` for the notebook).
- **Future:** Consider dropping root `intuition_engine/schemas.py` and importing from `intuition_engine.ode.schemas` everywhere to avoid two sources of truth.

---

## B. Parser audit

**ODE parser** (`intuition_engine/ode/parser.py`):
- **Hard-coded:** `build_symbol_dict()` fixes exactly `t`, `x`, and a fixed set of symbols (`m, b, k, F0, omega, c`). Any other symbol (e.g. `gamma`, `alpha`) in the equation will be parsed as an undefined symbol and may fail or behave oddly.
- **Assumption:** Exactly one `=`; LHS and RHS parse with the same dict. Dependent variable is always the single function `x` from the dict (i.e. “one dependent variable, named x”).
- **Fragile:** `_normalize_equation_string` only does `tdiff` → `t*diff`. No handling of other common typos or implicit multiplication.
- **Confirmed issue:** Parser cannot generalize to user-chosen names (e.g. `y(t)` as dependent, or `tau` as independent) without code change.

**Systems parser** (`intuition_engine/systems/parser.py`):
- **Hard-coded:** State variables are exactly `x`, `y`, `z` (from `build_symbol_dict_system_both`). RHS must use `x`, `y`, `z` (interpreted as `x(t)`, `y(t)`, `z(t)`). Independent variable must be `t`.
- **Assumption:** Each equation has LHS = first derivative of one of these (e.g. `diff(x(t),t)`); order of equations determines state order.
- **Likely issue:** More than three state variables (e.g. `w`) would require parser change. No way to use different names (e.g. `u`, `v`) without editing code.

**Recommendations:**
- **Phase 1:** Document in docstrings: “Supported input: single dependent variable `x(t)` and independent variable `t`” (ODE); “State variables must be `x`, `y`, `z`; independent variable `t`” (systems). No code change required for “small safe fixes.”
- **Phase 2:** Introduce a small “vocabulary” config (e.g. independent var name, list of state/dependent names) used by both parsers; keep default `t` and `x`/`x,y,z` so current behavior is unchanged.
- **Phase 3:** Optional: infer dependent/state vars from the equation string (e.g. from `diff(...)` appearances) and build the symbol dict dynamically.

---

## C. Classification design

**Current behavior** (`ode/classifier.py`):
- Classification is **structural/syntax-level**: order (from derivative counts), linearity (degree in substituted expression), constant vs time-varying (coefficients `.has(t)`), forced (non-zero remainder). Family is then a label from these booleans.
- **Not physical:** No notion of “oscillator,” “dissipative,” etc.; only “second_order_linear_constant_coeff_ode” etc. Physical interpretation is delegated to `explain.py` and `build_physical_systems`.
- **Confirmed issue:** Classifier notes still say “Equation matches the **v1 family**” for second-order constant-coeff — outdated wording.
- **Likely issue:** Order 0 is possible (no derivatives found) but family stays `None`; no explicit “order 0” or “algebraic” branch. High-order (3+) falls into “family is None.”

**Recommendations:**
- **Phase 1:** Replace “v1 family” with “recognized second-order linear constant-coefficient family” (or similar) in `classifier.py` notes.
- **Phase 2:** Add an optional `classification_tier` or keep family but add a short doc in `schemas.py`: “Family is a structural label; physical interpretation is in explain/regimes.”
- **Future:** If you add more families (e.g. Bernoulli, exact), extend the same pattern (order, linearity, const_coeff, then family string) so classification stays incremental.

---

## D. Feature extraction design

**Current behavior** (`ode/extractors.py`):
- **Single schema:** `ExtractedFeatures` has `a, b, c` (coefficients of x'', x', x), discriminant, natural_frequency, damping_ratio, damping_timescale, forcing_frequency, characteristic_polynomial, roots. This is **oscillator-centric** (second-order a*x''+b*x'+c*x).
- **Overloading:** For first-order equations, `a=0`; for nonlinear, discriminant/roots may still be computed from the same formula but interpretation is not necessarily valid. Scaling (`ode/scaling.py`) uses `natural_frequency`, `damping_ratio`, `forcing_ratio` — again oscillator-oriented.
- **Systems:** Do not use `ExtractedFeatures` for the system path; they use `SystemInfo` (matrix_A, vector_b, eigenvalues, etc.). So scalar ODEs overload one schema; systems have their own. No shared “base features” type.

**Recommendations:**
- **Phase 1:** In `ExtractedFeatures` docstring (or a short comment at top of `extractors.py`), state: “Schema is oriented to second-order linear oscillator form a*x''+b*x'+c*x=f; for first-order or nonlinear, many fields may be None or only loosely meaningful.”
- **Phase 2:** Consider a small “feature tier” in the report: e.g. `features_tier: "oscillator" | "first_order" | "generic"` and have the UI/doc note when interpretation is strongest (oscillator) vs partial (first_order/generic). No need to split schemas yet.
- **Phase 3:** If you add more families (e.g. Bernoulli), consider a base `ExtractedFeatures` with only `a, b, c, forcing` and family-specific extensions (e.g. `OscillatorFeatures(ExtractedFeatures)` with omega_n, zeta, etc.) so the main report can carry a union type.

---

## E. Regime logic

**Current behavior** (`ode/regimes.py`):
- Regime conditions are **symbolic** (e.g. `disc > 0`, `sp.Eq(sp.Symbol("zeta"), zeta)`) or string (e.g. `"b(t), c(t)"` for time-varying). Stored as `RegimeInsight(label, condition, meaning)`.
- **Inconsistency:** Some conditions are sympy expressions, others are strings. The UI tries `Math(safe_latex(r.condition))` and falls back to Markdown; for string conditions this is fine but the mix is a bit fragile.
- **Semantics:** Second-order branch uses `disc`, `wn`, `zeta`, `tau_d` from features; first-order uses `b/c` and ratio; nonlinear uses a generic `A` (amplitude). So regime logic is **family-aware** and uses derived quantities where available.
- **Likely issue:** For first-order time-varying, `tau_relax = sp.Abs(b/c)` can be symbolic (e.g. `|t|`); “Relaxation timescale” condition `t > tau_relax` may be odd. No bug, but explanation could note “time-dependent scale.”

**Recommendations:**
- **Phase 1:** Add a one-line comment in `RegimeInsight` (in `ode/schemas.py`): “condition may be a sympy expression or a string for display.”
- **Phase 2:** Optionally normalize: always store a string “condition_for_display” for the UI and keep a separate optional sympy “condition_expr” for future use (e.g. numerical checks). Low priority.
- **Future:** If you add more families, keep regime building per-family in one place (e.g. `regimes.py` with explicit branches per family) so it doesn’t become spaghetti.

---

## F. Validation / support honesty

**Current behavior** (`ode/validation.py`):
- `is_supported = True` **iff** `classification.family is not None`. So “supported” means “recognized into a known family,” not “we fully analyze every aspect.”
- Nonlinear and time-varying equations still get `family` set (e.g. `first_order_nonlinear_ode`) and hence `is_supported=True`, but feature extraction and regime coverage are partial (e.g. no omega_n for nonlinear).

**Confirmed issue:** The UI and docs use “fully supported” vs “partially supported,” but validation only distinguishes “has family” vs “no family.” So “fully supported” is overstated for nonlinear and time-varying.

**Recommendations:**
- **Phase 1:** Introduce a clearer semantics and keep current behavior:
  - Add to `ValidationResult`: e.g. `support_level: "full" | "partial" | "unrecognized"` where `full` = recognized family **and** we have full feature/regime coverage (e.g. second-order linear constant-coeff, or linear systems); `partial` = recognized but limited interpretation; `unrecognized` = no family.
  - Derive it from `classification.family` plus a small rule (e.g. full only for `second_order_linear_constant_coeff_ode` and `linear_system_constant_coeff_ode`; partial for the rest with a family; unrecognized when family is None).
  - In the UI, map “full” → “fully supported,” “partial” → “partially supported (recognized; interpretation may be incomplete),” “unrecognized” → current “partially supported” + warnings. No change to what we compute, only to what we claim.
- **Phase 2:** Add a short “Support” section in the README: “Fully analyzed: second-order linear constant-coefficient ODEs and linear first-order systems. Recognized but partially interpreted: first-order linear (constant or time-varying), second-order time-varying, nonlinear.”

---

## G. Scalar ODE vs system architecture

**Current behavior:**
- **One report type:** `AnalysisReport` holds both scalar-ODE fields (parsed, features, scaling, regimes, …) and optional `parsed_system`, `system_info`. For systems, we still fill `parsed` (first equation), `features` (empty), `scaling` (empty), `regimes` (from system insights), so the same schema is used for both.
- **Pros:** Single entry point; UI and callers branch on `report.system_info is not None`. No API break.
- **Cons:** For systems, `features` and `scaling` are meaningless; `parsed` is a stand-in for “first equation.” So the report is a union type in disguise.

**Recommendations:**
- **Phase 1:** Document in `AnalysisReport` docstring: “For scalar ODEs, parsed/features/scaling/regimes are primary; for systems, parsed_system/system_info are primary and features/scaling are placeholders.”
- **Phase 2:** Optionally add `report_type: "scalar_ode" | "system"` (or infer from `system_info is not None`) so downstream code and docs can refer to it explicitly. No schema split yet.
- **Phase 3:** If the codebase grows, consider a tagged union: e.g. `AnalysisReport(scalar=ScalarODEResult(...))` or `AnalysisReport(system=SystemResult(...))` with a single top-level discriminator. Not required for current scope.

---

## H. Error handling / transparency

**Current behavior:**
- **Parsers:** Raise `ValueError` with clear messages (e.g. “Equation must contain exactly one '='”). Good.
- **Solution** (`ode/solution.py`): `solve_ode` and `solve_system` catch all `Exception` and return `None`. Caller and UI show “No general solution computed” but do not report *why* (e.g. “NotImplementedError: solver not available for this form”).
- **Extractors:** `extract_features` uses `try: roots = sp.solve(...)` and sets `roots = None` on exception; no log or status. Same pattern in systems `_eigenvalues_list`, `_eigenvectors_list` (return [] on exception).
- **System path:** If `parse_system` or `extract_system_info` raises (e.g. non-linear RHS), we catch only `ValueError` in `analyze_equation` and fall back to scalar parsing; other exceptions propagate. So system detection is “try system, on ValueError treat as scalar.”

**Recommendations:**
- **Phase 1:** In `solution.py`, on exception optionally attach a simple reason to the return (e.g. return a small object `(None, str(e))` or a dataclass `SolutionResult(success=False, error=str(e))`) and have the UI show “No general solution: <reason>” when present. Alternatively keep returning `None` but log the exception (e.g. `logging.debug`) so developers can see failures.
- **Phase 2:** Add an optional `analysis_notes: List[str]` to the report (e.g. “Solution attempt failed: …”) so partial analyses can surface solution failures without breaking the pipeline.
- **Future:** Consider a `ParseResult` / `AnalysisResult` that can be `Ok(report)` or `Err(message, partial)` so callers can distinguish “no solution” from “parse failed” from “full success.”

---

## I. Tests

**Current coverage** (`tests/test_cases.py`):
- Happy path: driven damped oscillator (supported, order 2, linear, const coeff); undamped (features a, b, c, natural_frequency); first-order constant-coeff; nonlinear (family and supported); time-varying coeff; linear system (eigenvalues, stability, family); system eigenvectors (A*v = λ*v, trace, det).
- **Missing:**
  - **Malformed input:** Empty string; multiple `=`; invalid tokens; missing `diff` on LHS for systems.
  - **Unsupported forms:** Order 0; order 3+; system with only one equation (semicolon but one eq); system with non-linear RHS.
  - **Partial analysis:** Nonlinear equation — confirm solution is None or that we don’t crash; time-varying — confirm solution may be None.
  - **Symbolic parameters:** Already have symbolic m, k, etc.; could add one test that solution is not None for a simple linear ODE with symbols.
  - **Edge cases:** Repeated eigenvalues (e.g. 2x2 with single eigenvalue); system with 3 state vars (x, y, z).

**Recommendations:**
- **Phase 1:** Add tests: empty input raises; single-equation “system” (one semicolon-separated part) raises or is treated as scalar; nonlinear ODE returns report with solution possibly None; one test that a simple constant-coeff ODE has solution not None.
- **Phase 2:** Add tests for malformed system (e.g. LHS not a derivative); unsupported order (e.g. order 3); system with 3 equations (x, y, z) to ensure parser/extract still work.
- **Phase 3:** Add tests for “partial” support (e.g. assert support_level or validation message when family is nonlinear).

---

## J. README / scope honesty

**Current README:** Already describes single ODEs and systems, installation with venv, and usage. Scope section mentions “strongest support” and “deepest interpretation” but the wording is a bit run-on (lines 35–37).

**Recommendations:**
- **Phase 1:** Tidy Scope into a short list: (1) Strongest support: second-order linear constant-coefficient ODEs; linear first-order systems in normal form. (2) Recognized but partial interpretation: first-order linear (constant or time-varying), second-order time-varying, nonlinear. (3) Input format: one equation or multiple separated by `;`/newline. Fix the run-on and add a line that “fully supported” in the UI means “full interpretation available” for the above strongest cases.
- **Phase 2:** After adding `support_level` (F), add one sentence: “The UI labels each result as fully supported, partially supported, or unrecognized depending on how much interpretation is available.”

---

## Prioritized fix plan

### Phase 1 — Small, safe fixes (no behavior change)

| # | Item | Action |
|---|------|--------|
| 1 | .gitignore | Add `.pytest_cache/` (and optionally `*.egg-info/`, `dist/`, `build/` if you want). |
| 2 | requirements.txt | Add `sympy` (and optionally `jupyter`, `ipywidgets` for notebook). |
| 3 | Classifier wording | In `ode/classifier.py`, replace “v1 family” with “recognized second-order linear constant-coefficient family” (or similar). |
| 4 | Docstrings | Parser files: state supported variable names (t, x for ODE; t, x, y, z for systems). ExtractedFeatures: note oscillator-oriented schema. RegimeInsight: note condition can be sympy or string. AnalysisReport: note system path uses placeholder features/scaling. |
| 5 | README Scope | Clean up run-on; list strongest support vs partial vs input format. |
| 6 | Tests | Add: empty input raises; nonlinear report has solution possibly None; simple linear ODE has solution not None. |

### Phase 2 — Medium refactors (minimal API impact)

| # | Item | Action |
|---|------|--------|
| 7 | Validation honesty | Add `support_level: "full" | "partial" | "unrecognized"` to ValidationResult; set it from family + simple rules; update UI text to use it. |
| 8 | Solution transparency | Return a small result object or add report field for “solution attempt failed: …” (or log); UI shows reason when solution is None. |
| 9 | Optional report_type | Add `report_type: "scalar_ode" | "system"` (or derived from system_info) to AnalysisReport and document. |
| 10 | Parser vocabulary | Introduce a config dict (default t, x or x,y,z) for parser symbol dicts; use it in both parsers without changing default behavior. |
| 11 | Tests | Add malformed input tests; unsupported order; system with 3 states; partial-support assertion. |

### Phase 3 — Future expansion enablers

| # | Item | Action |
|---|------|--------|
| 12 | Family-specific features | Consider base ExtractedFeatures + optional family-specific payload (e.g. OscillatorFeatures) when adding new families. |
| 13 | Tagged report | Consider AnalysisReport as a tagged union (scalar vs system) if the codebase grows. |
| 14 | Parser inference | Optional: infer dependent/state names from equation string and build symbol dict dynamically. |
| 15 | ParseResult / AnalysisResult | Optional: Result type for parse/analyze so callers can handle Err(partial) explicitly. |

---

## File-by-file summary

| File | Confirmed issue | Likely / future |
|------|------------------|------------------|
| `.gitignore` | Add `.pytest_cache/` | — |
| `requirements.txt` | Empty; add sympy (and optional deps) | — |
| `ode/classifier.py` | “v1 family” wording | Optional classification_tier or doc |
| `ode/parser.py` | Doc: supported names t, x | Phase 2 vocabulary config |
| `ode/validation.py` | is_supported = “recognized”; add support_level | — |
| `ode/schemas.py` | — | RegimeInsight condition note; AnalysisReport doc |
| `ode/extractors.py` | — | Doc: oscillator-oriented schema |
| `ode/regimes.py` | — | Comment on condition type |
| `ode/solution.py` | Exceptions swallowed; no reason returned | Return or log reason |
| `ode/__init__.py` | — | Document system path placeholder fields |
| `systems/parser.py` | Doc: x, y, z, t only | Vocabulary config; >3 states |
| `pipeline.py` | — | — |
| `README.md` | Scope run-on; clarify support | Add support_level sentence after Phase 2 |
| `tests/test_cases.py` | Missing edge-case tests | Malformed, unsupported, partial, 3-state |

---

## Minimal code patches (Phase 1 only)

Below are concrete, minimal edits for Phase 1 only. No logic changes to classification, validation, or feature extraction.

1. **.gitignore** — append:
   ```
   .pytest_cache/
   ```

2. **requirements.txt** — set content to:
   ```
   sympy>=1.10
   ```
   (Optional: add `jupyter`, `ipywidgets` for the notebook.)

3. **ode/classifier.py** — replace the two notes that say “v1 family” with:
   - “Equation matches the recognized second-order linear constant-coefficient family and includes forcing/input.” (and same for homogeneous).

4. **README.md** — in Scope, replace the run-on with:
   - “**Strongest support:** second-order linear constant-coefficient ODEs; linear first-order systems in normal form. **Recognized with partial interpretation:** first-order linear (constant or time-varying), second-order time-varying, nonlinear. **Input:** one equation, or multiple equations separated by `;` or newline for systems.”

5. **tests/test_cases.py** — add:
   - `test_empty_input_raises`: `pytest.raises(ValueError, analyze_equation, "")`.
   - `test_nonlinear_solution_may_be_none`: analyze `diff(x(t),t,2)+x(t)**2=0`, assert report.solution is None or report has solution (no crash).
   - `test_simple_linear_ode_has_solution`: analyze `diff(x(t),t)+x(t)=0`, assert report.solution is not None.

No other files need code changes for Phase 1 beyond docstrings; docstring additions can be one-line each as suggested in the table.

---

**End of audit.**

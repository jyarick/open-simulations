from dataclasses import dataclass, field
from typing import Optional, List, Any, Literal
import sympy as sp


@dataclass
class ParsedEquation:
    raw_input: str
    lhs: sp.Expr
    rhs: sp.Expr
    canonical_expr: sp.Expr          # lhs - rhs
    dependent_function: sp.Function
    independent_variable: sp.Symbol


@dataclass
class EquationClassification:
    order: Optional[int]
    is_linear: bool
    has_constant_coefficients: bool
    is_forced: bool
    family: Optional[str]
    notes: List[str] = field(default_factory=list)


@dataclass
class ExtractedFeatures:
    a: Optional[sp.Expr] = None
    b: Optional[sp.Expr] = None
    c: Optional[sp.Expr] = None
    forcing: Optional[sp.Expr] = None
    discriminant: Optional[sp.Expr] = None
    natural_frequency: Optional[sp.Expr] = None
    damping_ratio: Optional[sp.Expr] = None
    damping_timescale: Optional[sp.Expr] = None
    forcing_frequency: Optional[sp.Expr] = None
    characteristic_polynomial: Optional[sp.Expr] = None
    roots: Optional[List[sp.Expr]] = None


@dataclass
class RegimeInsight:
    label: str
    condition: Any
    meaning: str


@dataclass
class ValidationResult:
    """support_level: full = full interpretation; partial = recognized but limited; unrecognized = no family."""
    is_supported: bool
    support_level: Literal["full", "partial", "unrecognized"] = "unrecognized"
    warnings: List[str] = field(default_factory=list)


@dataclass
class ScalingFeatures:
    natural_frequency: Optional[sp.Expr] = None
    damping_ratio: Optional[sp.Expr] = None
    forcing_ratio: Optional[sp.Expr] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    parsed: ParsedEquation
    classification: EquationClassification
    validation: ValidationResult
    features: ExtractedFeatures
    scaling: ScalingFeatures
    regimes: List[RegimeInsight]
    physical_systems: List[str]
    math_summary: str
    physics_summary: str
    parsed_system: Optional[Any] = None
    system_info: Optional[Any] = None
    solution: Optional[Any] = None  # general solution: Eq, list of Eq, or message str
    solution_error: Optional[str] = None  # reason solution is None when attempt was made

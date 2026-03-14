"""Data structures for linear systems of ODEs (matrix A, vector b, eigenvalues)."""

from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional
import sympy as sp


@dataclass
class ParsedSystem:
    """Parsed system of ODEs in normal form: d(x_i)/dt = rhs_i."""
    raw_input: str
    equations: List[Tuple[sp.Function, sp.Expr]]
    state_vars: List[sp.Function]
    independent_variable: sp.Symbol


@dataclass
class SystemInfo:
    """Analysis result for a linear constant-coefficient system dx/dt = A x + b."""
    matrix_A: sp.Matrix
    vector_b: sp.Matrix
    state_names: List[str]
    eigenvalues: List[Any]
    eigenvectors: List[Tuple[Any, List[Any]]]  # (eigenvalue, [list of eigenvectors])
    trace: Optional[Any] = None
    determinant: Optional[Any] = None
    stability_summary: str = ""
    regime_insights: List[str] = field(default_factory=list)
    is_linear_constant: bool = True
    notes: List[str] = field(default_factory=list)

"""Systems of ODEs: parse and analyze linear systems (matrix A, eigenvalues, stability)."""

from intuition_engine.systems.schemas import ParsedSystem, SystemInfo
from intuition_engine.systems.parser import parse_system, split_system_equations
from intuition_engine.systems.extract import extract_system_info

__all__ = [
    "ParsedSystem",
    "SystemInfo",
    "parse_system",
    "split_system_equations",
    "extract_system_info",
]

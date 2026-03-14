# helpers/state.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from helpers.core import emit_change


@dataclass
class AppState:
    """
    Central application state (single source of truth).

    Intentionally mutable and shared across UI modules.

    IMPORTANT:
      - No business logic here.
      - Core invariants and key-migration live in helpers.core.
    """

    # --- Core state ---
    entries: List[dict]
    original_data: Dict[str, dict]
    modified_data: Dict[str, Any]
    params: Dict[str, dict]
    counts: Dict[str, int]
    default_params: dict

    # --- Versioning / signaling ---
    version: int = 0
    history: List[str] = field(default_factory=list)

    # --- Reproducibility intent (not RNG object) ---
    noise_seed: int = 0
    lock_noise: bool = False

    def bump(self, note: str = ""):
        """Increment version and optionally log a note."""
        self.version += 1
        if note:
            self.history.append(note)

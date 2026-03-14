# helpers/env.py

from pathlib import Path
import sys

def ensure_project_root_on_path(root=None):
    """
    Make sure the project root (default: current working directory) is on sys.path.
    Safe to rerun.
    """
    root = Path.cwd() if root is None else Path(root)
    root_str = str(root)

    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    return root


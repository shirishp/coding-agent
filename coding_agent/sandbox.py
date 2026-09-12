import os
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", os.getcwd())).resolve()

PROTECTED_FROM_WRITES = {ROOT / ".agent" / "settings.json"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".ruff_cache"}


def resolve(path: str, for_writing: bool = False) -> Path:
    """Resolve a model-supplied path inside ROOT, or refuse."""
    target = (ROOT / path).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise ValueError(f"path escapes the project root: {path}")
    if for_writing and target in PROTECTED_FROM_WRITES:
        raise ValueError(
            f"{path} configures the agent itself and is read-only. "
            f"Ask the user to change it if it needs changing."
        )
    return target

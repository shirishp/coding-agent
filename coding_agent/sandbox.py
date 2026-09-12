from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".ruff_cache"}


def resolve(root: Path, path: str, for_writing: bool = False) -> Path:
    """Resolve a model-supplied path inside root, or refuse."""
    target = (root / path).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"path escapes the project root: {path}")
    if for_writing and target == root / ".agent" / "settings.json":
        raise ValueError(
            f"{path} configures the agent itself and is read-only. "
            f"Ask the user to change it if it needs changing."
        )
    return target

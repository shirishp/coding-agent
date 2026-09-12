from utils.paths import SKIP_DIRS, resolve

LIST_FILES_DEFINITION = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": (
            "List files and directories at a path. "
            "Set recursive true to walk the tree (skips .git, .venv, and similar)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory relative to the project root. Use '.' for the root.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Walk subdirectories. Defaults to false.",
                },
            },
            "required": ["path"],
        },
    },
}

MAX_RECURSIVE_ENTRIES = 200


def list_files(path=".", recursive: bool = False) -> str:
    p = resolve(path)
    if not p.exists():
        return f"ERROR: {path} does not exist."
    if p.is_file():
        return p.name
    if not recursive:
        return "\n".join(
            sorted(f.name + ("/" if f.is_dir() else "") for f in p.iterdir())
        )

    entries = []
    for item in sorted(p.rglob("*")):
        rel = item.relative_to(p)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        entries.append(str(rel) + ("/" if item.is_dir() else ""))
        if len(entries) >= MAX_RECURSIVE_ENTRIES:
            entries.append("[truncated]")
            break
    return "\n".join(entries) if entries else "(empty)"

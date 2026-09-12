import fnmatch
import re

from utils.paths import ROOT, SKIP_DIRS, resolve

GREP_DEFINITION = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": (
            "Search file contents with a regular expression. "
            "Use glob to limit which files are searched (for example '*.py')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regular expression to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "File or directory relative to the project root. Defaults to '.'.",
                },
                "glob": {
                    "type": "string",
                    "description": "Filename glob to include, for example '*.py'. Defaults to '*'.",
                },
            },
            "required": ["pattern"],
        },
    },
}

MAX_MATCHES = 50
MAX_FILE_BYTES = 2_000_000


def _included(path, root, include: str) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/")
    return fnmatch.fnmatch(path.name, include) or fnmatch.fnmatch(rel, include)


def grep(pattern: str, path: str = ".", glob: str = "*") -> str:
    try:
        regex = re.compile(pattern)
    except re.error as error:
        return f"ERROR: invalid regex: {error}"

    target = resolve(path)
    if not target.exists():
        return f"ERROR: {path} does not exist."
    root = target if target.is_dir() else target.parent
    files = (
        [target]
        if target.is_file()
        else sorted(p for p in target.rglob("*") if p.is_file())
    )

    hits = []
    truncated = False
    for file in files:
        if any(part in SKIP_DIRS for part in file.relative_to(ROOT).parts):
            continue
        if not _included(file, root, glob):
            continue
        if file.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            text = file.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        rel = file.relative_to(ROOT)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                hits.append(f"{rel}:{line_no}:{line}")
                if len(hits) >= MAX_MATCHES:
                    truncated = True
                    break
        if truncated:
            break

    if not hits:
        return "No matches."
    result = "\n".join(hits)
    if truncated:
        result += f"\n[truncated after {MAX_MATCHES} matches]"
    return result

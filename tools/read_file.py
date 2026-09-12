from utils.paths import resolve

READ_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a file and return numbered lines. offset is a 1-based line number; "
            "limit caps how many lines to return. Use offset/limit to continue after "
            "a truncated read."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file, relative to the project root.",
                },
                "offset": {
                    "type": "integer",
                    "description": "1-based line number to start from. Defaults to 1.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum lines to return. 0 means the rest of the file.",
                },
            },
            "required": ["path"],
        },
    },
}


def read_file(path: str, offset: int = 1, limit: int = 0) -> str:
    lines = resolve(path).read_text().splitlines()
    if not lines:
        return f"(empty file {path})"

    start = max(int(offset), 1) - 1
    if start >= len(lines):
        return f"ERROR: offset {offset} is past the end of {path} ({len(lines)} lines)."

    end = start + int(limit) if int(limit) > 0 else len(lines)
    chunk = lines[start:end]
    return "\n".join(f"{i:>4}|{line}" for i, line in enumerate(chunk, start=start + 1))

from utils.paths import resolve

LIST_FILES_DEFINITION = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List files and directories at a path. "
        "Use this to explore the project structure.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory relative to the project root. Use '.' for the root.",
                }
            },
            "required": ["path"],
        },
    },
}


def list_files(path="."):
    p = resolve(path)
    return "\n".join(sorted(f.name + ("/" if f.is_dir() else "") for f in p.iterdir()))

EDIT_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": (
            "Replace an exact string in a file. old_str must appear EXACTLY ONCE "
            "in the file — include surrounding lines to make it unique. "
            "To create a new file, pass an empty old_str and the full contents as new_str."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to the project root.",
                },
                "old_str": {
                    "type": "string",
                    "description": "Exact text to replace. Empty string creates a new file.",
                },
                "new_str": {
                    "type": "string",
                    "description": "Text to replace it with.",
                },
            },
            "required": ["path", "old_str", "new_str"],
        },
    },
}


def edit_file(runtime, path: str, old_str: str, new_str: str) -> str:
    target = runtime.resolve(path, for_writing=True)

    if old_str == "":
        already_existed = target.exists()
        if already_existed and target.read_text() != "":
            return (
                f"ERROR: {path} already exists and is not empty. Read it first, "
                f"then pass the text you want to replace as old_str."
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_str)
        action = "Filled empty file" if already_existed else "Created"
        return f"{action} {path} ({len(new_str)} bytes)."

    if not target.exists():
        return f"ERROR: {path} does not exist. To create it, pass an empty old_str."

    contents = target.read_text()
    match_count = contents.count(old_str)
    if match_count == 0:
        return f"ERROR: old_str not found in {path}."
    if match_count > 1:
        return f"ERROR: old_str appears {match_count} times in {path}; make it unique."

    target.write_text(contents.replace(old_str, new_str))
    return f"Edited {path}: 1 replacement."

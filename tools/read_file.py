from utils.paths import resolve

READ_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a file from the local filesystem and return its full contents. "
            "Use this whenever you need to see what is actually in a file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file, relative to the working directory.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Character offset to start reading from. Defaults to 0.",
                },
            },
            "required": ["path"],
        },
    },
}


def read_file(path: str, offset: int = 0) -> str:
    return resolve(path).read_text()[offset:]

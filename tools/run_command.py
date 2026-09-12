import subprocess

from coding_agent.sandbox import ROOT

RUN_COMMAND_DEFINITION = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Run a shell command in the project root and return stdout, stderr, and "
            "the exit code. Needs user permission. Use this to run tests, linters, "
            "git, or other project commands."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to run at the project root.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Seconds before the command is killed. Defaults to 30, max 120.",
                },
            },
            "required": ["command"],
        },
    },
}

DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 120


def run_command(command: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    if not command.strip():
        return "ERROR: command is empty."

    seconds = min(max(int(timeout), 1), MAX_TIMEOUT)
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=seconds,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: command timed out after {seconds}s."

    parts = [f"exit {completed.returncode}"]
    stdout = completed.stdout.rstrip("\n")
    stderr = completed.stderr.rstrip("\n")
    if stdout:
        parts.append(f"stdout:\n{stdout}")
    if stderr:
        parts.append(f"stderr:\n{stderr}")
    if not stdout and not stderr:
        parts.append("(no output)")
    return "\n\n".join(parts)

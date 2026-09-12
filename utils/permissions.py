import json
import os, sys

MUTATING_TOOLS = {"edit_file"}
session_allowed = set()  # tools the user approved for the whole session

DENIAL_MESSAGE = (
    "The user denied this {tool_name} call. Do not retry the same call. "
    "Explain what you were trying to change and ask how they would like to proceed."
)


def assume_yes() -> bool:
    """No human is available, so stop pretending to ask one."""
    return os.environ.get("AGENT_ASSUME_YES") == "1" or not sys.stdin.isatty()


def request_permission(call) -> str | None:
    """Return None to allow the call, or a denial string to send back instead."""
    tool_name = call.function.name
    if tool_name not in MUTATING_TOOLS or tool_name in session_allowed:
        return None

    print(f"\n  {tool_name} wants to run:")
    for field, value in json.loads(call.function.arguments).items():
        preview = value if len(str(value)) < 120 else str(value)[:117] + "..."
        print(f"    {field}: {preview!r}")

    if assume_yes():
        print("  assuming yes (AGENT_ASSUME_YES=1 or no tty)")
        return None

    answer = input("  allow? [y]es / [n]o / [a]lways: ").strip().lower()

    if answer == "a":
        session_allowed.add(tool_name)
        return None
    if answer == "y":
        return None
    return DENIAL_MESSAGE.format(tool_name=tool_name)

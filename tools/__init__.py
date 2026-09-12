import json

from coding_agent.hooks import HOOK_CONFIG, run_hooks
from coding_agent.permissions import request_permission
from coding_agent.sandbox import ROOT
from coding_agent.truncate import truncate_result
from tools.edit_file import EDIT_FILE_DEFINITION, edit_file
from tools.grep import GREP_DEFINITION, grep
from tools.list_files import LIST_FILES_DEFINITION, list_files
from tools.load_skill import LOAD_SKILL_DEFINITION, load_skill
from tools.read_file import READ_FILE_DEFINITION, read_file
from tools.run_command import RUN_COMMAND_DEFINITION, run_command

TOOLS = [
    READ_FILE_DEFINITION,
    LIST_FILES_DEFINITION,
    GREP_DEFINITION,
    EDIT_FILE_DEFINITION,
    RUN_COMMAND_DEFINITION,
    LOAD_SKILL_DEFINITION,
]
DISPATCH = {
    "read_file": read_file,
    "list_files": list_files,
    "grep": grep,
    "edit_file": edit_file,
    "run_command": run_command,
    "load_skill": load_skill,
}


def run_tool(call, extra_dispatch: dict | None = None) -> str:
    tool_name = call.function.name
    try:
        tool_input = json.loads(call.function.arguments)
    except json.JSONDecodeError as error:
        return f"ERROR: arguments were not valid JSON: {error}"

    blocked = run_hooks(HOOK_CONFIG, "PreToolUse", tool_name, tool_input, ROOT)
    if blocked is not None:
        return blocked

    denial = request_permission(call)
    if denial is not None:
        return denial
    result = truncate_result(execute_tool(call, tool_input, extra_dispatch))
    run_hooks(HOOK_CONFIG, "PostToolUse", tool_name, tool_input, ROOT)
    return result


def execute_tool(call, args: dict, extra_dispatch: dict | None = None) -> str:
    dispatch = DISPATCH if extra_dispatch is None else {**DISPATCH, **extra_dispatch}
    tool_fn = dispatch.get(call.function.name)
    if tool_fn is None:
        return f"ERROR: no such tool {call.function.name!r}"
    try:
        return tool_fn(**args)
    except Exception as error:
        return f"ERROR: {type(error).__name__}: {error}"

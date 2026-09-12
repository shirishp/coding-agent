import json

from tools.edit_file import EDIT_FILE_DEFINITION, edit_file
from tools.list_files import LIST_FILES_DEFINITION, list_files
from tools.load_skill import LOAD_SKILL_DEFINITION, load_skill
from tools.read_file import READ_FILE_DEFINITION, read_file
from utils.agents import spawn_agent
from utils.hooks import HOOK_CONFIG, run_hooks
from utils.paths import ROOT
from utils.permissions import request_permission
from utils.truncate import truncate_result

TOOLS = [
    READ_FILE_DEFINITION,
    LIST_FILES_DEFINITION,
    EDIT_FILE_DEFINITION,
    LOAD_SKILL_DEFINITION,
]
DISPATCH = {
    "read_file": read_file,
    "list_files": list_files,
    "edit_file": edit_file,
    "load_skill": load_skill,
    "spawn_agent": spawn_agent,
}


def run_tool(call) -> str:
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
    result = truncate_result(execute_tool(call, tool_input))
    run_hooks(HOOK_CONFIG, "PostToolUse", tool_name, tool_input, ROOT)
    return result


def execute_tool(call, args: dict) -> str:
    tool_fn = DISPATCH.get(call.function.name)
    if tool_fn is None:
        return f"ERROR: no such tool {call.function.name!r}"
    try:
        return tool_fn(**args)
    except Exception as error:
        return f"ERROR: {type(error).__name__}: {error}"

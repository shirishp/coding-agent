import json
import time

from utils.paths import ROOT

SPAWN_AGENT = {
    "type": "function",
    "function": {
        "name": "spawn_agent",
        "description": (
            "Delegate an investigation to a fresh agent with its own context. Use this "
            "when answering something needs reading several files but the answer itself "
            "is short. The agent shares NO history with you, so write the task as if for "
            "a new colleague: name files, paths and goals explicitly. You will receive "
            "only its final report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Self-contained description of the work.",
                },
                "agent_type": {"type": "string", "enum": ["explorer"]},
            },
            "required": ["task"],
        },
    },
}


AGENT_TYPES = {
    "explorer": {
        "tool_names": ("read_file", "list_files"),
        "max_turns": 12,
        "system_prompt": (
            "You are a read-only explorer working inside a codebase.\n"
            "Investigate, then report. Your reply is the ONLY thing the agent that "
            "called you will see — it cannot read your tool results.\n"
            "Report as a list of 'path:line — what is there' entries, then one "
            "sentence of summary. Do not describe your process."
        ),
    },
}

current_depth = 0


def spawn_agent(task: str, agent_type: str = "explorer") -> str:
    # Intentionally deferred imports to avoid circular dependencies.
    from tools import TOOLS
    from utils.loop import run_agent

    global current_depth
    config = AGENT_TYPES.get(agent_type)
    if config is None:  # the enum should prevent this; small models ignore enums
        return (
            f"ERROR: no agent type {agent_type!r}. Available: {', '.join(AGENT_TYPES)}."
        )

    tools = [
        schema for schema in TOOLS if schema["function"]["name"] in config["tool_names"]
    ]

    messages = [
        {"role": "system", "content": config["system_prompt"]},
        {"role": "user", "content": task},
    ]
    current_depth += 1
    try:
        result = run_agent(messages, tools, config["max_turns"], current_depth)
    finally:
        current_depth -= 1

    log_path = ROOT / ".agent" / "subagents" / f"{agent_type}-{int(time.time())}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(messages, indent=2, default=str))
    return result

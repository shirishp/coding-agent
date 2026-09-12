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
        "tool_names": ("read_file", "list_files", "grep"),
        "max_turns": 12,
        "system_prompt": (
            "You are a read-only explorer working inside a codebase.\n"
            "Investigate, then report. Your reply is the ONLY thing the agent that "
            "called you will see — it cannot read your tool results.\n"
            "Report as a list of 'path:line — what is there' entries, then one "
            "sentence of summary."
        ),
    },
}

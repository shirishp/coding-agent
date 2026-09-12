import json
import os
import time
from functools import partial

from dotenv import load_dotenv
from openai import OpenAI

from coding_agent.agents import AGENT_TYPES, SPAWN_AGENT
from coding_agent.compact import COMPACT_ABOVE_TOKENS, compact, estimate_tokens
from coding_agent.prompt import agents_md_section
from coding_agent.sandbox import ROOT
from tools import TOOLS, run_tool

load_dotenv()

# MODEL = "google/gemma-4-e4b"
MODEL = os.environ.get("AGENT_MODEL", "qwen/qwen3.5-9b")
BASE_URL = os.environ.get("AGENT_BASE_URL", "http://localhost:1234/v1")
API_KEY = os.environ.get("AGENT_API_KEY", "lm-studio")
MAX_TURNS = int(os.environ.get("AGENT_MAX_TURNS", "12"))
MAX_AGENT_DEPTH = 1

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)  # one per process


def offered_tools(base: list, depth: int, skill_loaded: bool) -> list:
    offered = [
        schema
        for schema in base
        if not (skill_loaded and schema["function"]["name"] == "load_skill")
    ]
    if depth < MAX_AGENT_DEPTH:
        offered.append(SPAWN_AGENT)
    return offered


def spawn_agent(task: str, agent_type: str = "explorer", depth: int = 0) -> str:
    """Run a nested agent. depth is bound by the loop, not by the model."""
    config = AGENT_TYPES.get(agent_type)
    if config is None:  # the enum should prevent this; small models ignore enums
        return (
            f"ERROR: no agent type {agent_type!r}. Available: {', '.join(AGENT_TYPES)}."
        )

    tools = [
        schema for schema in TOOLS if schema["function"]["name"] in config["tool_names"]
    ]

    system_prompt = config["system_prompt"]
    project_instructions = agents_md_section()
    if project_instructions:
        system_prompt = f"{system_prompt}\n\n{project_instructions}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]
    result = run_agent(messages, tools, config["max_turns"], depth + 1)

    log_path = ROOT / ".agent" / "subagents" / f"{agent_type}-{int(time.time())}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(messages, indent=2, default=str))
    return result


def run_agent(
    messages: list, tools: list = TOOLS, max_turns: int = MAX_TURNS, depth: int = 0
) -> str:
    skill_loaded = False  # per-agent now, not a module global
    turns_used = 0
    extra_dispatch = {"spawn_agent": partial(spawn_agent, depth=depth)}

    while turns_used < max_turns:
        turns_used += 1
        if estimate_tokens(messages) > COMPACT_ABOVE_TOKENS:
            messages[:] = compact(messages, client, MODEL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=offered_tools(tools, depth, skill_loaded),
        )
        reply = response.choices[0].message

        messages.append(
            {
                "role": "assistant",
                "content": reply.content,
                "tool_calls": [tc.model_dump() for tc in (reply.tool_calls or [])],
            }
        )

        if response.choices[0].finish_reason != "tool_calls":
            return reply.content or ""

        for call in reply.tool_calls:
            result = run_tool(call, extra_dispatch)
            print(
                f"  {'  ' * depth}⚒ {call.function.name}"
                f"({call.function.arguments}) → {len(result)} chars"
            )
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
            if call.function.name == "load_skill":
                skill_loaded = True

    return "Agent hit its turn limit without finishing."

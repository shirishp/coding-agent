import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from coding_agent.hooks import load_all_hooks
from coding_agent.sandbox import resolve
from coding_agent.skills import load_all_skills
from tools import build_tool_schemas


@dataclass
class Runtime:
    """Process-wide harness state. Built in main(), passed into the loop and tools."""

    root: Path
    client: OpenAI
    model: str
    max_turns: int
    hooks: dict
    skills: dict
    tools: list
    session_allowed: set = field(default_factory=set)

    def resolve(self, path: str, for_writing: bool = False) -> Path:
        return resolve(self.root, path, for_writing)

    @classmethod
    def from_env(cls) -> "Runtime":
        load_dotenv()
        root = Path(os.environ.get("AGENT_ROOT", os.getcwd())).resolve()
        skills = load_all_skills(root)
        return cls(
            root=root,
            client=OpenAI(
                base_url=os.environ.get("AGENT_BASE_URL", "http://localhost:1234/v1"),
                api_key=os.environ.get("AGENT_API_KEY", "lm-studio"),
            ),
            model=os.environ.get("AGENT_MODEL", "qwen/qwen3.5-9b"),
            max_turns=int(os.environ.get("AGENT_MAX_TURNS", "12")),
            hooks=load_all_hooks(root),
            skills=skills,
            tools=build_tool_schemas(skills),
        )

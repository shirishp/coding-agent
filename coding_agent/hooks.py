import json
import os
import re
import subprocess
from pathlib import Path

from coding_agent.permissions import assume_yes
from coding_agent.sandbox import ROOT

HOOK_TIMEOUT_SECONDS = 5


def load_hook_config(settings_file: Path) -> dict:
    if not settings_file.exists():
        return {}
    try:
        return json.loads(settings_file.read_text()).get("hooks", {})
    except json.JSONDecodeError:
        print(f"  ! ignoring invalid hook config at {settings_file}")
        return {}


def matching_hooks(config: dict, event: str, tool_name: str) -> list[str]:
    """Matchers are regexes tested against the tool name."""
    return [
        entry["command"]
        for entry in config.get(event, [])
        if re.fullmatch(entry.get("matcher", ".*"), tool_name)
    ]


BLOCKING_EVENTS = {"PreToolUse"}

FAILURE_HINTS = {
    126: "found but not executable. Run: chmod +x {command}",
    127: "command not found. Check the path in .agent/settings.json",
}


def report_broken_hook(command: str, problem: str) -> None:
    """Diagnostics for the human. The model cannot chmod anything."""
    print(f"  ! hook {command!r} {problem}")


def run_hooks(config, event, tool_name, tool_input, cwd) -> str | None:
    """Return None to proceed, or a reason to send the model instead of running the tool."""
    can_block = event in BLOCKING_EVENTS
    payload = json.dumps(
        {
            "hook_event_name": event,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "cwd": str(cwd),
        }
    )
    for command in matching_hooks(config, event, tool_name):
        try:
            completed = subprocess.run(
                command,
                shell=True,
                input=payload,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=HOOK_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            report_broken_hook(command, f"timed out after {HOOK_TIMEOUT_SECONDS}s")
            if can_block:
                return (
                    f"A policy check timed out, so {tool_name} was not run. Tell the "
                    f"user their {event} hook is not responding, and do not retry."
                )
            continue

        if completed.returncode == 0:
            continue  # the only outcome that means "proceed"

        if completed.returncode == 2:  # a deliberate refusal
            return completed.stderr.strip() or f"Blocked by hook {command!r}."

        last_line = (
            completed.stderr.strip().splitlines()[-1]
            if completed.stderr.strip()
            else "no stderr output"
        )
        hint = FAILURE_HINTS.get(completed.returncode, last_line)
        report_broken_hook(
            command, f"exited {completed.returncode}: {hint.format(command=command)}"
        )
        if can_block:
            return (
                f"A policy check could not run, so {tool_name} was not attempted. This "
                f"is a configuration problem on the user's machine, not a problem with "
                f"your request. Tell the user their {event} hook is failing, and do "
                f"not retry."
            )
    return None


def hook_search_path() -> list[Path]:
    """User settings, then project settings. Both contribute; neither can remove the other."""
    home = Path(os.environ.get("AGENT_HOME", Path.home()))
    return [home / ".agent" / "settings.json", ROOT / ".agent" / "settings.json"]


def confirm(settings_file: Path, config: dict) -> bool:
    """Project hook config is code from the repository. Show it before running it."""
    print(f"\n  {settings_file} defines hooks that run shell commands:")
    for event, entries in config.items():
        for entry in entries:
            print(f"    {event} [{entry.get('matcher', '.*')}] → {entry['command']}")
    if assume_yes():
        print("  assuming yes (AGENT_ASSUME_YES=1 or no tty)")
        return True
    try:
        return input("  enable them for this session? [y/N]: ").strip().lower() == "y"
    except EOFError:
        return False


def load_all_hooks() -> dict:
    user_settings, project_settings = hook_search_path()
    merged: dict = {}

    for event, entries in load_hook_config(user_settings).items():
        merged.setdefault(event, []).extend(entries)  # your own config, trusted

    project_config = load_hook_config(project_settings)
    if project_config and confirm(project_settings, project_config):
        for event, entries in project_config.items():
            merged.setdefault(event, []).extend(entries)
    return merged


HOOK_CONFIG = load_all_hooks()  # read once, at import

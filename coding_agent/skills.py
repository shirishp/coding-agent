import os
import re
from pathlib import Path

from coding_agent.sandbox import ROOT


def _parse_frontmatter(block: str) -> dict:
    """Parse simple YAML-ish key: value pairs, including indented continuations."""
    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in block.splitlines():
        matched = re.match(r"^(\w+):\s*(.*)$", line)
        if matched:
            current_key, value = matched.group(1), matched.group(2).strip()
            fields[current_key] = value
        elif current_key and (line.startswith(" ") or line.startswith("\t")):
            continuation = line.strip()
            if continuation:
                fields[current_key] = f"{fields[current_key]} {continuation}".strip()
    return fields


def load_catalogue(skills_dir: Path) -> dict:
    """Read every SKILL.md. Keep metadata for the prompt; hold bodies in reserve."""
    catalogue = {}
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        parsed = re.match(r"^---\n(.*?)\n---\n(.*)$", skill_file.read_text(), re.DOTALL)
        if parsed is None:
            continue
        frontmatter = _parse_frontmatter(parsed.group(1))
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not name or not description:
            continue
        catalogue[name] = {
            "description": description,
            "body": parsed.group(2).strip(),
            "dir": skill_dir,
        }
    return catalogue


def catalogue_section() -> str:
    """The only part that reaches the system prompt."""
    if not SKILL_CATALOGUE:
        return ""
    listing = "\n".join(
        f"- {name}: {skill['description']}" for name, skill in SKILL_CATALOGUE.items()
    )
    return (
        f"# Available skills\n{listing}\n\nIf a skill covers the task, load it first."
    )


def skill_search_path() -> list[Path]:
    """User skills first, project skills second, so the project wins a clash."""
    home = Path(os.environ.get("AGENT_HOME", Path.home()))
    return [home / ".agent" / "skills", ROOT / ".agent" / "skills"]


SKILL_CATALOGUE: dict = {}

for directory in skill_search_path():
    if directory.is_dir():
        SKILL_CATALOGUE.update(load_catalogue(directory))

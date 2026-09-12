from utils.paths import ROOT
from utils.skills import catalogue_section

AGENTS_MD_NAMES = ("AGENTS.md", "agents.md")
AGENTS_MD_CHAR_CAP = 8_000

BASE_PROMPT = """\
You are a coding assistant in a local project. Paths are relative to the project root.

Use tools to inspect and change files. Read a file before you edit it. Prefer the smallest change that solves the request.

Keep replies short: lead with the outcome, then only the detail that helps.
"""


def agents_md_section() -> str:
    """Inline AGENTS.md when the project has one. Empty string otherwise."""
    for name in AGENTS_MD_NAMES:
        path = ROOT / name
        if not path.is_file():
            continue
        text = path.read_text().strip()
        if not text:
            return ""
        if len(text) > AGENTS_MD_CHAR_CAP:
            omitted = len(text) - AGENTS_MD_CHAR_CAP
            text = (
                f"{text[:AGENTS_MD_CHAR_CAP]}\n\n"
                f"[AGENTS.md truncated after {AGENTS_MD_CHAR_CAP:,} characters; "
                f"{omitted:,} omitted. Call read_file on {name} for the rest.]"
            )
        return f"# Project instructions ({name})\n{text}"
    return ""


def build_system_prompt() -> str:
    return "\n\n".join(
        part
        for part in (BASE_PROMPT.strip(), agents_md_section(), catalogue_section())
        if part
    )

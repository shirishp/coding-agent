from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

Check = Callable[[Path], tuple[bool, str]]  # (passed, reason)


@dataclass
class Task:
    name: str
    fixture: str  # a directory to copy: the world before
    prompt: str  # what the human would type
    check: Check  # grades the world after


def fixes_typo(root: Path) -> tuple[bool, str]:
    source = root / "src" / "greet.py"
    if not source.exists():
        return False, "deleted the file"
    text = source.read_text()
    if "Helo" in text:
        return False, "typo still present"
    if "Hello" not in text:
        return False, "typo gone but replacement is wrong"
    if "def greet(name):" not in text:
        return False, "collateral damage to the signature"
    return True, "ok"


TASKS = [
    Task(
        name="fixes_typo",
        fixture="typo",
        prompt=(
            "Fix the typo in src/greet.py. The greeting says Helo instead of Hello. "
            "Change only that misspelling."
        ),
        check=fixes_typo,
    ),
]

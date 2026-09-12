import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from evals.tasks import TASKS

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
AGENT_ENTRY = [sys.executable, str(ROOT / "chat.py")]


def run_once(task, timeout: int = 120) -> dict:
    """One attempt, in a throwaway copy of the fixture."""
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / task.fixture
        shutil.copytree(FIXTURES / task.fixture, root)

        env = os.environ.copy()
        env["AGENT_ROOT"] = str(root)
        env["AGENT_ASSUME_YES"] = "1"
        env["AGENT_HOME"] = str(Path(scratch) / "home")

        subprocess.run(
            [*AGENT_ENTRY, task.prompt],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )

        passed, reason = task.check(root)
        return {"passed": passed, "reason": reason}


def main() -> None:
    failed = 0
    for task in TASKS:
        result = run_once(task)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}  {task.name}: {result['reason']}")
        failed += not result["passed"]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

# coding-agent

A minimal local coding harness for testing LLMs. It talks to an OpenAI-compatible
endpoint (LM Studio by default) and can read, list, and edit files inside a
sandboxed project root.

## Features

- **Filesystem tools**: `read_file`, `list_files`, `edit_file`
- **Skills**: load on demand with `load_skill`
- **Subagents**: `spawn_agent` delegates read-only exploration
- **Hooks**: project and user shell hooks around tool use
- **Permissions**: mutating tools need an explicit allow
- **Turn limit and compaction**: loops cannot run forever
- **Path sandbox**: tools cannot escape `AGENT_ROOT`

## Installation

1. Python 3.11+ and [`uv`](https://github.com/astral-sh/uv)
2. `uv sync`
3. Start LM Studio at `http://localhost:1234/v1`

## Running

```
uv run python chat.py
```

Type a request, then press Enter. Ctrl-D exits.

One-shot (used by evals):

```
uv run python chat.py "Fix the typo in src/greet.py"
```

## Configuration

Override defaults with a `.env` file or the environment:

| Variable | Default |
|---|---|
| `AGENT_MODEL` | `qwen/qwen3.5-9b` |
| `AGENT_BASE_URL` | `http://localhost:1234/v1` |
| `AGENT_API_KEY` | `lm-studio` |
| `AGENT_MAX_TURNS` | `12` |
| `AGENT_ROOT` | current working directory |
| `AGENT_ASSUME_YES` | unset (prompt for mutations) |

## Examples

Sample hooks and skills live in `examples/`. The harness only reads live config
from `.agent/` (and `~/.agent/` for user-level overrides). Copy the samples to
try them:

```
mkdir -p .agent
cp examples/settings.json .agent/
cp -R examples/hooks examples/skills .agent/
chmod +x .agent/hooks/*.sh
```

- `examples/hooks/protect-lockfiles.sh` blocks edits to lockfiles
- `examples/hooks/log-edits.sh` appends to `.agent/edits.log` after each edit
- `examples/skills/db-migrations/` is a skill the model can load with `load_skill`

`.agent/` is gitignored. Treat it as local runtime: settings, copied skills, hook
logs, and subagent transcripts.

## Evals

```
uv run python -m evals.run
```

Each task copies a fixture, runs the agent once with `AGENT_ASSUME_YES=1`, and
grades the resulting files. LM Studio must already be running.

## Security

- Tools resolve paths inside `AGENT_ROOT` only.
- `edit_file` requires `y` / `a` unless `AGENT_ASSUME_YES=1` or stdin is not a TTY.
- Project hooks in `.agent/settings.json` run shell commands; the harness asks before enabling them.

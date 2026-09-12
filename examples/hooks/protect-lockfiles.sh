#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
path=$(printf '%s' "$input" | python3 -c \
  'import json,sys; print(json.load(sys.stdin)["tool_input"].get("path",""))')
case "$path" in
  *uv.lock|*package-lock.json|*poetry.lock)
    # stderr is what the model will read. Write it like a denial message.
    echo "Lockfiles are generated, not edited. Change pyproject.toml and re-resolve instead." >&2
    exit 2 ;;
esac
exit 0

#!/usr/bin/env bash
set -euo pipefail
path=$(cat | python3 -c 'import json,sys; print(json.load(sys.stdin)["tool_input"]["path"])')
printf '%s edited %s\n' "$(date -u +%H:%M:%S)" "$path" >> .agent/edits.log

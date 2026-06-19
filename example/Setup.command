#!/bin/bash
# Double-click for one-time setup: create the Python venv and install dependencies.
# Safe to run more than once.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "Setting up the Stock Analyzer environment in:"
echo "  $DIR"
echo

if [ ! -d ".venv" ]; then
  echo "→ Creating Python virtual environment (.venv)…"
  python3 -m venv .venv
else
  echo "→ .venv already exists, reusing it."
fi

REQ=".claude/skills/ensure-deps/requirements.txt"
if [ -f "$REQ" ]; then
  echo "→ Installing dependencies from $REQ …"
  ./.venv/bin/pip install --upgrade pip >/dev/null
  ./.venv/bin/pip install -r "$REQ"
else
  echo "! Could not find $REQ — skipping dependency install."
fi

echo
echo "✓ Setup complete. Double-click 'Open in Claude.command' to start."
echo "  (You can close this window.)"

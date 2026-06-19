#!/bin/bash
# Double-click in Finder to launch Claude in this folder.
#
# Resolution order:
#   1. claude CLI on PATH               -> open Terminal here, run `claude`
#   2. ~/.local/bin/claude              -> same
#   3. /Applications/Claude.app exists  -> launch desktop app, reveal folder in Finder
#                                          (user opens the folder from inside the app)
#   4. Nothing installed                -> open the download page

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"

find_claude_cli() {
  if command -v claude >/dev/null 2>&1; then
    command -v claude
    return 0
  fi
  for candidate in "$HOME/.local/bin/claude" "/opt/homebrew/bin/claude" "/usr/local/bin/claude"; do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

CLAUDE_BIN="$(find_claude_cli || true)"

if [ -n "$CLAUDE_BIN" ]; then
  # Open a new Terminal window cd'd into this folder, running claude.
  # AppleScript handles quoting for paths with spaces.
  osascript <<EOF
tell application "Terminal"
  activate
  do script "cd \"$DIR\" && \"$CLAUDE_BIN\""
end tell
EOF
  exit 0
fi

if [ -d "/Applications/Claude.app" ]; then
  echo "Claude Code CLI not found. Launching Claude desktop app instead."
  echo "Once it opens, point Claude at this folder:"
  echo "  $DIR"
  open -R "$DIR"          # reveal folder in Finder
  open -a "Claude"        # launch desktop app
  exit 0
fi

echo "Neither the claude CLI nor Claude.app is installed."
echo "Opening the download page..."
open "https://claude.com/download"

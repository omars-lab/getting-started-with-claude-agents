#!/bin/bash
# Double-click in Finder to open the start-here.html onboarding guide
# in your default browser. No internet required — the guide is self-contained.

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
GUIDE="$DIR/start-here.html"

if [ -f "$GUIDE" ]; then
  open "$GUIDE"
else
  echo "start-here.html not found next to this launcher."
  echo "Regenerate it by running the onboarding-guide skill inside Claude Code."
fi

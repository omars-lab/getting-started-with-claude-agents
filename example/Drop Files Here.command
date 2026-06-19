#!/bin/bash
# Double-click to open the folder where you drop files for the agent to use.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/agent-inputs"
open "$DIR/agent-inputs"

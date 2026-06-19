#!/bin/bash
# Double-click to open the folder where the agent writes its reports & workbooks.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/agent-outputs"
open "$DIR/agent-outputs"

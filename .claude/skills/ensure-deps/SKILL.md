---
name: ensure-deps
description: Verify the project environment is ready before the agent does real work — Python venv exists, dependencies installed, LibreOffice available for workbook recalculation, ./agent-outputs/ writable, MCP servers reachable. Produces a single readiness report with actionable fixes for anything missing, and offers to run the safe ones (create venv, pip install) after asking. Use as workflow step 0; skip on subsequent runs in the same session. Triggers on "ensure deps", "check setup", "is this ready", "what do I need to install", or automatically before the first invocation of any data-fetching skill.
---

# ensure-deps

The first thing the agent runs. Without it, a missing dependency fails mid-workflow with a stack trace the user can't easily fix. With it, the user sees a single readable checklist before any real work starts.

## Output contract

A markdown block with one row per check, plus a fix command for any failed item:

```
### Environment check

| Status | Item | Detail |
|---|---|---|
| ✓ | Python venv | .venv/bin/python3 (Python 3.12.5) |
| ✓ | openpyxl | 3.1.5 |
| ✓ | yfinance | 0.2.40 |
| ✓ | edgar (edgartools) | 4.2.0 |
| ✓ | jinja2 | 3.1.6 |
| ✓ | LibreOffice | /opt/homebrew/bin/soffice |
| ✓ | ./agent-outputs/ writable | yes |
| - | MCP edgartools | not connected (optional) |
| ✗ | MCP finnhub | configured but unreachable |

**Verdict:** ready (one optional check failed — see below).

**Fix for MCP finnhub:** check `.claude/settings.json` for the server config and that FINNHUB_API_KEY is set in your environment.
```

Verdict line is one of:
- **`ready`** — all required checks pass.
- **`ready (with warnings)`** — required pass; one or more optional checks failed. Agent can proceed.
- **`not ready`** — one or more required checks failed. Agent must not proceed until fixed.

## What gets checked

### Required (block the run if missing)

| Check | How |
|---|---|
| Python venv at `.venv/` | `.venv/bin/python3` exists and runs |
| Required Python packages | `openpyxl`, `formulas`, `yfinance`, `pandas`, `jinja2`, `requests` import |
| `./agent-outputs/` writable | create + delete a sentinel file |
| `.claude/agents/stock-analyzer.md` exists | sanity check |

### Recommended (warn, don't block)

| Check | Why it's optional |
|---|---|
| `edgar` (edgartools) | The agent can also pull filings via WebFetch from sec.gov. |
| `plotly` | Only needed for the optional flow-diagram view in `explain-agent`. |
| MCP servers (per the configured list) | The agent uses Python libraries + WebFetch when MCPs aren't connected. |

The agent runs **pure Python** — no system dependencies (no LibreOffice, no Excel). Workbook formula verification uses the `formulas` package, which evaluates every formula in-process.

## Workflow

### Step 1 — Run the check script

```bash
./.venv/bin/python3 .claude/skills/ensure-deps/scripts/check.py
```

If the venv itself is missing, the script can't run. In that case the skill detects this in its own first three lines (a tiny shim that uses system `python3` to check for `.venv`) and prints the bootstrap fix instead.

The script returns JSON to stdout:

```json
{
  "verdict": "ready",
  "checks": [
    {"name": "Python venv", "status": "ok", "detail": ".venv/bin/python3 (Python 3.12.5)", "required": true},
    ...
  ],
  "fixes": []
}
```

### Step 2 — Render the table

Convert the JSON into the markdown table above. Show the fix block for any failed item.

### Step 3 — Offer to fix what's safely auto-fixable

For these specific failures, ask the user **once** before running:

| Failure | Fix command | Safe to auto-run? |
|---|---|---|
| `.venv/` missing | `python3 -m venv .venv` | Yes, with confirmation |
| Package missing | `./.venv/bin/pip install -r .claude/skills/ensure-deps/requirements.txt` | Yes, with confirmation |
| `./agent-outputs/` not writable | `mkdir -p ./agent-outputs` | Yes, with confirmation |
| MCP server unreachable | varies | **No** — surface the issue, the user fixes credentials/config |

Ask the user once, batched: *"I can run `python3 -m venv .venv && ./.venv/bin/pip install -r .claude/skills/ensure-deps/requirements.txt` for you — proceed?"* Don't ask separately for each step.

The dependency list lives at `.claude/skills/ensure-deps/requirements.txt` — this skill owns it. Adding a new Python dependency to the agent means editing that file *and* the package check list in `scripts/check.py`.

### Step 4 — Block or proceed

- **`not ready`** → the agent must not invoke any other skill. Stop and ask the user to address the failures.
- **`ready (with warnings)`** → the agent proceeds but mentions the warnings in its first message.
- **`ready`** → proceed to `ticker-discovery` (or whatever the user's first ask was) without further announcement.

## Standards

- **Specific fixes, not generic ones.** Print the exact pip install command — don't say "install your dependencies."
- **Don't reinstall what's already there.** The script checks before running anything.
- **Run once per session.** A second invocation in the same conversation should short-circuit unless the user explicitly asks for a recheck (e.g., after they install something).
- **Idempotent.** Running it twice does nothing the second time.
- **No network calls during the basic check.** Importing a package is fine; reaching out to Finnhub is the optional MCP layer.

## Common mistakes to avoid

- ❌ **Treating MCPs as required.** They're optional accelerators. The agent has Python+WebFetch fallbacks for everything.
- ❌ **Auto-installing system packages without asking.** `brew install --cask libreoffice` is a 600MB download and changes /Applications. Always ask.
- ❌ **Running this check inside other skills.** It's the agent's responsibility to call this once at workflow step 0. Other skills assume it's already passed.
- ❌ **Continuing after `not ready`.** Don't try to be helpful by proceeding anyway. The error mid-workflow will be worse.

## What this skill is not

- **Not a package manager.** It checks and prompts; `pip` does the actual work.
- **Not a dependency graph.** It checks the things it knows about — adding a new dependency means updating this skill's check list.
- **Not run on every skill invocation.** Once per session.

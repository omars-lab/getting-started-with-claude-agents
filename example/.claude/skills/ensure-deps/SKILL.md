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

If the venv itself is missing (e.g. a fresh download), run the script with **system Python** — `python3 .claude/skills/ensure-deps/scripts/check.py`. The script checks for `.venv/` first and returns a `not_ready` verdict whose fix is `python3 -m venv .venv`. Don't skip the check just because the venv is absent.

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

Ask the user once, batched: *"I can run `python3 -m venv .venv && ./.venv/bin/python3 -m pip install -r .claude/skills/ensure-deps/requirements.txt` for you — proceed?"* Don't ask separately for each step.

**On a yes, actually run it** — create the venv and install from the requirements file, then re-run the check and proceed. Do not stop and hand the user the commands to paste, and do not present a multi-option menu; that's the failure mode this skill exists to prevent. Only fall back to "you run it yourself" if the user declines or the install errors.

The dependency list lives at `.claude/skills/ensure-deps/requirements.txt` — this skill owns it, **it always exists in this folder**, and it is the only correct install source. Never substitute a hand-typed `pip install <packages>` list, and never report the file as missing. Adding a new Python dependency means editing that file *and* the package check list in `scripts/check.py`.

**Bootstrapping when the venv is absent:** the venv won't exist on a fresh download, so `./.venv/bin/python3` isn't available yet. Run the check with system Python instead — `python3 .claude/skills/ensure-deps/scripts/check.py` — it detects the missing venv and returns `not_ready` with the venv-creation fix. Then follow Step 3.

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
- ❌ **Halting and dumping commands instead of offering to run them.** On `not_ready` with auto-fixable failures, offer the one batched setup command and run it on a yes — don't make the user paste it, and don't present a 3-option menu.
- ❌ **Improvising a `pip install <packages>` list or saying requirements.txt is missing.** It always exists at `.claude/skills/ensure-deps/requirements.txt`. Install from it.
- ❌ **Skipping the check because the venv is gone.** Run it with system `python3`; it's built to report the missing venv.

## What this skill is not

- **Not a package manager.** It checks and prompts; `pip` does the actual work.
- **Not a dependency graph.** It checks the things it knows about — adding a new dependency means updating this skill's check list.
- **Not run on every skill invocation.** Once per session.

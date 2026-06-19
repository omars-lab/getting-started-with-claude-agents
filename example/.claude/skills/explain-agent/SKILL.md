---
name: explain-agent
description: Generate a self-contained interactive HTML diagram that explains how this agent works — what skills exist, when each one fires, what data flows where, and which guardrails apply at each step. Serves it on localhost so the reader can click around. Visual style draws from Anthropic's Claude Code context-window simulation (warm earthy palette, horizontal timeline of color-coded events). Use when someone asks "how does this agent work", "show me what's happening", "explain it visually", or as part of an onboarding walkthrough.
---

# explain-agent

Produce the visual artifact that makes the agent legible to someone who has never built one. The diagram is the thing this teaching example exists to support — without it, the README does most of the explaining; with it, the picture does.

## Output contract

Two files written to `./agent-outputs/`:

1. **`./agent-outputs/agent-diagram.html`** — a single self-contained HTML file. Inline CSS, inline JS, no external assets except optionally one CDN link for Plotly. A reader can email this file to themselves and it still works.
2. **`./agent-outputs/agent-diagram.json`** — the underlying event/skill graph as JSON. Lets the diagram be regenerated and lets future agents read the same source of truth.

Then **serve it on localhost**:

```bash
./.venv/bin/python3 -m http.server 8765 --directory ./agent-outputs &
open http://localhost:8765/agent-diagram.html
```

Tell the user the URL. The server stays running in the background; mention how to stop it (`kill %1` or `lsof -ti :8765 | xargs kill`).

## Visual style (drawing from code.claude.com/context-window)

The page uses the same earthy palette and stacked-timeline aesthetic as Claude Code's context-window simulation page. Tone: technical but warm, monospace headers over a cream background, no gradients, no glassmorphism.

### Palette (use these hex values, not approximations)

| Role | Color | Used for |
|---|---|---|
| Auto / system | `#6B6964` | Built-in events: agent loads, skills indexed, system prompt |
| Memory / persistence | `#E8A45C` | Anything cached or reused across runs |
| MCP / tools | `#9B7BC4` | MCP server calls, tool invocations |
| Skill descriptions | `#D4A843` | Skill discovery and metadata |
| Project context | `#6A9BCC` | Project-level config (CLAUDE.md, settings.json) |
| User input | `#558A42` | User prompts, confirmations |
| Claude / agent action | `#D97757` | Agent reasoning, decisions, writes |
| Tool results | `#A09E96` / `#8A8880` | Read/Bash output, fetched data |
| Hooks | `#B8860B` | Hook execution (pre/post tool) |
| Subagent | inherits | Subagent runs render as an indented stripe with the same kinds inside |
| Rules / guardrails | `#4A9B8E` | Project rules, deny-rules, guardrail invocations |

Background: `#FAF7F2` (cream/off-white). Body text: `#2B2A28`. Monospace: SF Mono / Menlo / Consolas.

### Layout

A horizontal **stacked timeline**. Time runs left to right. Each event is a colored rectangle with:
- Width proportional to either tokens consumed or wall-clock time (pick one and label the axis)
- A short label inside the rectangle if it fits, or above/below as a callout if not
- Hover tooltip showing: event kind, label, source, what the agent did, optional doc link

Above the timeline: a **legend** mapping each color to its role.

Below the timeline: a **skill panel**. Click a skill name in the panel and the timeline highlights every event from that skill. Click an event in the timeline and the skill panel scrolls to that skill's description.

Optional second view (toggle button at top-right): a **flow diagram** showing the same data as nodes + arrows — useful for readers who want the topology rather than the chronology.

### Style references (don't fetch these — just match the vibe)

- The context-window simulation at `https://code.claude.com/docs/en/context-window`
- Edward Tufte sparkline aesthetic — minimal axes, dense data, labels in-place
- The IRS Form 1040 line-item color cues, but with this palette

## What the diagram shows

A canonical run of the stock-analyzer agent, from prompt to delivered HTML report. The events the JSON encodes:

```jsonc
{
  "agent": "stock-analyzer",
  "events": [
    {"kind": "auto",  "label": "Load agent definition",    "tokens": 320,  "source": ".claude/agents/stock-analyzer.md"},
    {"kind": "auto",  "label": "Index project skills",     "tokens": 1100, "source": ".claude/skills/*"},
    {"kind": "user",  "label": "User prompt: 'what's worth looking at today?'"},
    {"kind": "claude","label": "Plan: invoke ticker-discovery"},
    {"kind": "skill", "label": "ticker-discovery — daily sweep", "skill": "ticker-discovery"},
    {"kind": "tools", "label": "WebSearch + WebFetch (Yahoo, SEC)"},
    {"kind": "claude","label": "Shortlist: 5 names"},
    {"kind": "user",  "label": "User confirms shortlist"},
    {"kind": "claude","label": "Fan out: ticker-data per ticker (parallel)"},
    {"kind": "skill", "label": "ticker-data NVDA",       "skill": "ticker-data"},
    {"kind": "skill", "label": "ticker-data AVGO",       "skill": "ticker-data"},
    {"kind": "tools", "label": "edgartools, yfinance, finnhub MCP"},
    {"kind": "claude","label": "Fan out: stock-analysis + growth-study"},
    {"kind": "skill", "label": "stock-analysis NVDA",    "skill": "stock-analysis"},
    {"kind": "skill", "label": "growth-study NVDA",      "skill": "growth-study"},
    {"kind": "skill", "label": "xlsx-author (consumed)", "skill": "xlsx-author", "consumed_by": "growth-study"},
    {"kind": "tools", "label": "recalc.py — verify formulas"},
    {"kind": "skill", "label": "thesis-stress-test NVDA","skill": "thesis-stress-test"},
    {"kind": "claude","label": "Assemble HTML report"},
    {"kind": "user",  "label": "User reviews report"}
  ]
}
```

Events with `consumed_by` render as a bracket beneath the consuming skill's bar — they don't get their own row.

Show roughly **3-5 of the parallel ticker fan-outs**, not all of them. The diagram should fit on one screen at default zoom.

## Workflow

### Step 1 — Read the current agent + skills

Walk `.claude/agents/` and `.claude/skills/*/SKILL.md`. Build the event list dynamically rather than hardcoding it — the diagram should stay correct as skills are added or removed.

For each skill found, extract from frontmatter:
- `name` (becomes the timeline label and the skill panel header)
- `description` (becomes the skill panel body — render the first 2 sentences)

### Step 2 — Build the JSON

Write `./agent-outputs/agent-diagram.json` with:
- `agent` — name from `.claude/agents/<name>.md` frontmatter
- `agent_description` — first paragraph of the agent file body
- `events` — chronological list as above
- `skills` — full list with name + description for the side panel
- `palette` — the hex values above (so the renderer doesn't have to know them)
- `generated_at` — ISO timestamp

### Step 3 — Render the HTML

Use the Jinja template at `./.claude/skills/explain-agent/templates/diagram.html.j2`. Populate from the JSON. Inline everything — readers should be able to open the file from anywhere.

The template is small enough (~400 lines including CSS + JS) to live alongside this skill and be edited when the visual needs to change.

### Step 4 — Serve it

```bash
./.venv/bin/python3 .claude/skills/explain-agent/scripts/serve.py
```

The script:
1. Generates the HTML if missing or stale (older than the source agent/skill files).
2. Starts `http.server` on port 8765 (or the next available port if taken).
3. Opens `http://localhost:<port>/agent-diagram.html` in the default browser via `open` (macOS) or `xdg-open` (Linux).
4. Prints the URL and the kill command, then backgrounds.

## Standards

- **Self-contained HTML** — single file, opens offline. CDN links only for Plotly if the toggle-to-flow-diagram view needs it.
- **Accessibility** — color is not the only signal. Each event also has an icon and a text label. Tooltips work without hover (focus-visible). Min 4.5:1 contrast everywhere.
- **No external trackers** — no Google Analytics, no fonts loaded from a CDN. This is a teaching artifact; it should not phone home.
- **Readable source** — the HTML can be read top to bottom by someone learning. Comments label sections. CSS at the top, data inline as a `<script type="application/json">` block, JS that consumes it at the bottom.

## Common mistakes to avoid

- **Hardcoded event list.** The whole point is that the diagram updates as skills change. Walk the filesystem.
- **Cute but unreadable.** Curved sankeys, animated transitions, particle effects — none of these help understanding. The reference (Claude Code context-window page) is restrained for a reason.
- **Color-only encoding.** Always pair color with a text label or icon.
- **Plotly when SVG would do.** A simple stacked bar is faster, lighter, and editable. Reserve Plotly for the optional flow-diagram view.
- **Skipping the localhost step.** Writing the HTML and stopping is half the deliverable. Serve and open.

## What this skill is not

- **Not documentation.** That's the README. This is the visualization.
- **Not a runtime trace.** It shows the *canonical* shape of a run, not a live trace of one specific session. (A trace tool would be a separate skill.)
- **Not a dashboard.** Static (regenerated on demand), not live-updating.

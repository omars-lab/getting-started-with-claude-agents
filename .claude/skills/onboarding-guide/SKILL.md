---
name: onboarding-guide
description: Regenerate the self-contained start-here.html onboarding guide — the double-clickable walkthrough that introduces a newcomer to this agent (what an agent vs a skill is, how to open it, how to reveal the hidden .claude folder, what each folder inside does), with embedded Finder mockups and a terminal GIF. Use when someone asks to "rebuild the guide", "refresh start-here", "update the onboarding page", or after the agent's skills/folders change and the guide is stale.
---

# onboarding-guide

Builds `start-here.html` at the repo root: a single self-contained file a non-technical friend can double-click to learn what this agent is and how to use it. It is the companion to `explain-agent` — that one diagrams *how a run flows*; this one is the *first-contact walkthrough* (open it, reveal `.claude`, read the four things inside, watch one run).

## Output contract

After running, these exist:

- **`./start-here.html`** — the guide, fully self-contained. Every image is inlined as a base64 data URI; it opens offline from anywhere with no external assets, no trackers, no CDN.
- **`.claude/skills/onboarding-guide/assets/`** — the regenerated source assets:
  - `terminal.gif` — a *faithful* Claude Code session (cream UI, grey prompt bar, the `● I'll … launch the stock-analyzer agent` turn, the `stock-analyzer(…)` subagent block with indented `└` tool calls, the orange `✻ Stewing…` spinner, the `Opus 4.8 | 📁 market-researcher | …` status line). Claude never says "agent is ready."
  - `finder-hidden.svg` — the folder as first seen, `.claude` hidden
  - `finder-shown.svg` — after `⌘⇧.` reveals the dotfiles
  - `finder-claude.svg` — the contents of `.claude` (agents, skills, plans, settings.json)
  - `finder-launch.svg` — the folder with `Open in Claude.command` highlighted (Getting Started step 1)
  - `finder-agents.svg` — inside `.claude/agents/`, the single `stock-analyzer.md` (Make it yours)
  - `finder-skills.svg` — inside `.claude/skills/`, the skill folders with `xlsx-author` highlighted (Make it yours)
  - `claude-agents.svg` — the `/agents` Library panel proving `stock-analyzer` is a configured Project agent
  - `claude-splash.svg` — the Claude Code startup splash (mascot + version + empty input box, "waiting for input")
- **`./View Guide.command`** — double-click launcher that opens `start-here.html` in the browser (create if missing).

## Workflow

Run all three steps from the repo root, using the project venv:

```bash
./.venv/bin/python3 .claude/skills/onboarding-guide/scripts/make_terminal_gif.py   # → assets/terminal.gif
./.venv/bin/python3 .claude/skills/onboarding-guide/scripts/make_finder_svgs.py     # → assets/finder-*.svg
./.venv/bin/python3 .claude/skills/onboarding-guide/scripts/make_agents_svg.py      # → assets/claude-agents.svg
./.venv/bin/python3 .claude/skills/onboarding-guide/scripts/make_claude_splash.py   # → assets/claude-splash.svg
./.venv/bin/python3 .claude/skills/onboarding-guide/scripts/build_html.py           # → ./start-here.html
```

1. **Render the terminal GIF** (`make_terminal_gif.py`). Uses Pillow to type out a real Claude Code session frame by frame, then `gifsicle -O3` to shrink it (~100 KB). Edit the `TRANSCRIPT` list to change what the session shows — keep it faithful to how Claude Code actually renders (see the asset note above).
2. **Render the Finder mockups** (`make_finder_svgs.py`). Pure-Python SVG — no dependencies. Edit the `visible` / `shown` / `inside` lists to match the current folder contents.
3. **Render the `/agents` panel** (`make_agents_svg.py`). Pure-Python SVG of the `/agents` Library view. Update the path/agent name if the agent is renamed or moved.
4. **Assemble the HTML** (`build_html.py`). Reads `templates/start-here.html.tmpl`, inlines each asset as a data URI, writes `./start-here.html`. Fails loudly if any `__TOKEN__` is left unreplaced.

Then tell the user the file is ready and they can double-click `View Guide.command` (or `start-here.html` itself).

### Editing the guide's content

The prose, layout, and styling live in `templates/start-here.html.tmpl`. Edit it directly, then re-run step 3 only. Keep the visual language consistent with `explain-agent`: cream `#FAF7F2` ground, ink `#2B2A28`, terracotta `#D97757` accent, teal `#4A9B8E`, monospace headers. No gradients, no glassmorphism — technical but warm.

## Dependencies

- **Pillow** in the venv (`./.venv/bin/pip install Pillow`) — for the GIF.
- **gifsicle** on PATH (`brew install gifsicle`) — optional; the GIF still builds without it, just larger.
- Everything else is standard library. The SVG and HTML steps need nothing extra.

## Keep it in sync

When skills are added or removed, the guide can drift:

- The skill chips in the `skills/` anatomy panel are listed in the template — update them there.
- The Finder mockup file lists (`make_finder_svgs.py`) should match what's actually in the folder.
- The input/output convention (`agent-inputs/` → `agent-outputs/`) is described in the template's "Inputs & outputs" section; keep it aligned with the agent definition.

This skill does **not** walk the filesystem dynamically (unlike `explain-agent`) — the guide is curated prose, so updates are intentional edits, not auto-generated.

## Standards

- **Self-contained.** One file, opens offline. If you add an image, inline it as a data URI via `build_html.py` — never link an external asset.
- **Reproducible.** Every visual is generated by a script in `scripts/`, never hand-pasted binary. Anyone can rebuild the exact guide.
- **Accessible.** Real `alt` text on every figure, visible focus, `prefers-reduced-motion` respected, ≥4.5:1 contrast.
- **No phoning home.** No analytics, no web fonts, no CDN. It's a teaching artifact for a friend.

## Common mistakes to avoid

- **Editing `start-here.html` directly.** It's generated — your edits vanish on the next build. Edit the template or the scripts.
- **Forgetting to re-run `build_html.py`** after changing an asset script. The HTML embeds a *copy* of the asset, not a link.
- **Leaving `gifsicle` out and shipping a 400 KB GIF.** Install it, or accept the larger file knowingly.
- **Letting the skill chips / Finder mockups drift** from the real folder contents after you add a skill.

## What this skill is not

- **Not `explain-agent`.** That renders the run-flow diagram from the live filesystem. This is the curated first-contact walkthrough.
- **Not the README.** The README is the thorough reference; this guide is the ten-minute visual on-ramp.
- **Not auto-syncing.** Regenerate it on demand after meaningful changes.

# Working in this repo

This is **getting-started-with-claude-agents** — a teaching example for Claude Code
agent development. It contains one working agent (`stock-analyzer`) and a
self-contained HTML onboarding guide that explains it.

## Layout

- `.claude/agents/stock-analyzer.md` — the agent (the *who*: a role + workflow).
- `.claude/skills/*/SKILL.md` — the skills (the *how*: one recipe each).
- `.claude/skills/onboarding-guide/` — generates `start-here.html`, the guide.
- `agent-inputs/` — drop files here for the agent to use (e.g. `watchlist.md`).
- `agent-outputs/` — everything the agent produces (gitignored).
- `start-here.html` / `index.html` — the built guide (`index.html` is the GitHub Pages entry point).

## Common tasks (use the Makefile)

- **Rebuild the guide** after editing the agent, a skill, or the guide template:
  `make build` — regenerates all assets (terminal GIF, Finder SVGs, splash, `/agents` panel)
  and assembles `start-here.html` + `index.html`.
- **Publish** (update the live GitHub Pages site): `make publish` — builds, commits, and
  pushes to `main`. Pushing triggers the Pages rebuild automatically.
- **Share a copy**: `make zip` — writes a timestamped zip to `~/Desktop`, omitting repo
  tooling (`.venv`, `.git`, `Makefile`, `CLAUDE.md`, `.gitignore`, `index.html`, etc.).

## Editing the guide

Never edit `start-here.html` or `index.html` directly — they're generated. Edit the
template at `.claude/skills/onboarding-guide/templates/start-here.html.tmpl` (prose,
layout, CSS) or the asset scripts under `.../scripts/`, then run `make build`. The full
recipe and conventions live in `.claude/skills/onboarding-guide/SKILL.md`.

## Conventions

- **Python**: always use the project venv — `./.venv/bin/python3`, never bare `python3`.
  If `.venv/` is missing, run `Setup.command` (or `make build` will fail).
- **Input/output**: the agent reads from `agent-inputs/` (it checks there at the start of
  every run) and writes only to `agent-outputs/`.
- **Secrets**: a gitleaks pre-commit hook scans staged changes. Don't commit credentials;
  `.env*` reads are denied in `.claude/settings.json`.
- **Self-contained guide**: `start-here.html` inlines every image as a data URI — no
  external assets, no trackers. Keep it that way (add new images via `build_html.py`).

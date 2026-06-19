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

- **Deploy everything** (the default after any change): `make ship` — builds once, uploads
  the downloadable release zip, then commits and pushes (which rebuilds GitHub Pages). Use
  this unless you specifically want just one of the steps below.
- **Rebuild the guide** locally only: `make build` — regenerates all assets (terminal GIF,
  Finder SVGs, splash, `/agents` panel) and assembles `start-here.html` + `index.html`.
- **Publish the site only**: `make publish` — build, commit, push (no release upload).
- **Refresh the download only**: `make release` — build, upload the fixed-name zip to the
  GitHub `latest` release.
- **Check responsive layout**: `make shots` — full-page screenshots of the guide at desktop
  (1280) and mobile (390) widths into `tests/screenshots/`. Needs Playwright in the venv:
  `./.venv/bin/python3 -m pip install playwright && ./.venv/bin/python3 -m playwright install chromium`.
- **Share a local copy**: `make zip` — writes a timestamped zip to `~/Desktop`, omitting repo
  tooling (`.venv`, `.git`, `Makefile`, `CLAUDE.md`, `.gitignore`, `index.html`, `tests/`, etc.).

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

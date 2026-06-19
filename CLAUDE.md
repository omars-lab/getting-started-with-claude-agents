# Working in this repo (for developers)

This is **getting-started-with-claude-agents** — a teaching example for Claude Code
agent development. End users download a folder containing one working agent
(`stock-analyzer`) and a self-contained HTML onboarding guide that explains it.
This file is for people *maintaining* the repo, not for those learning from it.

## Repo structure — important

The repo separates the **shippable example** from the **build tooling**:

| Path | What it is | Who uses it |
|---|---|---|
| `example/` | **The downloadable folder**, a real runnable Claude project. Holds `example/.claude/` (the `stock-analyzer` agent + its 10 skills), the launchers, README, and `agent-inputs/` / `agent-outputs/`. | Shipped to end users. |
| `.claude/` (repo root) | **Dev config**, active when you open the repo in Claude Code. Holds ONLY the `onboarding-guide` skill — the tooling that builds the web guide. | You, the maintainer. |
| `index.html` (repo root) | The **web-only guide**, generated for GitHub Pages. NOT shipped in the zip. | Web readers. |

`example/.claude/` is a real dotted config, so you can **`cd example && claude`** to
run the agent live while developing. `make dist`/`zip`/`release` package `example/`
(stripping generated `agent-outputs/` data); the guide and all repo tooling stay out.

## Maintaining the example (the agent + its skills)

Edit the teaching agent and skills under **`example/.claude/`**:

- `example/.claude/agents/stock-analyzer.md` — the agent (the *who*: role + workflow).
- `example/.claude/skills/*/SKILL.md` — the 10 skills (the *how*: one recipe each).
- `example/.claude/settings.json` — permissions shipped with the example.

If you **add or remove a teaching skill**, also update the guide so it stays accurate:
- the skill count ("10 different skills" / "ten abilities") in the template,
- the chip list and the `SKILLS` object in `start-here.html.tmpl`,
- the skill folders shown in `make_finder_svgs.py`.

The agent's runtime deps live in `example/.claude/skills/ensure-deps/requirements.txt`
(the README's Setup steps install them; the `ensure-deps` skill verifies them on first run).

## Editing the guide

The guide is generated — **never edit `index.html` directly**. Edit the template at
`.claude/skills/onboarding-guide/templates/start-here.html.tmpl` (prose, layout, CSS)
or the asset scripts under `.claude/skills/onboarding-guide/scripts/`, then `make build`.
Full conventions: `.claude/skills/onboarding-guide/SKILL.md`.

## Common tasks (use the Makefile — `make help` lists all)

- **Deploy everything** (default after any change): `make ship` — build once, upload the
  release zip, commit + push (rebuilds GitHub Pages).
- `make build` — regenerate assets + the web guide `index.html` (local only).
- `make dist` — stage the exact downloadable folder in `dist/` (a clean copy of `example/`).
  Inspect it to see precisely what a user gets.
- `make zip` — timestamped share zip to `~/Desktop`, built from `dist/`.
- `make release` — upload the fixed-name zip to the GitHub `latest` release (stable URL).
- `make publish` — build, commit, push (site only).
- `make setup` — install build/test tooling (Pillow, Playwright + Chromium) from
  `requirements-dev.txt`. The agent's *runtime* deps are separate
  (`example/.claude/skills/ensure-deps/requirements.txt`, installed per the example README's Setup steps).
- `make shots` — screenshot the guide at desktop (1280) + mobile (390) into
  `tests/screenshots/`. Run `make setup` first.
- `make clean` — remove `dist/`.

## What ships vs what doesn't

`make dist`/`zip`/`release` ship a clean copy of **`example/`**: its `.claude/`,
`README.md`, the `.command` launchers, `agent-inputs/` (with `watchlist.md`), and an
empty `agent-outputs/` (placeholders only). The web-only guide (`index.html`) and all
repo tooling (dev `.claude/`, `Makefile`, `CLAUDE.md`, `.gitignore`,
`.pre-commit-config.yaml`, `requirements-dev.txt`, `tests/`, `dist/`, `.venv/`, `.git/`)
stay out — they're not inside `example/` to begin with.

## Conventions

- **Python**: always use the project venv — `./.venv/bin/python3`, never bare `python3`.
- **Input/output**: the agent reads from `agent-inputs/` (checked at the start of every
  run) and writes only to `agent-outputs/`.
- **Secrets**: a gitleaks pre-commit hook scans staged changes. Don't commit credentials.
- **Self-contained guide**: the web guide (`index.html`) inlines every image as a data
  URI — no external assets, no trackers. Add new images via `build_html.py`.

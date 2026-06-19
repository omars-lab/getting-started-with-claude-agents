# Working in this repo (for developers)

This is **getting-started-with-claude-agents** — a teaching example for Claude Code
agent development. End users download a folder containing one working agent
(`stock-analyzer`) and a self-contained HTML onboarding guide that explains it.
This file is for people *maintaining* the repo, not for those learning from it.

## Two Claude configs — important

There are **two** agent configs, and they serve different audiences:

| Path | What it is | Who uses it |
|---|---|---|
| `.claude/` (dotted) | **Dev config**, active when you open this repo in Claude Code. Contains ONLY the `onboarding-guide` skill — the tooling that builds the guide. | You, the maintainer. |
| `claude/` (no dot) | **The maintained example** ("dist source"). Contains the `stock-analyzer` agent + its 10 teaching skills. Inactive in the repo (Claude Code only reads dotted `.claude`). | Shipped to end users. |

At package time, `make dist` copies `claude/` into the downloadable folder **as
`.claude/`**, so what the user downloads is a normal, working Claude project. The
dev `onboarding-guide` skill is never shipped — it's repo plumbing.

**Consequence:** while developing here, `stock-analyzer` is NOT a live agent (it
lives in `claude/`, which Claude Code ignores). That's intentional. To test it as a
live agent, work inside a `make dist` copy, or temporarily symlink/rename.

## Maintaining the example (the agent + its skills)

Edit the teaching agent and skills under **`claude/`**:

- `claude/agents/stock-analyzer.md` — the agent (the *who*: role + workflow).
- `claude/skills/*/SKILL.md` — the 10 skills (the *how*: one recipe each).
- `claude/settings.json` — permissions shipped with the example.

If you **add or remove a teaching skill**, also update the guide so it stays accurate:
- the skill count ("10 different skills" / "ten abilities") in the template,
- the chip list and the `SKILLS` object in `start-here.html.tmpl`,
- the skill folders shown in `make_finder_svgs.py`.

## Editing the guide

The guide is generated — **never edit `start-here.html` or `index.html` directly**.
Edit the template at `.claude/skills/onboarding-guide/templates/start-here.html.tmpl`
(prose, layout, CSS) or the asset scripts under `.claude/skills/onboarding-guide/scripts/`,
then `make build`. Full conventions: `.claude/skills/onboarding-guide/SKILL.md`.

## Common tasks (use the Makefile — `make help` lists all)

- **Deploy everything** (default after any change): `make ship` — build once, upload the
  release zip, commit + push (rebuilds GitHub Pages).
- `make build` — regenerate assets + `start-here.html`/`index.html` (local only).
- `make dist` — stage the exact downloadable folder in `dist/` (`claude/` → `.claude/`).
  Inspect it to see precisely what a user gets.
- `make zip` — timestamped share zip to `~/Desktop`, built from `dist/`.
- `make release` — upload the fixed-name zip to the GitHub `latest` release (stable URL).
- `make publish` — build, commit, push (site only).
- `make setup` — install build/test tooling (Pillow, Playwright + Chromium) from
  `requirements-dev.txt`. The agent's *runtime* deps are separate
  (`claude/skills/ensure-deps/requirements.txt`, installed by the shipped `Setup.command`).
- `make shots` — screenshot the guide at desktop (1280) + mobile (390) into
  `tests/screenshots/`. Run `make setup` first.
- `make clean` — remove `dist/`.

## What ships vs what doesn't

`make dist`/`zip`/`release` include: `claude/` (as `.claude/`), `start-here.html`,
`README.md`, the `.command` launchers, `agent-inputs/` (with `watchlist.md`), and an
empty `agent-outputs/` (placeholders only). They **omit** all repo tooling: the dev
`.claude/`, `Makefile`, `CLAUDE.md`, `.gitignore`, `.pre-commit-config.yaml`,
`requirements-dev.txt`, `index.html`, `tests/`, `dist/`, `.venv/`, `.git/`.

## Conventions

- **Python**: always use the project venv — `./.venv/bin/python3`, never bare `python3`.
- **Input/output**: the agent reads from `agent-inputs/` (checked at the start of every
  run) and writes only to `agent-outputs/`.
- **Secrets**: a gitleaks pre-commit hook scans staged changes. Don't commit credentials.
- **Self-contained guide**: `start-here.html` inlines every image as a data URI — no
  external assets, no trackers. Add new images via `build_html.py`.

# Stock Analyzer — a teaching example for Claude Code agents

This repo is two things at once:

1. A **working agent** that surveys the market each morning and produces a research report on a handful of names worth a closer look — with sourced math, recent news, and a stress test of the resulting thesis.
2. A **teaching example** for finance and research professionals who haven't built a Claude agent before. Open the folders, read the files, and the question *"what is an agent? what is a skill?"* should answer itself.

You don't need to know Python, JSON, or the Claude SDK to read this repo. You should be able to read it the way you'd read a research analyst's playbook.

---

## The two-line version

> **An agent is a *who*** — a role, like "senior research associate," that decides what to do next.
> **A skill is a *how*** — a specific recipe, like "spread the financials," that the agent follows.

The agent file (`.claude/agents/stock-analyzer.md`) describes the role and the workflow. The skill files (`.claude/skills/*/SKILL.md`) describe the recipes. The agent reads its own definition and decides which skill to invoke. The skills don't know about each other; they only know how to do their one job well.

This separation is the whole reason the example is interesting. Each skill can be read on its own, copied into another project, or rewritten — the agent picks them up automatically.

---

## What the agent does

Run it by typing `claude` in this folder, then asking:

> *"what's worth looking at today?"*

Here is what happens, step by step:

0. **`ensure-deps`** — the agent runs this first. It checks that the Python venv exists, dependencies are installed, LibreOffice is available for spreadsheet recalculation, and `./agent-outputs/` is writable. If anything is missing, you get a single readable checklist with the fix commands — the agent does not try to proceed past missing dependencies.
1. **`ticker-discovery`** — sweeps the news for earnings movers, 8-K filings, analyst actions, unusual volume. Returns 3–7 candidate tickers with a one-line reason each. (For under-the-radar names that aren't in the morning conversation, the pipeline is two skills: `stock-discovery` runs the raw setup sweep — insider buying clusters, 13F accumulation by trusted holders, post-spin orphans, coverage gaps, politician-trade clusters — then `hidden-opportunities` applies the asymmetry filter and surfaces 3-5 candidates worth deeper work.) The agent **stops here and asks you to approve the shortlist** before doing the expensive work.
2. **`ticker-data`** (parallel per ticker) — pulls the latest filings, quote, 2-year price history, news, and peer set into `./agent-outputs/<TICKER>/raw/`. Idempotent: if it ran an hour ago, it doesn't re-fetch.
3. **`stock-analysis`** (parallel per ticker) — produces a markdown read: business in 2-3 sentences, recent results table, 3-5 dated news bullets, peer context, 2-3 key debates with bull/bear, calendar of catalysts.
4. **`growth-study`** (parallel per ticker) — builds `./agent-outputs/<TICKER>.xlsx`, a 3-tab workbook (Fundamentals, News, Historical) with formulas referencing input cells, every input commented with its source. Runs LibreOffice headless recalc to catch `#DIV/0!`/`#REF!` errors before declaring done.
5. **`thesis-stress-test`** (per ticker) — pressure-tests the read: 3-5 what-if scenarios with shown math, falsifiable claims, the strongest contrarian argument, and a verdict (*Holds / Cracks under [X] / Already broken*).
6. **HTML report** — assembled at `./agent-outputs/report-YYYY-MM-DD.html`, linking everything together.

You can also run **`explain-agent`** at any time, which generates an interactive HTML diagram of how the agent works and serves it on localhost. Useful for onboarding people to this repo.

---

## Why split it into so many skills?

Because each skill is a discipline you'd recognize from a real research desk:

| Skill | What it owns |
|---|---|
| `ensure-deps` | The pre-flight check. Runs first; blocks if the environment isn't ready. |
| `ticker-discovery` | The morning idea-generation routine — catalyst-driven. |
| `stock-discovery` | The raw setup sweep — Form 4, 13F, buybacks, post-spins, coverage gaps, politician trades. No judgment, just data. |
| `hidden-opportunities` | The judgment layer on top of `stock-discovery` — applies the "is the consensus actually missing this?" filter. |
| `ticker-data` | The source-of-truth fetch. Whoever needs filings reads them from here. |
| `stock-analysis` | The qualitative read. The judgment. |
| `growth-study` | The model. The numbers. |
| `xlsx-author` | The shared spreadsheet conventions everyone follows. |
| `thesis-stress-test` | The validation step a thoughtful PM does before signing off. |
| `explain-agent` | Self-explanation, so the agent stays legible to outsiders. |

If you've worked with a junior analyst, you've effectively trained them on each of these as separate skills. The structure here mirrors that.

The `xlsx-author` skill is the cleanest example of why splitting matters: it defines the conventions (formulas-not-hardcodes, blue text for inputs, comments citing sources) once. `growth-study` *uses* those conventions instead of restating them. Tomorrow you might add a `peer-comps-workbook` skill that uses the same conventions — no duplication, no drift.

---

## Setup

You need Claude Code installed. If you don't have it: <https://claude.com/download>.

The easy path: **double-click `Setup.command`** in Finder. It creates the Python venv and installs dependencies for you (safe to run more than once). Then double-click **`Open in Claude.command`** to start.

Or do it by hand in this folder:

```bash
# 1. Create a project-local Python venv (one-time setup)
python3 -m venv .venv

# 2. Install dependencies (the list lives in the ensure-deps skill)
./.venv/bin/pip install -r .claude/skills/ensure-deps/requirements.txt

# 3. Run Claude
claude
```

Double-clickable launchers, for the non-terminal path:

- **`Setup.command`** — one-time venv + dependency install.
- **`Open in Claude.command`** — launch Claude Code in this folder.
- **`View Guide.command`** — open the visual walkthrough (`start-here.html`).
- **`Open Outputs.command`** / **`Drop Files Here.command`** — jump to `agent-outputs/` and `agent-inputs/`.

### Giving the agent files, getting files back

Two plainly-named folders keep this simple:

- **`agent-inputs/`** — drop anything you want the agent to work from here (a ticker list, a CSV, a thesis memo).
- **`agent-outputs/`** — everything the agent produces lands here (reports, workbooks, the per-ticker data cache).

You don't need to remember internal paths — just drop and collect.

The skills always invoke Python via `./.venv/bin/python3`, never bare `python3`. Bare `python3` would use the system interpreter and miss `openpyxl`, `yfinance`, etc.

---

## File map

```
.claude/
  agents/
    stock-analyzer.md            ← the role definition
  skills/
    ensure-deps/SKILL.md         ← pre-flight environment check
      scripts/check.py           ← runs the readiness checklist
      requirements.txt           ← canonical Python dependency list
    ticker-discovery/SKILL.md    ← daily catalyst sweep
    stock-discovery/SKILL.md     ← raw setup sweep (no judgment)
    hidden-opportunities/SKILL.md ← asymmetry filter on top of stock-discovery
    ticker-data/SKILL.md         ← cached data fetcher
    stock-analysis/SKILL.md      ← qualitative read
    growth-study/SKILL.md        ← workbook content
    xlsx-author/SKILL.md         ← shared workbook discipline
      scripts/recalc.py          ← LibreOffice recalc + error scan
    thesis-stress-test/SKILL.md  ← validation layer
    explain-agent/SKILL.md       ← visualization
      scripts/serve.py
      templates/diagram.html.j2
    _archive/                    ← superseded skills, kept for reference
    onboarding-guide/SKILL.md    ← regenerates start-here.html + its assets
      scripts/                       ← GIF, Finder mockups, HTML builder
      templates/start-here.html.tmpl
      assets/                        ← generated GIF + SVG mockups
  plans/
    refactor-to-stock-analyzer.md  ← how this repo got here
  settings.json                    ← project permissions
.venv/                             ← Python venv (you create this)
Setup.command                      ← double-click for one-time venv + deps install
Open in Claude.command             ← double-click to launch Claude here
View Guide.command                 ← double-click to open start-here.html
Open Outputs.command               ← double-click to open agent-outputs/
Drop Files Here.command            ← double-click to open agent-inputs/
start-here.html                    ← visual onboarding guide (open offline)
agent-inputs/                      ← drop files for the agent here
agent-outputs/                     ← the agent writes results here
README.md                          ← this file
```

---

## Things to read first

If you only have ten minutes:

1. **`.claude/agents/stock-analyzer.md`** — the role definition. Notice it's mostly prose, not code.
2. **`.claude/skills/xlsx-author/SKILL.md`** — the cleanest example of a skill: it defines a discipline, gives examples, lists common mistakes, and stops.
3. **`.claude/skills/thesis-stress-test/SKILL.md`** — the most opinionated skill, with a strong point of view about what good analysis looks like.

Each `SKILL.md` is structured the same way:

- A **frontmatter description** that tells the agent when this skill is relevant.
- The **output contract** — what file or markdown block this skill is responsible for producing.
- The **workflow** — numbered steps the agent follows.
- **Standards** — the rules that make the output trustworthy.
- **Common mistakes to avoid** — the trapdoors you've seen junior people fall into.
- **What this skill is not** — explicit non-goals, so it doesn't sprawl.

That's it. No special framework, no DSL. Just markdown a domain expert can read and edit.

---

## When to use this agent (and when not to)

**Use it when:**
- You want a triage on the day's market — what moved, what filed, what's worth a second look.
- You're stress-testing an existing thesis and want a steelman of the bear case.
- You're onboarding someone to "what does our research process look like?"

**Don't use it for:**
- Full-coverage initiation reports — this is a triage tool, not a 30-page primer.
- Trade execution, position sizing, or any action recommendation. The skills explicitly refuse to give advice.
- Anything time-critical. The agent stops to confirm at two checkpoints.

---

## Modifying the agent

The whole point of the example is that you can change it.

- **Add a skill:** create `.claude/skills/<your-skill>/SKILL.md` with the same structure. Reference it from `stock-analyzer.md`.
- **Change a workflow step:** edit `stock-analyzer.md`. The skills don't change.
- **Tighten a discipline:** edit the `Standards` section of the relevant `SKILL.md`. The agent will pick up the new rules on the next run.
- **Add a new MCP server:** add it to `.claude/settings.json` under `permissions.allow`.

The `explain-agent` skill walks `.claude/` dynamically, so the diagram updates automatically as you add or remove skills. There's no central registry to keep in sync.

---

## Caveats

- This is a **teaching example**, not a production research system. The data sources are public ones (SEC EDGAR, Yahoo Finance) and the news coverage is limited to what those sources surface.
- The agent does not place trades, does not email, does not post anywhere. It writes files in `./agent-outputs/` and surfaces them to you.
- Numbers in the workbook are sourced from the latest filing the agent could find. They are not a substitute for a Bloomberg terminal or a sell-side model.
- The stress test scenarios are starting points for a conversation, not predictions.

# Plan — Refactor `market-researcher` into `stock-analyzer`

**Audience for the finished example:** domain experts in finance/research who have not personally built a Claude agent. The repo doubles as a teaching artifact: opening it should make "what is an agent? what is a skill?" click.

**Authored:** 2026-05-09
**Last updated:** 2026-05-09 (added ticker-data, xlsx-author, thesis-stress-test, explain-agent; venv discipline; recalc verification)

---

## Goal

Refactor the existing sector/thematic primer agent into a **single-stock-analyzer** that:

1. **Discovers** tickers worth considering today via web search + market-data MCPs.
2. **Caches** raw data per ticker (filings, quotes, prices, news, peers) so other skills don't re-fetch.
3. **Analyzes** each candidate (business snapshot, news, peer context, key debates).
4. **Studies** revenue / growth trajectory (MoM, QoQ, YoY) into a 3-tab `.xlsx` workbook.
5. **Stress-tests** the resulting thesis (what-if scenarios, falsifiable claims, contrarian steelman).
6. **Produces** an HTML report linking to per-ticker workbooks.
7. **Explains itself** — an `explain-agent` skill emits an interactive HTML diagram on localhost.

## Final structure

```
.claude/
  agents/
    stock-analyzer.md              # the orchestrator
  skills/
    ensure-deps/SKILL.md           # pre-flight environment check
      scripts/check.py
      requirements.txt             # canonical Python deps (owned by this skill)
    ticker-discovery/SKILL.md      # find candidates today
    ticker-data/SKILL.md           # pull filings/quotes/news into ./agent-outputs/<TICKER>/raw/
    stock-analysis/SKILL.md        # qualitative read for one ticker
    growth-study/SKILL.md          # MoM/QoQ/YoY trajectory + xlsx output
    xlsx-author/SKILL.md           # shared workbook discipline (consumed by growth-study)
      scripts/recalc.py            # LibreOffice headless recalc + error scan
    thesis-stress-test/SKILL.md    # validate the read with scenarios + steelman
    explain-agent/SKILL.md         # generate interactive diagram of how the agent works
      scripts/serve.py
      templates/diagram.html.j2
    _archive/                      # superseded skills, kept for reference
  plans/
    refactor-to-stock-analyzer.md  # this file
  settings.json                    # project permissions
.venv/                             # project-local Python venv (created by user)
claude -> .claude                  # symlink (Finder visibility)
Open in Claude.command             # double-clickable launcher
README.md                          # teaches agent vs. skill, walks the example
```

## Skill mapping (old → new)

| Old skill              | Action      | New skill              | Notes |
|------------------------|-------------|------------------------|-------|
| `idea-generation`      | repurpose   | `ticker-discovery`     | Pivot from screening pre-defined criteria to web-search-driven daily sweep. |
| `competitive-analysis` | merge       | `stock-analysis`       | Collapse into single-name research (business, results, peers, debates). |
| `sector-overview`      | merge       | `stock-analysis`       | Sector/macro context becomes one section inside per-ticker analysis. |
| `comps-analysis`       | repurpose   | `growth-study` + `xlsx-author` | Workbook discipline split into a shared skill; growth-study points at MoM/YoY revenue trajectory. |
| `pptx-author`          | drop        | —                      | Output is HTML, not slides. |
| (new)                  | add         | `ticker-data`          | Source-of-truth fetcher; idempotent cache at `./agent-outputs/<TICKER>/raw/`. |
| (new)                  | add         | `xlsx-author`          | Shared formulas-not-hardcodes discipline. Recalc verification. |
| (new)                  | add         | `thesis-stress-test`   | Validates the read so the agent doesn't ship a news summary as analysis. |
| (new)                  | add         | `explain-agent`        | Self-explanation as a skill — interactive HTML diagram on localhost. |
| (new)                  | add         | `ensure-deps`          | Pre-flight environment check. Owns the canonical `requirements.txt`. Runs as workflow step 0. |
| (new)                  | add         | `stock-discovery`      | Pure setup sweep (Form 4, 13F, buyback 8-Ks, post-spins, coverage gaps, options, politician trades). No judgment — returns every name that clears each setup's threshold. |
| (new)                  | add         | `hidden-opportunities` | Judgment layer on top of `stock-discovery`. Applies the asymmetry filter and returns 3-5 names. |

Old skills are moved to `.claude/skills/_archive/`, not deleted, so the teaching example can show the before/after.

## Data-source policy (applies to all skills)

Priority order — try each tier before the next:

1. **MCP servers** (if connected): EdgarTools (filings), Alpha Vantage (quotes/fundamentals), Finnhub (news/analyst), FRED (macro), Yahoo Finance MCP.
2. **Python libraries** via Bash: `edgartools`, `yfinance`, `sec-edgar-downloader`, `pandas-datareader`. **Always invoke via `./.venv/bin/python3`** — never bare `python3`, which would miss the project venv.
3. **WebFetch** scrape-friendly sources: `finance.yahoo.com`, `stockanalysis.com`, `efts.sec.gov`, `www.sec.gov`. Avoid finviz (rate-limited), Bloomberg/Refinitiv (paywall).

Skills cite sources in the deliverable; `[UNSOURCED]` if a number can't be traced.

## Workbook discipline (xlsx-author)

Pulled out from `growth-study` so multiple skills (and future ones, like a peer-comps workbook) share the conventions instead of restating them.

- Formulas reference input cells. Never hardcode derived values.
- Every raw input has a comment citing the source (filing, page, accessed date).
- Color semantics: blue text = inputs, black = formulas, green = cross-sheet refs, red = external refs. Yellow background `#FFF2CC` = key assumptions the user can override.
- Headers: navy `#1F4E79` (section), light blue `#D9E1F2` (column), light gray `#F2F2F2` (stats rows).
- Numbers: percentages 1 decimal, multiples `Nx`, dollars no decimals + thousands separator, years stored as text.
- **Mandatory recalc verification.** openpyxl writes formula *strings* but doesn't evaluate them. After saving, run `./.venv/bin/python3 .claude/skills/xlsx-author/scripts/recalc.py ./agent-outputs/<TICKER>.xlsx` — pure-Python evaluation via the `formulas` package — to scan for `#REF!`/`#DIV/0!`/etc. errors.

Drawn from Anthropic's official xlsx skill (github.com/anthropics/skills/skills/xlsx) so users transferring between projects find the same conventions.

## Validation discipline (thesis-stress-test)

Without this, the agent stops at "here's the read" — which is a news summary, not analysis. The skill:

1. Restates the working thesis as a single what/why/by-when sentence.
2. Runs 3–5 stress scenarios (revenue halves, margins compress 200bps, catalyst slips, etc.) with shown math.
3. Lists 3–4 falsifiable claims (specific, observable, dated).
4. Steelmans the contrarian view with cited data.
5. Issues a verdict: *Holds / Cracks under [scenario] / Already broken*.

## Self-explanation (explain-agent)

The agent explains itself as part of the deliverable. `./.venv/bin/python3 .claude/skills/explain-agent/scripts/serve.py`:

1. Walks `.claude/agents/` and `.claude/skills/*/SKILL.md` to build the event/skill graph dynamically.
2. Writes `./agent-outputs/agent-diagram.json` (regenerable source of truth) and `./agent-outputs/agent-diagram.html` (self-contained, offline-capable).
3. Serves on localhost (port 8765 or next free) and opens the browser.

Visual style borrows the warm earthy palette + stacked horizontal timeline aesthetic of `code.claude.com/docs/en/context-window`. The diagram updates automatically as skills are added or removed because the event list is generated, not hardcoded.

## Agent behavior

- **Input:** any of `analyze the market today`, a sector hint, or a list of tickers. If no input, default to a daily sweep.
- **Workflow:**
  0. `ensure-deps` → readiness check (venv, packages, LibreOffice, ./agent-outputs/). Stop if not ready.
  1. `ticker-discovery` → shortlist of 3–7 names with one-line reasons. **Stop, confirm with user.**
  2. For each approved ticker (parallel): `ticker-data` → cache.
  3. For each ticker (parallel): `stock-analysis` (qualitative) and `growth-study` (workbook, runs `recalc.py` before finishing).
  4. For each ticker (sequential after stock-analysis): `thesis-stress-test`.
  5. Assemble HTML report at `./agent-outputs/report-YYYY-MM-DD.html` linking to `./agent-outputs/<TICKER>.xlsx`.
- **Stop points:** after discovery (confirm shortlist), after the report draft.

## Deliverable spec

- **`./agent-outputs/report-YYYY-MM-DD.html`** — top section: market context + shortlist. Per-ticker section: thesis hook, recent news, growth snapshot, stress-test verdict, link to `.xlsx`.
- **`./agent-outputs/<TICKER>.xlsx`** — three tabs (Fundamentals, News, Historical), built per `xlsx-author` conventions, recalc-verified.
- **`./agent-outputs/<TICKER>/raw/`** — `manifest.json`, `filings/`, `quote.json`, `prices/daily-2y.csv`, `news.json`, `peers.json`. Idempotent with staleness windows.
- **`./agent-outputs/agent-diagram.html`** + **`./agent-outputs/agent-diagram.json`** — generated by `explain-agent` on demand.

## Project settings (`.claude/settings.json`)

Allowlist common read-only / safe operations so the agent runs without permission churn:

- Bash: `python3 *`, `pip install *`, `uv run *`, `mkdir *`, `open ./agent-outputs/*`
- WebFetch: yahoo finance, stockanalysis.com, sec.gov, efts.sec.gov, finnhub.io, alphavantage.co
- Read/Edit/Write: scoped to `./agent-outputs/**`

Deny: reads/edits to `.env`, `rm -rf *`, raw `curl`/`wget` (force WebFetch).

## Python environment

- Project-local venv at `.venv/` (user creates with `python3 -m venv .venv`).
- All Python invocations: `./.venv/bin/python3` — bare `python3` would use the system interpreter and miss `openpyxl`, `yfinance`, etc.
- Dependencies in `.claude/skills/ensure-deps/requirements.txt` (owned by the `ensure-deps` skill): openpyxl, yfinance, edgartools, pandas, pandas-datareader, requests, jinja2, plotly.
- LibreOffice required for `recalc.py`; auto-detected at common paths, install hint printed if missing.

## README angle

Three-section walkthrough:

1. **What is this?** — In plain language: the agent is the senior analyst; the skills are the playbooks. Show how `stock-analyzer.md` *delegates* and how each `SKILL.md` *contains the how-to*.
2. **Run it yourself** — `cd` here, run `claude`, ask "what's worth looking at today?", watch the agent invoke each skill, open the report.
3. **See it visually** — run the `explain-agent` skill to open the localhost diagram.

## What NOT to do

- Don't introduce new abstractions (no orchestration framework, no shared "utils" skill).
- Don't preserve `pptx-author` for "future flexibility."
- Don't add backwards-compatibility shims; the old market-researcher agent is being replaced, not extended.
- Don't over-comment skill files. Skills are self-contained and should read top-to-bottom by a domain expert without a programming background.
- Don't restate `xlsx-author` rules inside `growth-study`. The whole point of the split is that `growth-study` references and `xlsx-author` defines.

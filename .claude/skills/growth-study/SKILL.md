---
name: growth-study
description: Spread a single ticker's revenue and growth trajectory (MoM, QoQ, YoY) into an institutional-grade Excel workbook with three tabs — Fundamentals, News, Historical. Outputs ./agent-outputs/<TICKER>.xlsx referenced by the HTML report. Use after stock-analysis, when the qualitative story needs the numbers behind it. Triggers on "growth study", "build the model", "spread the financials", "MoM YoY analysis", or "make the workbook".
---

# Growth Study

Build the per-ticker workbook that grounds the recommendation. This is the audit trail — every claim in the HTML report should trace back to a cell here.

This skill is the **content** of the workbook (which metrics, which tabs, which sources). The **form** (formulas-not-hardcodes, comment-every-input, color conventions, recalc verification) lives in `xlsx-author`. Read that skill first if you haven't already — this one assumes those rules.

## Data-source priority

1. **MCP servers first** if connected — `edgartools` for filings, `alphavantage` / `finnhub` / `yahoo_finance` for fundamentals + quotes, `fred` for macro context.
2. **Python libraries via Bash** — `edgartools` (parsed XBRL filings), `yfinance` (price + statements), `sec-edgar-downloader` (raw filings).
3. **WebFetch** scrape-friendly: `www.sec.gov`, `efts.sec.gov`, `finance.yahoo.com`, `stockanalysis.com`. Skip finviz, Bloomberg, Refinitiv.

**Never use web search as a primary data source.** It lacks the citation discipline this workbook requires.

Inputs that the `ticker-data` skill already cached at `./agent-outputs/<TICKER>/raw/` should be read from disk, not re-fetched.

## Output contract

Write `./agent-outputs/<TICKER>.xlsx`. Three tabs, in order:

1. **Fundamentals** — the metrics actually used to make the recommendation
2. **News** — recent material headlines (last ~30 days)
3. **Historical** — quarterly revenue + growth-rate trajectory

Run `recalc.py` before declaring the workbook done (see xlsx-author). Return the relative path in your final message so the HTML report can link to it.

## Tab 1 — Fundamentals

Header rows:

| Row | Content |
|---|---|
| 1 | `<TICKER> — FUNDAMENTALS` (merged across the table; navy fill, white bold) |
| 2 | `As of: <YYYY-MM-DD> · Currency: USD millions except per-share` |
| 3 | (blank) |

Then a metrics block. Pick metrics that match the business — don't list every possible ratio:

```
| Metric                  | Latest Q | YoY Δ    | 4Q ago | 4Q Δ | Source        |
| Revenue                 | <input>  | =B5/D5-1 | <input>|      | 10-Q Q1 FY26  |
| Gross profit            | <input>  |          | <input>|      | 10-Q Q1 FY26  |
| Gross margin            | =B6/B5   |          | =D6/D5 |      | calc          |
| Operating income        | <input>  |          | <input>|      | 10-Q Q1 FY26  |
| Operating margin        | =B8/B5   |          |        |      | calc          |
| Net income              | <input>  |          | <input>|      | 10-Q Q1 FY26  |
| Diluted EPS             | <input>  |          | <input>|      | 10-Q Q1 FY26  |
| Free cash flow          | <input>  |          | <input>|      | 10-Q Q1 FY26  |
| Shares outstanding (M)  | <input>  |          | <input>|      | 10-Q Q1 FY26  |
```

Below the metrics: a **Recommendation Drivers** block — 3-5 cells naming the specific drivers used to make the call (e.g., "Data-center segment Q1 +73% YoY"), each pointing to the cell that backs it.

7 metrics that tell the story beats 15 that don't. Resist the urge to pad.

## Tab 2 — News

Header row + one row per item:

| Date | Source | Headline | One-line summary | Link |
|------|--------|----------|------------------|------|
| 2026-05-22 | 10-Q | NVDA Q1 FY26 results | Revenue $26.1B, +73% YoY, data-center segment +83% | https://www.sec.gov/... |
| 2026-05-08 | 8-K | Earnings press release | Beat top + bottom; raised Q2 guide to $28B mid | https://www.sec.gov/... |

- Up to ~10 items, last 30 days.
- Filings, guidance changes, M&A, regulatory actions, executive moves. Skip routine analyst notes and price-action commentary.
- Link column is a real Excel hyperlink, not a string: `cell.hyperlink = url; cell.style = "Hyperlink"`.

If `ticker-data` already wrote `news.json`, read it instead of re-fetching.

## Tab 3 — Historical

Quarterly trajectory, oldest left to newest right (one orientation per workbook). Minimum 8 quarters of revenue.

```
|              | Q1'24 | Q2'24 | Q3'24 | Q4'24 | Q1'25 | Q2'25 | Q3'25 | Q4'25 | Q1'26 |
| Revenue ($M) | 7,192 | 13,507| 18,120| 22,103| 26,044| 30,040| 35,082| 39,331| ...   |
| QoQ growth   |       |=C2/B2-1|...   |       |       |       |       |       |       |
| YoY growth   |       |       |       |       |=F2/B2-1|...    |       |       |       |
```

Years stored as text (`"2024"`), not numbers — avoids accidental arithmetic.

If the company is consumer / retail / marketplace and discloses monthly KPIs, add a monthly block beneath the quarterly one with MoM growth.

Add a small `LineChart` visualizing revenue and YoY growth, anchored next to the data — not floating.

## Workflow

1. **Confirm the ticker** with the user. If multi-class shares (BRK.B, GOOGL vs GOOG), pick the one with deeper analyst coverage and note the choice.
2. **Read cached data** from `./agent-outputs/<TICKER>/raw/` if `ticker-data` ran. Otherwise pull via `edgartools`/`yfinance` and write back to that location for reuse.
3. **Write the openpyxl script** that builds all three tabs in one workbook. Invoke via `./.venv/bin/python3 build_<TICKER>.py` — never bare `python3`.
4. **Verify step-by-step** before finishing: show Fundamentals, get sanity check, then proceed to historical and news. Don't build end-to-end and present.
5. **Recalculate and verify** with `./.venv/bin/python3 .claude/skills/xlsx-author/scripts/recalc.py ./agent-outputs/<TICKER>.xlsx`. Fix any errors before finishing.
6. **Save** and return the relative path.

## Sanity checks (in addition to xlsx-author's general checks)

- YoY growth rates make sense vs. peer-group magnitude (flag obvious outliers).
- Historical block has at least 8 quarters; older if the user requested.
- Every news item has a date and a real hyperlink.
- Same metric shows the same value on every tab where it appears.

## Standards

- **Same metric definitions across companies** when comparing — don't mix EBITDA definitions (e.g., adjusted vs. reported) silently.
- **Same fiscal period** when comparing. Flag exceptions explicitly.
- **Convert FX to USD** for international names; note the rate and date in the Fundamentals header.
- **Missing data** shows as `-` or `N/A` with `[E]` if estimated. Never blank.
- **No advice in cells.** Cells contain numbers and citations. Judgment lives in the markdown deliverable and the HTML report.

## Common mistakes to avoid

- ❌ Re-stating xlsx-author's rules instead of just following them. Read that skill once and trust the conventions.
- ❌ Mixing fiscal periods (LTM vs Q1) in the same row without flagging.
- ❌ Adding 15 metrics when 7 tell the story.
- ❌ Skipping the recalc step and shipping a workbook with `#DIV/0!` cells.
- ❌ Re-fetching data `ticker-data` already cached.

## What this skill is not

- **Not workbook formatting discipline.** That's `xlsx-author`.
- **Not data fetching.** That's `ticker-data`.
- **Not the analysis.** Numbers here ground the read; the read itself lives in `stock-analysis`.
- **Not the deliverable.** The HTML report is assembled by the agent, separately, using this workbook as one of its inputs.

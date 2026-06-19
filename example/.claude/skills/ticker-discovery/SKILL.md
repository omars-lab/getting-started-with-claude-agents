---
name: ticker-discovery
description: Surface 3-7 stocks worth a closer look today by sweeping news, earnings, analyst actions, and unusual price/volume moves. Use when an analyst asks "what's interesting today?", "anything moving?", or hands over a sector and wants a starting basket. Triggers on "find tickers", "daily sweep", "what's worth looking at", or "stock screen for today".
---

# Ticker Discovery

A morning triage skill. Pull the threads the market is pulling on right now and hand back a short, defensible list.

## Output contract

A markdown shortlist, 3-7 names, in this exact shape:

```
| Ticker | Reason today (one line) | Source |
|--------|-------------------------|--------|
| NVDA   | Q1 print beat top + bottom; data-center revenue +73% YoY | NVDA 8-K, 2026-05-08 |
| ...    | ...                     | ...    |
```

Then a one-paragraph "what I left out and why" so the user can push back. **Stop here and wait for the user to approve the list before anything deeper happens.**

## Workflow

### Step 1 — Read the brief

Three inputs to confirm before searching:

- **Direction** — long ideas, short ideas, or both? Default: long-biased catalyst sweep.
- **Universe** — broad market, a sector, or a watchlist the user will paste? Default: broad US large/mid cap.
- **Time horizon** — today's news only, this week, or last 30 days? Default: today + last 5 trading days.

If the user said nothing, run defaults and flag the assumptions in the "what I left out" paragraph.

### Step 2 — Sweep the catalysts

Pull threads in this order. Stop once you have ~10 candidates worth filtering.

**A. Earnings movers (highest signal)**
- Companies that reported in the last 1-3 sessions
- Look for: beat-and-raise, miss-and-cut, guidance changes, segment surprises
- Source: company 8-Ks via EDGAR; earnings-calendar pages on stockanalysis.com / Yahoo Finance

**B. Material news / 8-K filings**
- M&A announcements, product launches, regulatory actions, lawsuits, restatements
- Source: SEC EDGAR full-text search (`efts.sec.gov`), company press releases, Finnhub MCP if available

**C. Analyst actions**
- Notable upgrades / downgrades / large target-price moves from major shops
- Be skeptical: most are noise. Flag only when the move is >15% target change or comes from the lead-coverage analyst

**D. Unusual price / volume**
- Names up/down >5% on >2x average volume, with a clear narrative reason
- Skip names where the move is unexplained — those are traps, not ideas

**E. Macro / sector catalysts**
- Fed decisions, CPI prints, oil moves, FX swings — only if they meaningfully reshape the day's risk
- FRED MCP is the cleanest source if available; otherwise reputable news outlets

### Step 3 — Filter to 3-7

Cut ruthlessly. A name belongs on the shortlist only if you can finish this sentence:

> "Worth a closer look today because [one specific, sourced reason]."

If the reason is "stock is up a lot" without a *why*, it's not a candidate. If the reason is "AI tailwind," it's too generic — find the specific tailwind for this name on this day.

Aim for 3-7. Five is the sweet spot. More than 7 means you didn't filter; fewer than 3 means broaden the sweep.

### Step 4 — Present and stop

Return the table + "what I left out" paragraph. Then stop. Do not start analyzing tickers until the user picks which ones make the cut.

## Data sources, in priority order

1. **MCP servers** (if connected) — `finnhub` for news + analyst actions, `alphavantage` for quotes + earnings calendar, `edgartools` for 8-K text, `yahoo_finance` for movers.
2. **Python via Bash** — `yfinance` for quotes/movers, `edgartools` for filings, `pandas-datareader` for FRED data.
3. **WebFetch** — `finance.yahoo.com/calendar/earnings`, `stockanalysis.com/markets/gainers`, `efts.sec.gov/LATEST/search-index?q=...&forms=8-K`. Don't scrape finviz (aggressive rate limiting) or paywalled outlets.

## What this skill is not

- **Not a screener for valuation/quality.** That's a separate, slower workflow. This is "what catalyst is live today."
- **Not a fundamental view.** A ticker on the shortlist is a candidate for analysis, not a conclusion.
- **Not advice.** Reasons cite events; they don't recommend action.

## Common mistakes to avoid

- **Recency bias** — yesterday's mover is not automatically today's idea. If the catalyst is already 3 sessions old and priced in, drop it.
- **Stale catalysts** — "Company X announced earnings" without saying *what* about earnings. The reason has to be specific.
- **Crowded trades** — if a name has been on every shortlist for a week, the marginal idea value is low. Note it, deprioritize it.
- **Listing every mover** — the value is in the cut, not the gather.

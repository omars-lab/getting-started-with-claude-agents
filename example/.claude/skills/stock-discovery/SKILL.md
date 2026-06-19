---
name: stock-discovery
description: Pure data sweep — scans SEC filings (Form 4, 13F, 8-K, S-1), price/volume, options chains, and politician trade disclosures for names that pattern-match specific setups. Returns a *grouped candidate list* with sourced data points, no judgment applied. Use when the user asks to "find candidates", "scan for setups", "what's the smart money doing", or as the upstream feed for `hidden-opportunities`. Distinct from `ticker-discovery`, which is news/catalyst-driven (today's earnings, 8-Ks, analyst actions); this skill is setup-driven and does not require a news catalyst.
---

# stock-discovery

The data layer. Scans for names that match specific, observable setups — *every* name that clears the threshold gets surfaced. No filtering for "is the consensus missing this?" — that judgment belongs to `hidden-opportunities`.

This separation matters: discovery should be wide and reproducible (run it twice, get the same names). Judgment should be narrow and opinionated (apply the asymmetry filter).

## Output contract

Grouped JSON saved to `./agent-outputs/discovery/<YYYY-MM-DD>.json`, plus a markdown summary:

```json
{
  "swept_at": "2026-05-09T17:30:00Z",
  "universe": "unconstrained",
  "setups": {
    "insider_buying_cluster": [
      {"ticker": "XYZ", "data": {"buyers": 4, "total_value_usd": 12000000, "earliest": "2026-04-12"}, "source": "Form 4 filings via EDGAR"}
    ],
    "13f_accumulation": [
      {"ticker": "CPRT", "data": {"holder": "Akre Capital", "share_change_pct": 85.7, "value_usd": 308000000}, "source": "13F-HR 2026-02-13 acc 0001112520-26-000008"}
    ],
    "buyback_authorization": [...],
    "post_spin_orphan": [...],
    "coverage_gap": [...],
    "unusual_options": [...],
    "distressed_not_broken": [...],
    "politician_cluster": [...]
  }
}
```

The markdown summary is a per-setup table with one row per candidate. No "what I dismissed" paragraph — that's the judgment skill's job. **Do not pre-filter.** If the insider-buying sweep finds 40 names, return 40.

## What gets swept

| Setup | Threshold | Source |
|---|---|---|
| **Insider buying cluster** | 3+ insiders open-market purchases (code "P"), 60-90 day window, ≥$1M total | Form 4 XML via EDGAR |
| **13F accumulation** | New position OR >+10% share add by a defined trusted-holder list (Baupost, Akre, Pabrai, Polen, etc.) | 13F-HR XML via EDGAR |
| **Buyback authorization** | Board authorizes ≥5% of float, 8-K filed in last 90 days | 8-K full-text via EDGAR |
| **Post-spin orphan** | S-1/S-4 spin filed 12-24 months ago, ≤3 sell-side analysts | S-1 corpus + Finnhub analyst count |
| **Coverage gap** | Market cap >$1B, ≤2 analysts | Finnhub `recommendation-trends` or stockanalysis.com |
| **Unusual options activity** | Call OI ratio >5x 30-day avg, no public catalyst | yfinance options chain |
| **Distressed-but-not-broken** | Down >40% from 52w high, FCF positive last 4 quarters | yfinance prices + cashflow |
| **Politician trade cluster** | 3+ distinct Congress members trading same ticker, same direction, 30-day window | capitoltrades.com (free, no auth) |

The same name surfacing under multiple setups is *not* deduplicated here. Cross-setup confirmation is itself signal — but it's `hidden-opportunities`' job to weight that.

## Workflow

### Step 1 — Confirm the brief

Two parameters:
- **Universe** — small-cap (<$2B), mid-cap ($2B-$10B), large-cap, or unconstrained. Default: $500M-$10B (band where coverage gaps are most common).
- **Setups to sweep** — all 8, or a subset (e.g., "smart-money only" = insider + 13F).

### Step 2 — Run each sweep

Each sweep is independent — run them in parallel where the data source allows (EDGAR rate-limits, so SEC sweeps serialize naturally). All Python invocations go through `./.venv/bin/python3` and use a UA header identifying the requester for EDGAR access.

For each setup, pull *all* matches above the threshold. Cap at 50 per setup if it gets unwieldy, but log the cap in the output.

### Step 3 — Save grouped output

Write `./agent-outputs/discovery/<YYYY-MM-DD>.json` and `./agent-outputs/discovery/<YYYY-MM-DD>.md`. Hand off the path to whatever skill consumes it (typically `hidden-opportunities`).

## Standards

- **Sourced.** Every row cites the filing accession number, URL, or the timestamp+source for non-SEC data.
- **Reproducible.** Two runs on the same day with the same brief produce the same output. No randomness, no LLM judgment in this layer.
- **Pre-judgment.** Don't decide which names are "interesting." Surface all matches.
- **Setup-typed.** Every row is tagged with which setup surfaced it. A name appearing in two setups gets two rows.

## Common mistakes to avoid

- ❌ **Pre-filtering for "interesting" names.** That's `hidden-opportunities`. This skill is the firehose.
- ❌ **Deduping across setups.** Cross-setup confirmation is signal, not noise.
- ❌ **Adding qualitative columns** (e.g., "thesis quality"). Output is data only.
- ❌ **Skipping the threshold check** to fill a setup's table. If the sweep finds zero matches, the setup's array is empty — that's fine.

## What this skill is not

- **Not a judgment layer.** No asymmetry filter, no shortlist, no "what I dismissed." See `hidden-opportunities`.
- **Not a news scan.** That's `ticker-discovery`. This skill is setup-driven, not catalyst-driven; the two complement each other.
- **Not a fundamental analysis.** Outputs are pointers to candidates. Per-name analysis lives in `stock-analysis` and `growth-study`.

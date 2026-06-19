---
name: hidden-opportunities
description: Apply the asymmetry filter to a candidate list — surface 3-5 names where the consensus is *not yet looking*. Consumes the grouped output from `stock-discovery` (or a hand-supplied list) and returns a defensible shortlist plus a "what I dismissed and why" paragraph. Use when the user asks for "hidden gems", "under-followed names", "what's flying under the radar", "smart-money positioning", or wants ideas off the consensus path. Distinct from `ticker-discovery` (catalyst-driven daily sweep) and from `stock-discovery` (raw setup sweep with no judgment applied).
---

# Hidden Opportunities

`stock-discovery` is the firehose — it returns every name that pattern-matches a setup. This skill is the filter. It answers: *of all the candidates surfaced, which ones is the consensus actually missing — and why?*

The bar is high. A "hidden gem" without a specific, sourced setup *and* a specific reason the consensus isn't watching is just a guess. Each name on the shortlist has to clear the test:

> "This is asymmetric because [the consensus is not seeing X], and the data point that proves the consensus isn't seeing it is [Y]."

If you can't fill in both blanks with a specific X and a specific Y, drop the name.

## Output contract

A markdown shortlist, 3-5 names:

```
| Ticker | Setup | Why under-followed | Source |
|--------|-------|--------------------|--------|
| CPRT   | Akre +85.7% share add (Q4 13F); stock -47% from 52w high | Mid-cap industrial, 9 analysts, consensus "hold" — desks de-rated post-drawdown | Akre 13F-HR 2026-02-13 acc 0001112520-26-000008; yfinance 2026-05-09 |
| ...    | ...   | ...                | ...    |
```

Then a **"what I dismissed and why"** paragraph that names the candidates that didn't clear the bar and the specific reason each was cut. **Stop here and wait for the user to approve before deeper analysis.**

If fewer than 3 candidates clear the bar, return fewer with an explicit "thin pickings today" note. **Don't lower the bar to fill the table.**

## Workflow

### Step 1 — Get the candidate list

Either:
- **Read `./agent-outputs/discovery/<YYYY-MM-DD>.json`** if `stock-discovery` ran today, or
- **Invoke `stock-discovery`** if it hasn't been run, or
- **Accept a hand-supplied list** if the user is bringing names from outside the agent.

The judgment layer doesn't care where the candidates came from. It only judges.

### Step 2 — Apply the asymmetry filter

For each candidate, finish this sentence:

> *"This is asymmetric because [the consensus is not seeing X], and the data point that proves the consensus isn't seeing it is [Y]."*

X has to be specific (not "stock is cheap"). Y has to be a dated, sourced data point (a filing, an analyst count, a price drawdown).

Examples that pass:
- *"Consensus isn't seeing that Akre Capital is a low-turnover concentrated holder buying aggressively into a 47% drawdown — Y = +85.7% share add filed 2026-02-13."*
- *"Consensus dropped coverage when the stock fell out of major data feeds — Y = yfinance 404, Akre still added +52.7% in the same quarter."*

Examples that fail:
- *"Stock is undervalued"* (X is not specific)
- *"Insiders are bullish"* (Y is not dated/sourced)
- *"Trades at a discount to peers"* (neither X nor Y)

### Step 3 — Cross-setup weighting

A name that surfaces under **two or more setups** in the discovery output is a *strong candidate* and should be elevated. A name surfacing under one setup is a *candidate*. Use this to break ties and prioritize the shortlist.

### Step 4 — Cut to 3-5 and diversify

Aim for 3-5. Diversify across setup types — five names from "13F accumulation" is one bet on Akre, not five separate ideas. If the discovery output is dominated by one setup, surface the diversity gap as a note.

### Step 5 — Present and stop

Return the table + "what I dismissed and why" paragraph. Stop. Wait for the user to pick which to analyze deeper via `stock-analysis` / `growth-study`.

## Standards

- **Sourced or it doesn't count.** Every row cites the discovery source (filing accession, URL, timestamp).
- **Specific, not generic.** "Cheap" is not a setup. "Trades at 0.7x revenue with $300M net cash and FCF positive last 4 quarters" is.
- **Dated.** Anything older than 90 days is stale and gets dropped unless the user explicitly extends the window.
- **Diversified.** A shortlist of 5 insider-buying names is one idea, not five.
- **Honest about what didn't run.** If `stock-discovery` couldn't sweep a setup type (e.g., no Form 4 crawler today), say so in the dismissal paragraph rather than claiming it returned zero matches.

## Common mistakes to avoid

- ❌ **Recomputing the discovery sweep here.** That's `stock-discovery`'s job. This skill consumes its output.
- ❌ **Survivorship bias.** A trusted holder *bought* doesn't mean they bought *recently* or *are still holding* — 13Fs are 45 days stale by the time they're public. Verify the filing date.
- ❌ **Coverage gaps that aren't gaps.** A name with "1 analyst covering" might be a foreign listing US analysts don't pick up — not a true under-followed setup.
- ❌ **Politician-trade noise.** A single politician trading SPY isn't signal. Cluster threshold (3+ reps, same direction, 30-day window) is the bar `stock-discovery` enforces; if `hidden-opportunities` sees a single-rep row in the candidate list, it's a discovery bug — flag it, don't surface it.
- ❌ **Distressed names dressed as hidden gems.** Down 80% with declining revenue isn't a "hidden gem" — it's a falling knife. Apply the FCF-positive filter unless the user explicitly asked for distressed.
- ❌ **Returning 5 names just to fill the table.** If 2 clear the bar, return 2.

## What this skill is not

- **Not a discovery sweep.** That's `stock-discovery`. This skill assumes candidates already exist.
- **Not a fundamental view.** A name on the list is a *candidate for `stock-analysis`*, not a conclusion.
- **Not a substitute for `ticker-discovery`.** Catalyst-driven names belong there. Use both pipelines when the user wants both perspectives.
- **Not advice.** Setups create asymmetric *opportunity to analyze*. They don't recommend action.

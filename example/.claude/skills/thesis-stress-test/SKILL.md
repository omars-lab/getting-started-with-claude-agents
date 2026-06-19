---
name: thesis-stress-test
description: Stress-test a working stock thesis by running "what if X happens" scenarios against the model, surfacing falsifiable claims, and steelmanning the contrarian view. This is how the agent validates its own recommendations before presenting them — answering "still a good investment if [shock] happens?" with a specific, sourced answer rather than hand-waving. Use after stock-analysis and growth-study have produced the read; before the HTML report is finalized. Triggers on "stress test", "what if", "validate the thesis", "steelman the bear", or "how does this break".
---

# Thesis Stress Test

How the agent validates its own work. Without this skill, the agent says "here's the read" and stops — which is a news summary, not analysis. With it, the agent says "here's the read, here's what would prove it wrong, and here's the strongest argument against it."

## Output contract

A markdown block appended to each ticker's section in the HTML report, structured exactly as:

```
### Stress test

**Working thesis (one sentence):** [the read from stock-analysis]

**Scenarios**

| Shock | Magnitude | Effect on thesis | Source for shock probability |
|---|---|---|---|
| Revenue growth halves | YoY 25% → 12% | [Specific consequence: which margins, which line items, which valuation level] | [recent precedent or analyst range] |
| Catalyst slips two quarters | Q2 → Q4 | ... | ... |
| Margin compresses 200bps | 47% → 45% | ... | ... |

**Falsifiable claims** — the data points that would prove this thesis wrong if observed:
- [Specific, dated, observable data point]
- ...

**Contrarian steelman** — the strongest version of the bear case (or bull, if the thesis is short):
- [Argument 1, with the data the contrarian points at]
- [Argument 2, ...]

**Verdict**: [Holds / Cracks under [specific scenario] / Already broken — see [claim]]
```

## Workflow

### Step 1 — Restate the thesis as a single sentence

Read the markdown deliverable from `stock-analysis`. Pull out the working thesis. If it takes more than one sentence to state, the thesis isn't sharp enough — push back to the user before stress-testing.

A thesis sentence has three parts: **what / why / by when**.

> "NVDA's data-center revenue grows 40%+ for FY27 because hyperscaler capex commits remain ahead of supply, and the Q2 print will likely raise full-year guide again."

Generic versions to reject: "NVDA is a strong long," "AI tailwinds are intact," "the AI trade has legs."

### Step 2 — Generate 3-5 stress scenarios

Pick scenarios that **could plausibly happen** and **would change the read** if they did. Both criteria — irrelevant scenarios are noise, impossible scenarios are theater.

Default scenario menu (pick 3-5, customize for the company):

| Scenario | When to use |
|---|---|
| **Revenue growth halves** | Test growth-rate sensitivity. Useful for any thesis built on a specific growth rate. |
| **Margin compresses 200bps** | Test operating leverage. Useful when the bull case is "margins expand." |
| **Catalyst slips one or two quarters** | Test timing dependence. Useful when the thesis names a specific event (product launch, FDA decision, court ruling). |
| **Top customer leaves** | Test concentration risk. Useful when one customer is >10% of revenue. |
| **Multiple compresses to 5-year median** | Test valuation premium. Useful when the stock trades >1 std dev above its history. |
| **Competitor closes the gap** | Test moat. Useful when the thesis assumes durability of a specific advantage. |
| **Macro: rates +200bps** | Test rate sensitivity. Useful for long-duration growth names and financials. |
| **Regulatory action lands** | Test specific regulatory exposure. Use when the company is in an open inquiry. |

For each scenario chosen, **show the math**:

> "If revenue growth halves from 25% to 12% YoY, FY27 revenue is $X (vs. consensus $Y) and operating income is $Z. At a sector-median 22x P/E, that's a $A stock vs. today's $B."

Reference cells in `./agent-outputs/<TICKER>.xlsx` if the math came from the workbook. Don't restate numbers without sourcing them.

### Step 3 — Identify falsifiable claims

A falsifiable claim is one a future data point could disprove. "Growth stays strong" is not falsifiable. "Q2 revenue >$28B" is.

Three or four claims is plenty. Each one:
- **Specific** — names a metric and a level
- **Observable** — comes from a future filing, print, or public data
- **Dated** — has a deadline (next earnings, next macro print, end of quarter)

> "Q2 FY26 data-center revenue must be ≥$22B for the trajectory to hold; below that, the supply constraint narrative weakens. Reports late August 2026."

### Step 4 — Steelman the contrarian

For a long thesis, write the strongest bear case. For a short thesis, the strongest bull. Use the same standards as the rest of the analysis: cite data, name the specific claim, no hand-waving.

The test: would a thoughtful investor on the other side of the trade recognize their own argument here? If they'd say "you didn't engage with my actual point," go back and find their actual point.

Two arguments is fine. Three is better. The bear-case data points often come from:
- Recent earnings-call Q&A (analysts ask the bear questions)
- The 10-K Risk Factors section (the company's own enumeration of what could go wrong)
- Sell-side notes from negative-rated coverage

### Step 5 — Verdict

One of three:
- **Holds** — Thesis survives the scenarios. Note which one came closest to breaking it.
- **Cracks under [scenario]** — A specific scenario flips the read. State the exact scenario and the level at which the thesis breaks.
- **Already broken — see [falsifiable claim]** — One of the falsifiable claims has already fired in observable data. The thesis was wrong; surface this prominently.

The verdict matters. A thesis that survives every scenario is suspicious — it usually means the scenarios were too soft. Push the magnitudes harder.

## Standards

- **Specific or it doesn't count.** "Margins compress" → "operating margin compresses 200bps from 47% to 45%."
- **Sourced or it doesn't count.** Shock magnitudes come from analyst ranges, historical precedent, or stated sensitivities — not from intuition.
- **Math, not vibes.** Each scenario shows the calculation, ideally referencing a cell in `./agent-outputs/<TICKER>.xlsx`.
- **No advice.** Output is "here's how the thesis behaves under stress." It does not say "you should sell" or "you should buy."

## Common mistakes to avoid

- ❌ **Hedge-everything verdicts** — "could go either way depending on execution" is not a verdict.
- ❌ **Symmetric scenarios** — "what if growth doubles vs. halves" is two scenarios, but if both lead to the same "depends" conclusion, you haven't stressed anything.
- ❌ **Strawman contrarians** — picking the weakest version of the bear case so it falls over.
- ❌ **Falsifiable claims with no date** — "if growth slows, the thesis breaks" is true but useless. When? Slows to what?
- ❌ **Recycling the bull case** — the contrarian section is not the same as the debates section in stock-analysis. Debates are open questions; the steelman is a complete opposing view.
- ❌ **Skipping the math** — "if X happens, the thesis breaks" without showing what the stock looks like in that scenario.

## What this skill is not

- **Not the analysis.** That's `stock-analysis`. This skill consumes its output and pressure-tests it.
- **Not a model.** Numbers come from `./agent-outputs/<TICKER>.xlsx`. This skill cites and recombines them.
- **Not advice.** It validates how a thesis behaves under shocks. It does not recommend action.
- **Not Monte Carlo.** Three to five hand-picked scenarios beat a thousand randomized ones, because the picks force engagement with the actual mechanism.

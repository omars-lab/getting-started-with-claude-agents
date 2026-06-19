# Archived skills

These skills are from the original `market-researcher` agent shape (sector / thematic primer with comps spread + slide pack). They are kept here for reference — they are *not* discovered by Claude Code because they live one level deeper than `.claude/skills/<name>/SKILL.md`.

| Old skill | Replaced by | Why |
|---|---|---|
| `sector-overview` | `stock-analysis` | Now per-ticker, not per-sector. Sector context is one section inside the per-ticker analysis. |
| `competitive-analysis` | `stock-analysis` | Competitive landscape collapses into peer-context within a single-name view. |
| `comps-analysis` | `growth-study` | Repurposed to MoM/QoQ/YoY revenue trajectory in `./out/<TICKER>.xlsx`. The "formulas not hardcodes + cite every input" discipline is preserved. |
| `idea-generation` | `ticker-discovery` | Pivoted from screening pre-defined criteria to web-search-driven daily catalyst sweep. |
| `pptx-author` | — (dropped) | Output is now an HTML report, not slide decks. |

To restore one, move it back up to `.claude/skills/<name>/`.

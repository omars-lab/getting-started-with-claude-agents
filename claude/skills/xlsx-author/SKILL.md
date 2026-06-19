---
name: xlsx-author
description: Build .xlsx workbooks the right way — formulas referencing input cells (never hardcoded results), every raw input commented with its source, consistent header/font/fill conventions. Use this skill when authoring any spreadsheet artifact in this project. Other skills (growth-study, future peer-comp workbooks) consume these conventions instead of re-stating them.
---

# xlsx-author

The shared discipline for any `.xlsx` produced in this project. If a skill writes a workbook, it follows these rules.

## ⚠️ Two non-negotiables

### 1. Formulas reference inputs. Never hardcode derived values.

```python
# Right — margin recomputes when revenue or COGS changes
ws["D5"] = "=C5/B5"

# Wrong — silent bug waiting to happen
ws["D5"] = 0.687
```

The only hardcoded values are **raw inputs** (revenue, EBITDA, share price). Every ratio, margin, growth rate, sum, average, percentile is a formula referencing input cells.

### 2. Every raw input has a comment citing its source.

```python
from openpyxl.comments import Comment

ws["B5"] = 26144
ws["B5"].comment = Comment(
    "Source: NVDA 10-Q FY26 Q1, filed 2026-05-22, "
    "Condensed Consolidated Statements of Income, Revenue line. "
    "Accessed via edgartools 2026-05-09.",
    "stock-analyzer"
)
```

If a number cannot be sourced, write `"[UNSOURCED]"` in the cell. Never estimate to fill space.

## Output contract

- Write to `./agent-outputs/<name>.xlsx`. Create `./agent-outputs/` if it doesn't exist.
- Return the relative path in your final message so the consumer (HTML report, agent) can collect it.

## Python environment

This project uses a **project-local venv** at `.venv/`. Always invoke Python via `./.venv/bin/python3`, never bare `python3` (which would use the system interpreter and miss `openpyxl`).

```bash
./.venv/bin/python3 -c "import openpyxl; print(openpyxl.__version__)"
```

If `.venv/` is missing, the user has not run setup yet. Direct them to the project README's setup step before proceeding.

## Visual conventions

Drawing from [Anthropic's official xlsx skill](https://github.com/anthropics/skills/tree/main/skills/xlsx) and standard finance-model conventions.

### Cell text colors (carry semantic meaning)

| Color | Meaning |
|---|---|
| **Blue** | Raw input — hardcoded value sourced from a filing, quote, or external system |
| **Black** | Formula — derived value computed from other cells |
| **Green** | Cross-sheet reference — formula reading from another tab in the same workbook |
| **Red** | External reference — formula reading from another workbook or external file |

### Cell fills

| Fill | Where |
|---|---|
| Dark blue `#1F4E79` | Workbook title and section header rows. White bold text on top. |
| Light blue `#D9E1F2` | Column headers. Black bold text, centered. |
| Light gray `#F2F2F2` | Statistics rows (max, percentiles, median, min). Black text. |
| **Yellow** `#FFF2CC` | Key assumptions — values the user might want to override |
| White | Default data rows |

The yellow-background convention matters: in a financial model, assumptions are the cells a portfolio manager will tweak. Marking them yellow tells the reader "this is where to push back."

### Typography

- Font: Calibri (modern) or Times New Roman (traditional finance) — pick one per workbook
- Data cells: 11pt
- Headers: 12pt bold
- Borders: none — clean and minimal

Numbers:

| Type | Format | Notes |
|---|---|---|
| Percentages | 1 decimal: `12.3%` | |
| Multiples | 1 decimal with 'x': `13.5x` | |
| Dollars ($M / $B) | No decimals, thousands separator: `26,144` | Unit declared in the row/column header, not repeated in cells |
| Margins | 1 decimal as percentage: `68.7%` | |
| Years | Stored as text, not numbers (avoids accidental arithmetic) | |
| Zeros | Displayed as `-` (custom format `#,##0;-#,##0;-`) | |

Layout:
- Uniform column widths (set them explicitly — don't rely on autofit)
- Consistent row heights (typically 20pt for data)
- All numbers center-aligned
- One blank row between data block and statistics
- No separate "STATISTICS" header row above quartiles

## Helper pattern (recommended)

If you're writing more than one workbook in a session, build small helpers and reuse them:

```python
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = PatternFill("solid", fgColor="1F4E79")
LIGHT_BLUE = PatternFill("solid", fgColor="D9E1F2")
LIGHT_GRAY = PatternFill("solid", fgColor="F2F2F2")
WHITE_BOLD = Font(color="FFFFFF", bold=True, size=12)
BLACK_BOLD = Font(color="000000", bold=True, size=11)
INPUT_BLUE = Font(color="1F4E79", size=11)

def section_header(ws, cell_range, text):
    cell = ws[cell_range.split(":")[0]]
    cell.value = text
    ws.merge_cells(cell_range)
    for row in ws[cell_range]:
        for c in row:
            c.fill = NAVY
            c.font = WHITE_BOLD

def raw_input(ws, coord, value, source):
    cell = ws[coord]
    cell.value = value
    cell.font = INPUT_BLUE
    cell.comment = Comment(source, "stock-analyzer")

def formula(ws, coord, expr):
    ws[coord] = expr  # openpyxl writes a leading "=" as a formula
```

Pull these into a single Python script per workbook — don't try to extract a shared library. Skills are meant to be self-contained.

## Office JS pitfall

If you're driving a live Excel session via Office JS (not headless), don't `.merge()` then set `.values` on the merged range — that throws `InvalidArgument`. Instead, write the value to the top-left cell first, then merge:

```js
ws.getRange("A1").values = [["TICKER — FUNDAMENTALS"]];
const hdr = ws.getRange("A1:H1");
hdr.merge();
hdr.format.fill.color = "#1F4E79";
hdr.format.font.color = "#FFFFFF";
hdr.format.font.bold = true;
```

This skill is primarily for the headless Python+openpyxl path; the Office JS note is here so the convention is consistent if a skill ever drives a live workbook.

## Recalculate and verify (mandatory)

openpyxl writes formula *strings* — it does not evaluate them. A workbook can save successfully and still be full of `#REF!` or `#DIV/0!` errors that only appear when Excel opens it. To catch this before handing the file off, evaluate every formula in pure Python and scan for errors.

This skill ships `scripts/recalc.py` exactly for that:

```bash
./.venv/bin/python3 .claude/skills/xlsx-author/scripts/recalc.py ./agent-outputs/<TICKER>.xlsx
```

The script:
1. Loads the workbook with the pure-Python `formulas` package (pip-installed, no system deps).
2. Compiles and evaluates every formula in the workbook.
3. Scans the computed values for error sentinels: `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NUM!`, `#NULL!`, `#SPILL!`, `#CALC!`.
4. Returns JSON: `{success: bool, total_formulas: N, errors: [{sheet, cell, error_type}]}`.

If the JSON reports errors, fix them and rerun before considering the workbook done. The dependency is in `.claude/skills/ensure-deps/requirements.txt` — `ensure-deps` blocks the run if it's missing.

## Verify step-by-step before finishing

Don't build the entire workbook end-to-end and then present it. Confirm with the user at each stage:

1. After header layout → "header looks right?"
2. After raw inputs are entered → "sources match what you expected?"
3. After formulas built → "margins / growth rates pass the sanity check?"
4. Then statistics, then save.

This catches errors when they're cheap to fix.

## Sanity checks before saving

- Gross margin > operating margin > net margin (always, by definition)
- Multiple reasonableness: `EV/Revenue` typically 0.5–20x, `EV/EBITDA` typically 8–25x, `P/E` typically 10–50x outside hypergrowth
- No `#DIV/0!` or `#REF!` cells
- Every blue cell has a comment
- Same metric shows the same value on every tab where it appears (no drift)

## Common mistakes to avoid

- ❌ Hardcoding a margin, growth rate, or ratio. Always reference input cells.
- ❌ Raw inputs without source comments.
- ❌ Mixing fiscal periods (LTM vs Q1) in one row without flagging.
- ❌ Inventing numbers to fill an empty cell.
- ❌ Adding 15 metrics when 7 tell the story.
- ❌ Skipping the verify-step-by-step protocol and presenting a 100-row workbook for review at the end.
- ❌ Introducing colors outside the navy / light-blue / light-gray / white palette without a user-supplied template.

## What this skill is not

- **Not a data fetcher.** Raw inputs come from `ticker-data` (or a peer skill). xlsx-author only formats and stores.
- **Not analysis.** Cells contain numbers and citations. Judgment lives in the markdown deliverables — not in the spreadsheet.
- **Not a slide deck.** No charts as primary output, no narrative — that's the HTML report.

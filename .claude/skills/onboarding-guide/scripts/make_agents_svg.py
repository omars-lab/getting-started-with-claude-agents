#!/usr/bin/env python3
"""Render the Claude Code `/agents` Library panel as an SVG mockup — proof that
stock-analyzer is a configured Project agent. Matches the real cream UI:

  › /agents                       (grey command bar)
  Agents   Running   [Library]    (tabs, Library active/blue)
    Create new agent
    Project agent (/Users/.../.claude/agents)
  stock-analyzer · inherit

Run via:  ./.venv/bin/python3 scripts/make_agents_svg.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)

W, H = 760, 300
CREAM = "#FBF4E4"
BAR = "#DAD8D2"
INK = "#33312E"
MUTED = "#6B6960"
BLUE = "#5B7FB0"
BLUE_FILL = "#4F6FBF"
RULE = "#C9C2AF"
MONO = "SF Mono, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, fill=INK, size=15, weight="400", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="10" fill="{CREAM}"/>',
    # command bar
    f'<rect x="14" y="14" width="{W-28}" height="34" rx="6" fill="{BAR}"/>',
    t(26, 36, "›", MUTED, 16),
    t(46, 36, "/agents", INK, 16, "600"),
    # separator
    f'<line x1="20" y1="70" x2="{W-20}" y2="70" stroke="{BLUE}" stroke-width="1.5"/>',
    # tabs
    t(34, 104, "Agents", BLUE, 16, "600"),
    t(132, 104, "Running", MUTED, 16),
    # active Library pill
    f'<rect x="232" y="88" width="92" height="26" rx="5" fill="{BLUE_FILL}"/>',
    t(278, 106, "Library", "#FFFFFF", 15, "600", "middle"),
    # body
    t(56, 156, "Create new agent", MUTED, 15),
    t(56, 206, "Project agent", INK, 15, "600"),
    t(180, 206, "(~/getting-started-with-claude-agents/.claude/agents)", MUTED, 14),
    # the configured agent row — highlighted to draw the eye
    f'<rect x="44" y="226" width="320" height="30" rx="6" fill="#F3E9CF"/>',
    t(56, 247, "stock-analyzer", INK, 16, "600"),
    t(196, 247, "·", MUTED, 16),
    t(214, 247, "inherit", MUTED, 16),
    "</svg>",
]

out = ASSETS / "claude-agents.svg"
out.write_text("\n".join(parts))
print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")

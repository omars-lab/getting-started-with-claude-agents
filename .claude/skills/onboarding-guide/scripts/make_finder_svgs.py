#!/usr/bin/env python3
"""Render clean Finder-style mockups as SVG (crisp, tiny, embeddable).

Two mockups:
  finder-hidden.svg   — the folder as first seen, .claude NOT visible
  finder-shown.svg    — after Cmd+Shift+. reveals .claude and other dotfiles

SVG so it stays sharp at any zoom and embeds as a data URI with no binary bloat.
Run via:  ./.venv/bin/python3 scripts/make_finder_svgs.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)

W = 720
ROW_H = 30
TOP = 96  # below toolbar + column header

# colors
WIN_BG = "#FFFFFF"
TOOLBAR = "#ECECEC"
SIDEBAR = "#F5F5F7"
TEXT = "#1D1D1F"
DIM = "#8A8A8E"
SEL = "#E8DACb"  # warm selection
ACCENT = "#D97757"
HIDDEN_FILL = "#B9B7B2"  # dimmed dotfiles

FOLDER = "#7FB2E8"
FOLDER_DARK = "#5B95D6"


def folder_icon(x, y, dim=False):
    f = "#C9C7C2" if dim else FOLDER
    fd = "#A9A7A2" if dim else FOLDER_DARK
    return (
        f'<path d="M{x} {y+4} h7 l3 3 h11 a2 2 0 0 1 2 2 v11 a2 2 0 0 1 -2 2 '
        f'h-21 a2 2 0 0 1 -2 -2 v-14 a2 2 0 0 1 2 -2 z" fill="{f}" stroke="{fd}"/>'
    )


def file_icon(x, y, dim=False):
    f = "#E9E9EA" if not dim else "#DEDCD7"
    s = "#C7C7CC" if not dim else "#BDBBB6"
    return (
        f'<path d="M{x+2} {y} h11 l5 5 v15 a2 2 0 0 1 -2 2 h-14 a2 2 0 0 1 -2 -2 '
        f'v-18 a2 2 0 0 1 2 -2 z" fill="{f}" stroke="{s}"/>'
        f'<path d="M{x+13} {y} v5 h5" fill="none" stroke="{s}"/>'
    )


def cmd_icon(x, y):
    # a little terminal-ish badge for .command
    return (
        f'<rect x="{x}" y="{y}" width="22" height="22" rx="4" fill="#2B2A28"/>'
        f'<text x="{x+5}" y="{y+15}" font-family="SF Mono, Menlo, monospace" '
        f'font-size="11" fill="#7CA76E">&gt;_</text>'
    )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row(i, name, kind, hidden=False, note=None, selected=False):
    y = TOP + i * ROW_H
    parts = []
    if selected:
        parts.append(f'<rect x="208" y="{y}" width="{W-216}" height="{ROW_H}" rx="6" fill="{SEL}"/>')
    if i % 2 == 1 and not selected:
        parts.append(f'<rect x="208" y="{y}" width="{W-216}" height="{ROW_H}" fill="#FAFAFA"/>')
    ix, iy = 224, y + 4
    if kind == "folder":
        parts.append(folder_icon(ix, iy, dim=hidden))
    elif kind == "command":
        parts.append(cmd_icon(ix, iy))
    else:
        parts.append(file_icon(ix, iy, dim=hidden))
    color = HIDDEN_FILL if hidden else TEXT
    weight = "600" if name.startswith(".claude") else "400"
    parts.append(
        f'<text x="258" y="{y+19}" font-family="-apple-system, Helvetica, sans-serif" '
        f'font-size="13" font-weight="{weight}" fill="{color}">{esc(name)}</text>'
    )
    if note:
        parts.append(
            f'<text x="{W-24}" y="{y+19}" text-anchor="end" '
            f'font-family="SF Mono, Menlo, monospace" font-size="11" fill="{ACCENT}">{esc(note)}</text>'
        )
    return "".join(parts)


def window(rows, title, badge=None, crumbs=None):
    """title: leaf name (shown when at the top folder).
    crumbs: optional list of path segments relative to (and including) the top
    folder, e.g. ["getting-started-with-claude-agents", ".claude", "skills"].
    When given, the title bar renders a breadcrumb with the last crumb emphasized."""
    n = len(rows)
    height = TOP + n * ROW_H + 18
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
        f'font-family="-apple-system, Helvetica, sans-serif">',
        f'<rect x="0" y="0" width="{W}" height="{height}" rx="12" fill="{WIN_BG}" '
        f'stroke="#D4D2CC"/>',
        # toolbar
        f'<path d="M0 12 a12 12 0 0 1 12 -12 h{W-24} a12 12 0 0 1 12 12 v40 h-{W} z" fill="{TOOLBAR}"/>',
    ]
    for j, col in enumerate(["#ED6A5E", "#F5BF4F", "#62C554"]):
        cx = 22 + j * 20
        parts.append(f'<circle cx="{cx}" cy="20" r="6" fill="{col}"/>')
    if crumbs and len(crumbs) > 1:
        # breadcrumb: dim ancestors joined by ›, current (last) crumb emphasized
        spans = []
        for i, c in enumerate(crumbs):
            last = i == len(crumbs) - 1
            fill = TEXT if last else DIM
            wt = "600" if last else "500"
            if i > 0:
                spans.append(f'<tspan fill="{DIM}" font-weight="400"> › </tspan>')
            spans.append(f'<tspan fill="{fill}" font-weight="{wt}">{esc(c)}</tspan>')
        parts.append(
            f'<text x="{W//2}" y="25" text-anchor="middle" font-size="13">'
            + "".join(spans) + '</text>'
        )
    else:
        parts.append(
            f'<text x="{W//2}" y="25" text-anchor="middle" font-size="13" '
            f'font-weight="600" fill="{TEXT}">{esc(title)}</text>'
        )
    # sidebar
    parts.append(f'<rect x="0" y="52" width="200" height="{height-52}" fill="{SIDEBAR}"/>')
    parts.append(f'<rect x="0" y="52" width="200" height="{height-52}" fill="{SIDEBAR}"/>')
    side = ["Favorites", "  AirDrop", "  Desktop", "  Downloads", "  Documents", "Locations", "  Macintosh HD"]
    for k, label in enumerate(side):
        sy = 76 + k * 26
        is_head = not label.startswith("  ")
        col = DIM if is_head else TEXT
        wt = "600" if is_head else "400"
        if "Downloads" in label:
            parts.append(f'<rect x="8" y="{sy-15}" width="184" height="24" rx="6" fill="{SEL}"/>')
        parts.append(f'<text x="20" y="{sy}" font-size="12.5" font-weight="{wt}" fill="{col}">{esc(label.strip()) if is_head else esc(label.strip())}</text>')
    # column header
    parts.append(f'<line x1="208" y1="{TOP-8}" x2="{W-16}" y2="{TOP-8}" stroke="#E2E0DA"/>')
    parts.append(f'<text x="224" y="{TOP-14}" font-size="11" font-weight="600" fill="{DIM}">Name</text>')
    if badge:
        parts.append(
            f'<rect x="{W-200}" y="62" width="184" height="24" rx="12" fill="#FBEEE8"/>'
            f'<text x="{W-108}" y="78" text-anchor="middle" font-size="11" font-weight="600" '
            f'fill="{ACCENT}">{esc(badge)}</text>'
        )
    parts.extend(rows)
    parts.append("</svg>")
    return "\n".join(parts)


FOLDER = "getting-started-with-claude-agents"

# --- hidden view (what they see first) ---
visible = [
    ("agent-inputs", "folder", False, "drop files here", False),
    ("agent-outputs", "folder", False, "results land here", False),
    ("README.md", "file", False, "start here", True),
]
rows_hidden = [row(i, *v) for i, v in enumerate(visible)]
(ASSETS / "finder-hidden.svg").write_text(
    window(rows_hidden, FOLDER)
)

# --- shown view (after Cmd+Shift+.) ---
shown = [
    (".claude", "folder", True, "the agent lives here", True),
    ("agent-inputs", "folder", False, "drop files here", False),
    ("agent-outputs", "folder", False, "results land here", False),
    ("README.md", "file", False, None, False),
]
rows_shown = [row(i, *v) for i, v in enumerate(shown)]
(ASSETS / "finder-shown.svg").write_text(
    window(rows_shown, FOLDER, badge="⌘ ⇧ .  pressed")
)

# --- inside .claude ---
inside = [
    ("agents", "folder", False, "the role", True),
    ("skills", "folder", False, "the recipes", True),
    ("plans", "folder", False, "how it was built", False),
    ("settings.json", "file", False, "permissions", False),
]
rows_inside = [row(i, *v) for i, v in enumerate(inside)]
(ASSETS / "finder-claude.svg").write_text(
    window(rows_inside, ".claude", crumbs=[FOLDER, ".claude"])
)

# --- inside .claude/agents/ (Make it yours: the role file) ---
agents = [
    ("stock-analyzer.md", "file", False, "the role — read this first", True),
]
rows_agents = [row(i, *v) for i, v in enumerate(agents)]
(ASSETS / "finder-agents.svg").write_text(
    window(rows_agents, "agents", crumbs=[FOLDER, ".claude", "agents"])
)

# --- inside .claude/skills/ (Make it yours: copy a SKILL.md) ---
skills = [
    ("ensure-deps", "folder", False, None, False),
    ("growth-study", "folder", False, None, False),
    ("stock-analysis", "folder", False, None, False),
    ("thesis-stress-test", "folder", False, "the most opinionated", False),
    ("ticker-data", "folder", False, None, False),
    ("xlsx-author", "folder", False, "← copy this one", True),
]
rows_skills = [row(i, *v) for i, v in enumerate(skills)]
(ASSETS / "finder-skills.svg").write_text(
    window(rows_skills, "skills", crumbs=[FOLDER, ".claude", "skills"])
)

for f in ["finder-hidden.svg", "finder-shown.svg", "finder-claude.svg",
          "finder-agents.svg", "finder-skills.svg"]:
    p = ASSETS / f
    print(f"wrote {p}  ({p.stat().st_size // 1024} KB)")

#!/usr/bin/env python3
"""Render the macOS Spotlight search panel as an SVG mockup — used in Getting
Started step 1 (⌘ Space → type "terminal" → Return).

Matches the real Spotlight look: rounded translucent panel, magnifier glyph,
the typed query with " — Open", a top result row for Terminal.app.

Run via:  ./.venv/bin/python3 scripts/make_spotlight_svg.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)

W, H = 720, 220
PANEL = "#F3F1EC"
INK = "#1D1D1F"
DIM = "#8A8A8E"
SUBTLE = "#B6B5B2"
SEL = "#E4E0D7"
RULE = "#DCDAD3"
TERM_BG = "#2B2A28"
TERM_FG = "#7CA76E"
SANS = "-apple-system, Helvetica, Arial, sans-serif"
MONO = "SF Mono, Menlo, monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def termicon(x, y, s=34):
    """A little Terminal.app icon: dark rounded square with a green >_."""
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="8" fill="{TERM_BG}"/>'
        f'<text x="{x+7}" y="{y+s-11}" font-family="{MONO}" font-size="15" '
        f'fill="{TERM_FG}" font-weight="700">&gt;_</text>'
    )


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
    # drop shadow + panel
    f'<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="20" fill="#000" opacity="0.06"/>',
    f'<rect x="10" y="10" width="{W-20}" height="{H-28}" rx="20" fill="{PANEL}" stroke="{RULE}"/>',
    # search row: magnifier + query
    f'<circle cx="48" cy="52" r="11" fill="none" stroke="{DIM}" stroke-width="2.5"/>',
    f'<line x1="56" y1="60" x2="64" y2="68" stroke="{DIM}" stroke-width="2.5"/>',
    f'<text x="82" y="62" font-family="{SANS}" font-size="30" fill="{INK}">terminal.app</text>',
    f'<text x="300" y="62" font-family="{SANS}" font-size="22" fill="{SUBTLE}">— Open</text>',
    termicon(W-66, 34),
    # divider
    f'<line x1="28" y1="92" x2="{W-28}" y2="92" stroke="{RULE}"/>',
    # top result row (selected)
    f'<rect x="22" y="104" width="{W-44}" height="46" rx="10" fill="{SEL}"/>',
    termicon(36, 109, s=36),
    f'<text x="84" y="133" font-family="{SANS}" font-size="20" fill="{INK}" font-weight="500">Terminal.app</text>',
    f'<text x="{W-150}" y="132" font-family="{SANS}" font-size="13" fill="{DIM}">Press</text>',
    f'<rect x="{W-104}" y="118" width="56" height="22" rx="5" fill="#fff" stroke="{RULE}"/>',
    f'<text x="{W-76}" y="133" font-family="{MONO}" font-size="12" fill="{INK}" text-anchor="middle">return</text>',
    # hint line below
    f'<text x="36" y="184" font-family="{SANS}" font-size="14" fill="{DIM}">'
    f'⌘ Space opens Spotlight · type “terminal” · Return to launch</text>',
    "</svg>",
]

out = ASSETS / "spotlight.svg"
out.write_text("\n".join(parts))
print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")

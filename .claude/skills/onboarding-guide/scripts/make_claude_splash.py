#!/usr/bin/env python3
"""Render the Claude Code startup splash as an SVG — what you see right after
launching `claude`, while it waits for your first message. Matches the real UI:

  ➜ git claude
     [mascot]  Claude Code v2.x
               Opus 4.8 with high effort · Claude Max
               ~/Downloads/market-researcher
  ─────────────────────────────────────────────
  › ▍
  ─────────────────────────────────────────────
  Opus 4.8 | 📁 market-researcher | ~10% of 200k tokens

Run via:  ./.venv/bin/python3 scripts/make_claude_splash.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)

W, H = 860, 300
CREAM = "#FBF4E4"
INK = "#33312E"
MUTED = "#6B6960"
ORANGE = "#C8742E"
GREEN = "#7CA76E"
BLUE = "#5B7FB0"
RULE = "#E3DCC9"
CURSOR = "#6B6960"
TERRA = "#C16A4A"   # mascot body
MONO = "SF Mono, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, fill=INK, size=15, weight="400"):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def mascot(ox, oy, px=9):
    """A tiny blocky Claude mascot built from squares."""
    # rows of the sprite; 1 = body pixel
    grid = [
        "011110",
        "111111",
        "1101011",  # eyes row (handled separately)
    ]
    cells = []
    # body block
    for (gx, gy, gw, gh) in [(1, 0, 4, 1), (0, 1, 6, 2)]:
        cells.append(f'<rect x="{ox+gx*px}" y="{oy+gy*px}" width="{gw*px}" '
                     f'height="{gh*px}" fill="{TERRA}"/>')
    # legs
    for lx in (0, 2, 4):
        cells.append(f'<rect x="{ox+lx*px}" y="{oy+3*px}" width="{px}" height="{px}" fill="{TERRA}"/>')
    cells.append(f'<rect x="{ox+5*px}" y="{oy+3*px}" width="{px}" height="{px}" fill="{TERRA}"/>')
    # eyes (cream knockouts)
    cells.append(f'<rect x="{ox+1*px}" y="{oy+1*px}" width="{px}" height="{px}" fill="{CREAM}"/>')
    cells.append(f'<rect x="{ox+4*px}" y="{oy+1*px}" width="{px}" height="{px}" fill="{CREAM}"/>')
    return "".join(cells)


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="10" fill="{CREAM}"/>',
    # command line
    t(24, 36, "➜", GREEN, 15),
    t(46, 36, "market-researcher", BLUE, 15),
    t(232, 36, "claude", INK, 15),
    # mascot
    mascot(28, 54),
    # splash text block
    t(118, 70, "Claude Code", INK, 15, "700"),
    t(232, 70, "v2.1.183", MUTED, 15),
    t(118, 94, "Opus 4.8 with high effort · Claude Max", MUTED, 15),
    t(118, 118, "~/Downloads/market-researcher", MUTED, 15),
    # separator + input box
    f'<line x1="20" y1="176" x2="{W-20}" y2="176" stroke="{RULE}"/>',
    t(24, 210, "›", MUTED, 16),
    f'<rect x="42" y="196" width="11" height="20" fill="{CURSOR}"/>',
    f'<line x1="20" y1="234" x2="{W-20}" y2="234" stroke="{RULE}"/>',
    # status line
    t(24, 260, "Opus 4.8", BLUE, 14),
    t(108, 260, "|", MUTED, 14),
    # folder glyph
    f'<rect x="124" y="250" width="17" height="11" fill="#D6B25C"/>',
    f'<rect x="124" y="247" width="8" height="4" fill="#D6B25C"/>',
    t(148, 260, "market-researcher", MUTED, 14),
    t(322, 260, "|", MUTED, 14),
    t(340, 260, "▓░░░░░░░░ ~10% of 200k tokens", MUTED, 14),
    # auto mode hint
    t(24, 286, "▶▶ auto mode on", ORANGE, 13),
    t(186, 286, "(shift+tab to cycle)  ·  ← for agents", MUTED, 13),
    "</svg>",
]

out = ASSETS / "claude-splash.svg"
out.write_text("\n".join(parts))
print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")

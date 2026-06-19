#!/usr/bin/env python3
"""Assemble the self-contained start-here.html from the template + assets.

Reads templates/start-here.html.tmpl, inlines every asset in assets/ as a
base64 data URI (so the file opens offline with no external dependencies),
and writes start-here.html at the repo root.

Run via:  ./.venv/bin/python3 scripts/build_html.py
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
ASSETS = SKILL / "assets"
TEMPLATE = SKILL / "templates" / "start-here.html.tmpl"
# repo root = .../market-researcher (skill is .claude/skills/onboarding-guide)
REPO = SKILL.parent.parent.parent
OUT = REPO / "start-here.html"

EMBEDS = {
    "__TERMINAL_GIF__": ("terminal.gif", "image/gif"),
    "__FINDER_HIDDEN__": ("finder-hidden.svg", "image/svg+xml"),
    "__FINDER_SHOWN__": ("finder-shown.svg", "image/svg+xml"),
    "__FINDER_CLAUDE__": ("finder-claude.svg", "image/svg+xml"),
    "__FINDER_LAUNCH__": ("finder-launch.svg", "image/svg+xml"),
    "__FINDER_AGENTS__": ("finder-agents.svg", "image/svg+xml"),
    "__FINDER_SKILLS__": ("finder-skills.svg", "image/svg+xml"),
    "__CLAUDE_AGENTS__": ("claude-agents.svg", "image/svg+xml"),
    "__CLAUDE_SPLASH__": ("claude-splash.svg", "image/svg+xml"),
}


def data_uri(filename, mime):
    raw = (ASSETS / filename).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def main():
    html = TEMPLATE.read_text()
    for token, (fn, mime) in EMBEDS.items():
        html = html.replace(token, data_uri(fn, mime))
    missing = [t for t in EMBEDS if t in html]
    if missing:
        raise SystemExit(f"unreplaced tokens: {missing}")
    OUT.write_text(html)
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB, fully self-contained)")
    # Also publish as index.html so GitHub Pages serves the guide at the site root.
    INDEX = REPO / "index.html"
    INDEX.write_text(html)
    print(f"wrote {INDEX}  (GitHub Pages entry point)")


if __name__ == "__main__":
    main()

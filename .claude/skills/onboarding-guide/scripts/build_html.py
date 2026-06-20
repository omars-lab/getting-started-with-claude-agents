#!/usr/bin/env python3
"""Assemble the self-contained onboarding guide from the React template + assets.

Reads templates/start-here.react.tmpl (a single-file React + htm app), inlines
the vendored React/ReactDOM/htm runtime and every image asset as a base64 data
URI, and writes index.html at the repo root — the GitHub Pages entry point.
The result is fully self-contained: no CDN, no build step, opens offline.
The guide is web-only; it is not shipped inside the downloadable example.

Run via:  ./.venv/bin/python3 scripts/build_html.py
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
ASSETS = SKILL / "assets"
VENDOR = SKILL / "vendor"
TEMPLATE = SKILL / "templates" / "start-here.react.tmpl"
# repo root (skill is .claude/skills/onboarding-guide)
REPO = SKILL.parent.parent.parent
OUT = REPO / "index.html"

# Image tokens → (filename, mime), inlined as data URIs.
EMBEDS = {
    "__TERMINAL_GIF__": ("terminal.gif", "image/gif"),
    "__FINDER_HIDDEN__": ("finder-hidden.svg", "image/svg+xml"),
    "__FINDER_SHOWN__": ("finder-shown.svg", "image/svg+xml"),
    "__FINDER_CLAUDE__": ("finder-claude.svg", "image/svg+xml"),
    "__FINDER_AGENTS__": ("finder-agents.svg", "image/svg+xml"),
    "__FINDER_SKILLS__": ("finder-skills.svg", "image/svg+xml"),
    "__CLAUDE_AGENTS__": ("claude-agents.svg", "image/svg+xml"),
    "__CLAUDE_SPLASH__": ("claude-splash.svg", "image/svg+xml"),
    "__SPOTLIGHT__": ("spotlight.svg", "image/svg+xml"),
}

# Vendor JS tokens → filename, inlined verbatim inside <script> tags.
VENDORS = {
    "__REACT_JS__": "react.production.min.js",
    "__REACTDOM_JS__": "react-dom.production.min.js",
    "__HTM_JS__": "htm.umd.js",
}


def data_uri(filename, mime):
    raw = (ASSETS / filename).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def main():
    html = TEMPLATE.read_text()

    # Inline vendored runtime. Guard against a literal </script> in the JS
    # prematurely closing the inline tag (none expected in minified UMD, but
    # escape defensively).
    for token, fn in VENDORS.items():
        js = (VENDOR / fn).read_text()
        js = js.replace("</script>", "<\\/script>")
        html = html.replace(token, js)

    # Inline image assets as data URIs.
    for token, (fn, mime) in EMBEDS.items():
        html = html.replace(token, data_uri(fn, mime))

    leftover = [t for t in {**EMBEDS, **VENDORS} if t in html]
    if leftover:
        raise SystemExit(f"unreplaced tokens: {leftover}")
    OUT.write_text(html)
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB, GitHub Pages entry point)")


if __name__ == "__main__":
    main()

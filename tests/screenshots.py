#!/usr/bin/env python3
"""Visual check: screenshot the built guide at desktop and mobile widths.

Loads ./start-here.html in headless Chromium and writes full-page PNGs to
tests/screenshots/. Use to eyeball responsive layout after editing the guide.

Setup (one-time): `make setup`
  (installs requirements-dev.txt + Chromium into the project venv)

Run:
    ./.venv/bin/python3 tests/screenshots.py
    # or: make shots
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
GUIDE = REPO / "index.html"
OUT = pathlib.Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(exist_ok=True)

VIEWPORTS = [
    ("desktop", 1280, 900),
    ("mobile", 390, 844),   # iPhone-ish portrait
]


def main():
    if not GUIDE.exists():
        sys.exit(f"missing {GUIDE} — run `make build` first")
    url = GUIDE.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, w, h in VIEWPORTS:
            page = browser.new_page(viewport={"width": w, "height": h},
                                    device_scale_factor=2)
            page.goto(url, wait_until="networkidle")
            shot = OUT / f"{name}.png"
            page.screenshot(path=str(shot), full_page=True)
            print(f"wrote {shot}  ({name} {w}x{h})")
            page.close()
        browser.close()


if __name__ == "__main__":
    main()

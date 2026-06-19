# Makefile for getting-started-with-claude-agents
#
#   make build    → regenerate start-here.html + index.html and all assets
#   make publish  → build, commit, and push (updates the live GitHub Pages site)
#   make zip      → timestamped zip of this folder for sharing (omits repo tooling)
#   make help     → list targets

# STAMP resolved when `make` runs; archives go to the Desktop.
NAME  := $(notdir $(CURDIR))
STAMP := $(shell date +%Y%m%d-%H%M%S)
DEST  := $(HOME)/Desktop
ZIP   := $(DEST)/$(NAME)-$(STAMP).zip
PY    := ./.venv/bin/python3
SKILL := .claude/skills/onboarding-guide/scripts

# Release: a fixed asset name gives the guide a stable download URL
# (releases/latest/download/$(REL_ASSET)).
REL_TAG   := latest
REL_ASSET := $(NAME).zip
REPO_SLUG := omars-lab/$(NAME)

DIST := dist/$(NAME)

.PHONY: help setup build dist publish zip release ship shots clean _push _upload

help:
	@echo "Targets:"
	@echo "  make setup    Install dev tooling (Pillow, Playwright + Chromium) into the venv"
	@echo "  make build    Regenerate the guide (start-here.html + index.html) and assets"
	@echo "  make dist     Stage the downloadable example in dist/ (claude/ → .claude/)"
	@echo "  make publish  Build, commit, and push — updates the live GitHub Pages site"
	@echo "  make release  Build a fresh zip and upload it to the GitHub 'latest' release"
	@echo "  make ship     Build once, then release AND publish (one command, full deploy)"
	@echo "  make shots    Screenshot the guide at desktop + mobile widths (tests/screenshots/)"
	@echo "  make zip      Create ~/Desktop/$(NAME)-<timestamp>.zip for sharing"
	@echo "  make clean    Remove dist/ and local zips"

# Visual check: full-page screenshots at desktop + mobile widths.
# Needs playwright in the venv (see tests/screenshots.py for setup).
shots: build
	@$(PY) tests/screenshots.py

# Install developer tooling into the venv (guide build + screenshot tests).
# The agent's own runtime deps install via Setup.command / ensure-deps.
setup:
	@$(PY) -m pip install -q -r requirements-dev.txt
	@$(PY) -m playwright install chromium
	@echo "Dev tooling ready (Pillow, Playwright + Chromium)."

# Regenerate every asset, then assemble the guide. Mirrors the onboarding-guide skill.
build:
	@$(PY) $(SKILL)/make_terminal_gif.py
	@$(PY) $(SKILL)/make_finder_svgs.py
	@$(PY) $(SKILL)/make_agents_svg.py
	@$(PY) $(SKILL)/make_claude_splash.py
	@$(PY) $(SKILL)/build_html.py

# Commit any changes and push. Pushing to main triggers the GitHub Pages
# rebuild automatically (the gitleaks pre-commit hook runs first). No-ops
# cleanly if there's nothing to commit.
_push:
	@git add -A
	@git diff --cached --quiet && echo "Nothing to publish — already up to date." || \
		git commit -m "Update onboarding guide ($(STAMP))"
	@git push origin main
	@echo "Pushed. GitHub Pages will rebuild from main shortly."

# Build, then commit and push (updates the live GitHub Pages site).
publish: build _push

# Stage the exact folder a user downloads into dist/$(NAME):
#   - claude/ (the maintained teaching example) is copied in AS .claude/
#   - the dev .claude/ (onboarding-guide tooling) is NOT included
#   - repo tooling (Makefile, CLAUDE.md, tests/, requirements-dev.txt, …) is omitted
#   - agent-outputs/ ships empty (placeholders only); agent-inputs/ keeps watchlist.md
# This is the single source of truth for both `zip` and `release`.
dist:
	@rm -rf dist && mkdir -p "$(DIST)"
	@cp -R claude "$(DIST)/.claude"
	@cp -R agent-inputs "$(DIST)/agent-inputs"
	@mkdir -p "$(DIST)/agent-outputs"
	@cp agent-outputs/.gitkeep agent-outputs/README.txt "$(DIST)/agent-outputs/" 2>/dev/null || true
	@cp README.md start-here.html "$(DIST)/"
	@cp *.command "$(DIST)/"
	@find "$(DIST)" -name '.DS_Store' -delete
	@echo "Staged downloadable example in $(DIST)/"

# Timestamped zip onto the Desktop, built from the staged dist/.
zip: dist
	@cd dist && zip -r -q "$(ZIP)" "$(NAME)"
	@echo "Created $(ZIP)"

# Build a fixed-name zip from dist/ and upload to the GitHub 'latest' release,
# giving the guide a stable URL: releases/latest/download/$(REL_ASSET).
# Creates the release on first run; replaces the asset on subsequent runs.
_upload: dist
	@TMP="$$(mktemp -d)"; OUT="$$TMP/$(REL_ASSET)"; \
	( cd dist && zip -r -q "$$OUT" "$(NAME)" ) && \
	( gh release view $(REL_TAG) -R $(REPO_SLUG) >/dev/null 2>&1 || \
	  gh release create $(REL_TAG) -R $(REPO_SLUG) -t "Latest" \
	    -n "Download the latest copy of this folder." ) && \
	gh release upload $(REL_TAG) "$$OUT" -R $(REPO_SLUG) --clobber && \
	echo "Uploaded $(REL_ASSET) → https://github.com/$(REPO_SLUG)/releases/latest/download/$(REL_ASSET)"; \
	rm -rf "$$TMP"

release: build _upload

# Full deploy in one command: build once, upload the release zip, then commit
# and push (which rebuilds GitHub Pages). Order matters — upload the downloadable
# zip before publishing the site that links to it.
ship: build _upload _push

clean:
	@rm -rf dist
	@echo "Removed dist/."

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

.PHONY: help setup build publish zip release ship shots _push _upload

help:
	@echo "Targets:"
	@echo "  make setup    Install dev tooling (Pillow, Playwright + Chromium) into the venv"
	@echo "  make build    Regenerate the guide (start-here.html + index.html) and assets"
	@echo "  make publish  Build, commit, and push — updates the live GitHub Pages site"
	@echo "  make release  Build a fresh zip and upload it to the GitHub 'latest' release"
	@echo "  make ship     Build once, then release AND publish (one command, full deploy)"
	@echo "  make shots    Screenshot the guide at desktop + mobile widths (tests/screenshots/)"
	@echo "  make zip      Create ~/Desktop/$(NAME)-<timestamp>.zip for sharing"

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

# Zip the current directory onto the Desktop, omitting repo tooling.
# agent-outputs/ ships present-but-empty: all generated data is excluded, only
# its placeholders (.gitkeep, README.txt) are added back. agent-inputs/ keeps
# its example watchlist.md. Excludes match the paths zip sees (leading ./).
zip:
	@cd "$(CURDIR)" && zip -r -q "$(ZIP)" . \
		-x '*/.venv/*' '.venv/*' \
		-x '*/.git/*' '.git/*' \
		-x 'Makefile' \
		-x '*.zip' \
		-x '.gitignore' \
		-x '.pre-commit-config.yaml' \
		-x 'CLAUDE.md' \
		-x 'index.html' \
		-x 'requirements-dev.txt' \
		-x 'tests/*' \
		-x 'agent-outputs/*' \
		-x '.DS_Store' '*/.DS_Store' \
		-x '__pycache__/*' '*/__pycache__/*'
	@cd "$(CURDIR)" && zip -q "$(ZIP)" agent-outputs/.gitkeep agent-outputs/README.txt
	@echo "Created $(ZIP)"

# Build a fixed-name zip and upload it to the GitHub 'latest' release, so the
# guide can link to a stable URL: releases/latest/download/$(REL_ASSET).
# Creates the release on first run; replaces the asset on subsequent runs.
_upload:
	@TMP="$$(mktemp -d)"; OUT="$$TMP/$(REL_ASSET)"; \
	cd "$(CURDIR)" && zip -r -q "$$OUT" . \
		-x '*/.venv/*' '.venv/*' -x '*/.git/*' '.git/*' \
		-x 'Makefile' -x '*.zip' -x '.gitignore' \
		-x '.pre-commit-config.yaml' -x 'CLAUDE.md' -x 'index.html' \
		-x 'requirements-dev.txt' -x 'tests/*' \
		-x 'agent-outputs/*' -x '.DS_Store' '*/.DS_Store' \
		-x '__pycache__/*' '*/__pycache__/*' && \
	zip -q "$$OUT" agent-outputs/.gitkeep agent-outputs/README.txt && \
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

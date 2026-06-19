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

.PHONY: help build publish zip

help:
	@echo "Targets:"
	@echo "  make build    Regenerate the guide (start-here.html + index.html) and assets"
	@echo "  make publish  Build, commit, and push — updates the live GitHub Pages site"
	@echo "  make zip      Create ~/Desktop/$(NAME)-<timestamp>.zip for sharing"

# Regenerate every asset, then assemble the guide. Mirrors the onboarding-guide skill.
build:
	@$(PY) $(SKILL)/make_terminal_gif.py
	@$(PY) $(SKILL)/make_finder_svgs.py
	@$(PY) $(SKILL)/make_agents_svg.py
	@$(PY) $(SKILL)/make_claude_splash.py
	@$(PY) $(SKILL)/build_html.py

# Build, then commit any changes and push. Pushing to main triggers the
# GitHub Pages rebuild automatically (the gitleaks pre-commit hook runs first).
# No-ops cleanly if there's nothing to commit.
publish: build
	@git add -A
	@git diff --cached --quiet && echo "Nothing to publish — already up to date." || \
		git commit -m "Update onboarding guide ($(STAMP))"
	@git push origin main
	@echo "Pushed. GitHub Pages will rebuild from main shortly."

# Zip the current directory onto the Desktop, omitting repo tooling.
# Excludes are matched against the paths zip sees (leading ./).
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
		-x '.DS_Store' '*/.DS_Store' \
		-x '__pycache__/*' '*/__pycache__/*'
	@echo "Created $(ZIP)"

# Makefile for getting-started-with-claude-agents
#
#   make zip   → build a timestamped zip of this folder for sharing,
#                omitting repo tooling (.venv, .git, Makefile, .gitignore,
#                .pre-commit-config.yaml, index.html) and macOS cruft.
#                Keeps .claude (the agent + skills) and start-here.html.

# Folder name → archive base name (e.g. getting-started-with-claude-agents)
NAME := $(notdir $(CURDIR))
# Timestamp resolved when `make` runs, not when this file is written.
STAMP := $(shell date +%Y%m%d-%H%M%S)
# Archives are written to the Desktop.
DEST := $(HOME)/Desktop
ZIP  := $(DEST)/$(NAME)-$(STAMP).zip

.PHONY: zip help

help:
	@echo "Targets:"
	@echo "  make zip   Create ~/Desktop/$(NAME)-<timestamp>.zip (omits .venv, .git, Makefile, .DS_Store)"

# Zip the current directory onto the Desktop. Excludes are matched against
# the paths zip sees (leading ./).
zip:
	@cd "$(CURDIR)" && zip -r -q "$(ZIP)" . \
		-x '*/.venv/*' '.venv/*' \
		-x '*/.git/*' '.git/*' \
		-x 'Makefile' \
		-x '*.zip' \
		-x '.gitignore' \
		-x '.pre-commit-config.yaml' \
		-x 'index.html' \
		-x '.DS_Store' '*/.DS_Store' \
		-x '__pycache__/*' '*/__pycache__/*'
	@echo "Created $(ZIP)"

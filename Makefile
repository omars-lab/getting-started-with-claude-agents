# Makefile for getting-started-with-claude-agents
#
#   make build    → regenerate the web guide (index.html) and all assets
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

.PHONY: help setup build validate-config deploy dist zip release shots clean _upload

help:
	@echo "Targets:"
	@echo "  make setup    Install dev tooling (Pillow, Playwright + Chromium) into the venv"
	@echo "  make build    Build the web guide (Vite+React app in web/) → dist-site/ (local preview)"
	@echo "  make validate-config  Static-check the Actions workflows (actionlint) — config dry-run"
	@echo "  make deploy   Deploy the guide to GitHub Pages by triggering the Actions workflow"
	@echo "  make dist     Stage the downloadable example in dist/ (clean copy of example/)"
	@echo "  make release  Build a fresh zip and upload it to the GitHub 'latest' release"
	@echo "  make shots    Screenshot the guide at desktop + mobile widths (tests/screenshots/)"
	@echo "  make zip      Create ~/Desktop/$(NAME)-<timestamp>.zip for sharing"
	@echo "  make clean    Remove dist/ and local zips"

# Visual check: full-page screenshots at desktop + mobile widths.
# Needs playwright in the venv (see tests/screenshots.py for setup).
shots: build
	@$(PY) tests/screenshots.py

# Install developer tooling into the venv (guide build + screenshot tests).
# The agent's own runtime deps install per the example README (ensure-deps verifies).
setup:
	@$(PY) -m pip install -q -r requirements-dev.txt
	@$(PY) -m playwright install chromium
	@echo "Dev tooling ready (Pillow, Playwright + Chromium)."

# Build the web guide. It is a Vite + React app (source under web/) that consumes the
# @omars-lab/blog-ui component package from GitHub Packages, so installing needs a GitHub
# token with read:packages in the env:
#     export GITHUB_TOKEN=$(gh auth token)   # or a PAT with read:packages
# Builds to dist-site/ for LOCAL PREVIEW only (yarn preview). The published site is built
# in CI by the deploy-pages workflow — nothing is copied to the repo root anymore. The
# downloadable example (`make dist`) is unaffected — it packages example/, never the guide.
build:
	@command -v node >/dev/null || { echo "node is required to build the guide (https://nodejs.org)"; exit 1; }
	@[ -n "$$GITHUB_TOKEN" ] || { echo "GITHUB_TOKEN not set — needed to install @omars-lab/blog-ui from GitHub Packages."; echo "  run: export GITHUB_TOKEN=\$$(gh auth token)"; exit 1; }
	@yarn install --frozen-lockfile
	@yarn build
	@echo "Guide built → dist-site/ (local preview: yarn preview). Deploy with: make deploy"

# Statically validate the workflow config BEFORE it runs in CI (a config dry-run).
# actionlint deeply type-checks the Actions schema, action inputs, and ${{ }} expressions —
# far more than a YAML parse. Auto-installs via brew or the official script if missing; falls
# back to a plain YAML parse so the target never hard-fails on a missing tool.
validate-config:
	@if command -v actionlint >/dev/null 2>&1; then \
		echo "actionlint: linting .github/workflows/…"; \
		actionlint; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "Installing actionlint via brew…"; brew install actionlint && actionlint; \
	else \
		echo "actionlint not found and no brew; falling back to YAML parse."; \
		for f in .github/workflows/*.yml; do \
			python3 -c "import sys,yaml; yaml.safe_load(open('$$f')); print('  ok:', '$$f')" || exit 1; \
		done; \
		echo "Install actionlint for full validation: brew install actionlint"; \
	fi

# Deploy the guide to GitHub Pages by triggering the Actions workflow (deploy-pages.yml),
# which builds from web/src in CI and publishes the artifact. This is the manual kick of the
# same pipeline that runs automatically on push to main. Pages source is "GitHub Actions",
# so there is no commit-to-branch step — CI is the single source of truth for the live site.
# Validates the workflow config first (fail-closed: don't trigger a run on a broken config).
deploy: validate-config
	@command -v gh >/dev/null || { echo "gh CLI required: https://cli.github.com"; exit 1; }
	@echo "Triggering the Pages deploy workflow on main…"
	@gh workflow run deploy-pages.yml --ref main
	@sleep 4
	@gh run list --workflow=deploy-pages.yml --limit 1 || true
	@echo "Watch it: gh run watch \$$(gh run list --workflow=deploy-pages.yml --limit 1 --json databaseId -q '.[0].databaseId')"

# Stage the exact folder a user downloads into dist/$(NAME).
# The example/ directory IS the shippable folder (real dotted .claude/), so this
# is just a clean copy with generated agent-outputs/ data stripped to placeholders.
# The web-only guide (index.html) and all repo tooling stay out by construction.
dist:
	@rm -rf dist && mkdir -p dist
	@cp -R example "$(DIST)"
	@rm -f "$(DIST)/agent-outputs/"* 2>/dev/null || true
	@printf 'The Stock Analyzer writes everything it produces here — reports,\nworkbooks, and the per-ticker data cache. Empty until you run the agent.\n' > "$(DIST)/agent-outputs/README.txt"
	@touch "$(DIST)/agent-outputs/.gitkeep"
	@rm -rf "$(DIST)/out"
	@find "$(DIST)" -name '.DS_Store' -delete
	@find "$(DIST)" -name '__pycache__' -type d -prune -exec rm -rf {} +
	@find "$(DIST)" -name '*.pyc' -delete
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

# Upload the downloadable-example zip to the GitHub 'latest' release. Independent of the
# web guide (which deploys via `make deploy` / the Actions workflow).
release: _upload

clean:
	@rm -rf dist
	@echo "Removed dist/."

#!/usr/bin/env python3
"""
Verify the project environment is ready for the stock-analyzer agent.

Usage:
    ./.venv/bin/python3 .claude/skills/ensure-deps/scripts/check.py

Output (stdout, JSON):
    {
      "verdict": "ready" | "ready_with_warnings" | "not_ready",
      "checks": [
        {"name": "...", "status": "ok"|"missing"|"warn",
         "detail": "...", "required": true|false,
         "fix_command": "..." | null}
      ]
    }

Exit codes:
    0 = ready
    1 = ready with warnings (optional checks failed)
    2 = not ready (required checks failed)
"""

import json
import sys
import tempfile
from importlib import metadata
from pathlib import Path


REQUIRED_PACKAGES = [
    ("openpyxl", "openpyxl"),
    ("formulas", "formulas"),
    ("yfinance", "yfinance"),
    ("pandas", "pandas"),
    ("jinja2", "Jinja2"),
    ("requests", "requests"),
]

OPTIONAL_PACKAGES = [
    ("edgar", "edgartools"),
    ("plotly", "plotly"),
]


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude").is_dir():
            return parent
    return Path.cwd()


def check_venv(root: Path) -> dict:
    venv_python = root / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        return {
            "name": "Python venv",
            "status": "missing",
            "detail": f"{venv_python.relative_to(root)} not found",
            "required": True,
            "fix_command": "python3 -m venv .venv",
        }
    # If we got here, we're running under the venv (per the docstring usage).
    py = sys.version.split()[0]
    return {
        "name": "Python venv",
        "status": "ok",
        "detail": f".venv/bin/python3 (Python {py})",
        "required": True,
        "fix_command": None,
    }


def check_package(import_name: str, dist_name: str, required: bool) -> dict:
    label = f"{import_name} ({dist_name})" if import_name != dist_name else import_name
    try:
        __import__(import_name)
    except ImportError:
        return {
            "name": label,
            "status": "missing",
            "detail": "not installed",
            "required": required,
            "fix_command": "./.venv/bin/pip install -r .claude/skills/ensure-deps/requirements.txt",
        }
    try:
        version = metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        version = "unknown"
    return {
        "name": label,
        "status": "ok",
        "detail": version,
        "required": required,
        "fix_command": None,
    }


def check_out_writable(root: Path) -> dict:
    out_dir = root / "out"
    try:
        out_dir.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=out_dir, delete=True) as _:
            pass
        return {
            "name": "./agent-outputs/ writable",
            "status": "ok",
            "detail": "yes",
            "required": True,
            "fix_command": None,
        }
    except (OSError, PermissionError) as e:
        return {
            "name": "./agent-outputs/ writable",
            "status": "missing",
            "detail": str(e),
            "required": True,
            "fix_command": "mkdir -p ./agent-outputs && chmod u+w ./agent-outputs",
        }


def check_agent_file(root: Path) -> dict:
    agent_file = root / ".claude" / "agents" / "stock-analyzer.md"
    if agent_file.exists():
        return {
            "name": "stock-analyzer agent",
            "status": "ok",
            "detail": str(agent_file.relative_to(root)),
            "required": True,
            "fix_command": None,
        }
    return {
        "name": "stock-analyzer agent",
        "status": "missing",
        "detail": ".claude/agents/stock-analyzer.md not found",
        "required": True,
        "fix_command": None,
    }


def check_settings(root: Path) -> dict:
    settings = root / ".claude" / "settings.json"
    if not settings.exists():
        return {
            "name": "settings.json",
            "status": "warn",
            "detail": "missing — agent will prompt for permissions on first run",
            "required": False,
            "fix_command": None,
        }
    try:
        json.loads(settings.read_text())
    except json.JSONDecodeError as e:
        return {
            "name": "settings.json",
            "status": "missing",
            "detail": f"invalid JSON: {e}",
            "required": True,
            "fix_command": None,
        }
    return {
        "name": "settings.json",
        "status": "ok",
        "detail": ".claude/settings.json valid",
        "required": False,
        "fix_command": None,
    }


def main() -> int:
    root = project_root()
    checks: list[dict] = []

    # Venv: special-case — if missing, the rest of the script likely can't run
    # via the venv interpreter anyway. We still report the rest, since the
    # caller may have invoked with system python to do exactly this discovery.
    checks.append(check_venv(root))
    checks.append(check_agent_file(root))
    checks.append(check_settings(root))
    checks.append(check_out_writable(root))

    for import_name, dist_name in REQUIRED_PACKAGES:
        checks.append(check_package(import_name, dist_name, required=True))
    for import_name, dist_name in OPTIONAL_PACKAGES:
        checks.append(check_package(import_name, dist_name, required=False))

    required_failures = [c for c in checks if c["required"] and c["status"] != "ok"]
    optional_failures = [c for c in checks if not c["required"] and c["status"] != "ok"]

    if required_failures:
        verdict = "not_ready"
        exit_code = 2
    elif optional_failures:
        verdict = "ready_with_warnings"
        exit_code = 1
    else:
        verdict = "ready"
        exit_code = 0

    print(json.dumps({"verdict": verdict, "checks": checks}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

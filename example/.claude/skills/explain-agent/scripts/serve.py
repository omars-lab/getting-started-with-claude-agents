#!/usr/bin/env python3
"""
Generate (if stale) and serve the agent diagram on localhost.

Usage:
    ./.venv/bin/python3 .claude/skills/explain-agent/scripts/serve.py

Behavior:
1. Walk .claude/agents/ and .claude/skills/*/SKILL.md to build the event
   list and skill panel data.
2. Write ./agent-outputs/agent-diagram.json (source of truth, regenerable).
3. Render ./agent-outputs/agent-diagram.html from templates/diagram.html.j2.
   Skips render if both files are newer than every source file.
4. Start http.server on port 8765 (or next free port) and open the page.

The HTML is fully self-contained — open the file from anywhere and it
works offline.
"""

import datetime as dt
import http.server
import json
import os
import re
import socket
import socketserver
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path


# Palette mirrors SKILL.md — keep these in sync.
PALETTE = {
    "auto": "#6B6964",
    "memory": "#E8A45C",
    "tools": "#9B7BC4",
    "skill": "#D4A843",
    "project": "#6A9BCC",
    "user": "#558A42",
    "claude": "#D97757",
    "tool_result": "#A09E96",
    "hook": "#B8860B",
    "rule": "#4A9B8E",
    "background": "#FAF7F2",
    "body": "#2B2A28",
}


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude").is_dir():
            return parent
    raise SystemExit("could not locate project root (no .claude/ directory found above this script)")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    fm: dict = {}
    for line in block.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            fm[key] = value.strip("\"'") if value else ""
    return fm, body


def first_paragraph(text: str) -> str:
    for chunk in text.strip().split("\n\n"):
        cleaned = chunk.strip()
        if cleaned and not cleaned.startswith("#"):
            return re.sub(r"\s+", " ", cleaned)
    return ""


def first_two_sentences(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:2]).strip()


def discover_agent(root: Path) -> dict:
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return {"name": "(unknown)", "description": "", "file": ""}
    candidates = sorted(agents_dir.glob("*.md"))
    if not candidates:
        return {"name": "(unknown)", "description": "", "file": ""}
    # Prefer stock-analyzer if present, otherwise first.
    target = next((c for c in candidates if c.stem == "stock-analyzer"), candidates[0])
    text = target.read_text()
    fm, body = parse_frontmatter(text)
    return {
        "name": fm.get("name", target.stem),
        "description": first_paragraph(body),
        "file": str(target.relative_to(root)),
    }


def discover_skills(root: Path) -> list[dict]:
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        if "_archive" in skill_md.parts:
            continue
        text = skill_md.read_text()
        fm, body = parse_frontmatter(text)
        skills.append(
            {
                "name": fm.get("name", skill_md.parent.name),
                "description": first_two_sentences(fm.get("description", "")) or first_two_sentences(first_paragraph(body)),
                "file": str(skill_md.relative_to(root)),
            }
        )
    return skills


def build_events(skills: list[dict]) -> list[dict]:
    """Build canonical event list. Reference real skills when available."""
    skill_names = {s["name"] for s in skills}

    def has(name: str) -> bool:
        return name in skill_names

    events: list[dict] = [
        {"kind": "auto", "label": "Load agent definition", "tokens": 320, "source": ".claude/agents/stock-analyzer.md"},
        {"kind": "auto", "label": "Index project skills", "tokens": 1100, "source": ".claude/skills/*"},
        {"kind": "user", "label": "User prompt: 'what's worth looking at today?'", "tokens": 80},
        {"kind": "claude", "label": "Plan: invoke ticker-discovery", "tokens": 240},
    ]
    if has("ticker-discovery"):
        events += [
            {"kind": "skill", "label": "ticker-discovery — daily sweep", "skill": "ticker-discovery", "tokens": 900},
            {"kind": "tools", "label": "WebSearch + WebFetch (Yahoo, SEC)", "tokens": 1400},
            {"kind": "claude", "label": "Shortlist: 5 names", "tokens": 320},
            {"kind": "user", "label": "User confirms shortlist", "tokens": 40},
        ]
    if has("ticker-data"):
        events += [
            {"kind": "claude", "label": "Fan out: ticker-data per ticker (parallel)", "tokens": 200},
            {"kind": "skill", "label": "ticker-data NVDA", "skill": "ticker-data", "tokens": 720},
            {"kind": "skill", "label": "ticker-data AVGO", "skill": "ticker-data", "tokens": 720},
            {"kind": "skill", "label": "ticker-data MU", "skill": "ticker-data", "tokens": 720},
            {"kind": "tools", "label": "edgartools, yfinance, finnhub MCP", "tokens": 2200},
        ]
    if has("stock-analysis") or has("growth-study"):
        events.append({"kind": "claude", "label": "Fan out: stock-analysis + growth-study", "tokens": 240})
    if has("stock-analysis"):
        events.append({"kind": "skill", "label": "stock-analysis NVDA", "skill": "stock-analysis", "tokens": 1500})
    if has("growth-study"):
        events.append({"kind": "skill", "label": "growth-study NVDA", "skill": "growth-study", "tokens": 1300})
    if has("xlsx-author"):
        events.append({"kind": "skill", "label": "xlsx-author (consumed)", "skill": "xlsx-author", "consumed_by": "growth-study", "tokens": 0})
    events.append({"kind": "tools", "label": "recalc.py — verify formulas", "tokens": 320})
    if has("thesis-stress-test"):
        events.append({"kind": "skill", "label": "thesis-stress-test NVDA", "skill": "thesis-stress-test", "tokens": 1100})
    events += [
        {"kind": "claude", "label": "Assemble HTML report", "tokens": 800},
        {"kind": "user", "label": "User reviews report", "tokens": 30},
    ]
    return events


def build_data(root: Path) -> dict:
    agent = discover_agent(root)
    skills = discover_skills(root)
    events = build_events(skills)
    return {
        "agent": agent["name"],
        "agent_description": agent["description"],
        "agent_file": agent["file"],
        "events": events,
        "skills": skills,
        "palette": PALETTE,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def render_html(data: dict, template_path: Path) -> str:
    """Render the HTML without requiring Jinja at runtime — we do a tiny
    placeholder substitution. The template uses {{DATA_JSON}} as the only
    placeholder; the rest is plain HTML/CSS/JS that consumes that JSON.
    """
    template = template_path.read_text()
    payload = json.dumps(data, indent=2)
    return template.replace("{{DATA_JSON}}", payload)


def is_stale(out_html: Path, out_json: Path, root: Path, template_path: Path) -> bool:
    if not out_html.exists() or not out_json.exists():
        return True
    out_mtime = min(out_html.stat().st_mtime, out_json.stat().st_mtime)
    sources = [template_path, *Path(root, ".claude").rglob("SKILL.md"), *Path(root, ".claude", "agents").glob("*.md")]
    sources = [p for p in sources if p.exists() and "_archive" not in p.parts]
    return any(p.stat().st_mtime > out_mtime for p in sources)


def find_free_port(start: int = 8765, end: int = 8800) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit(f"no free port in range {start}-{end}")


def serve(directory: Path, port: int) -> None:
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(directory), **kwargs)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=False)
    thread.start()
    print(f"\n  serving {directory} at http://localhost:{port}/agent-diagram.html")
    print(f"  stop with: lsof -ti :{port} | xargs kill")
    print(f"  or:        kill {os.getpid()}\n")


def main() -> int:
    root = project_root()
    skill_dir = root / ".claude" / "skills" / "explain-agent"
    template_path = skill_dir / "templates" / "diagram.html.j2"
    out_dir = root / "out"
    out_dir.mkdir(exist_ok=True)
    out_html = out_dir / "agent-diagram.html"
    out_json = out_dir / "agent-diagram.json"

    if not template_path.exists():
        print(f"template missing: {template_path}", file=sys.stderr)
        return 2

    if is_stale(out_html, out_json, root, template_path):
        data = build_data(root)
        out_json.write_text(json.dumps(data, indent=2))
        out_html.write_text(render_html(data, template_path))
        print(f"  generated {out_html.relative_to(root)}")
        print(f"  generated {out_json.relative_to(root)}")
    else:
        print(f"  up to date: {out_html.relative_to(root)}")

    port = find_free_port()
    serve(out_dir, port)

    url = f"http://localhost:{port}/agent-diagram.html"
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.run([opener, url], check=False)
    except FileNotFoundError:
        webbrowser.open(url)

    # Block forever (the http server thread is non-daemon).
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nshutting down")
    return 0


if __name__ == "__main__":
    sys.exit(main())

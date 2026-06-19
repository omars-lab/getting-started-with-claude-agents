#!/usr/bin/env python3
"""Render a synthesized GIF of a *genuine* Claude Code session running the
stock-analyzer agent — matched to how Claude Code actually renders:

  - cream/light UI (not a dark terminal)
  - the user prompt in a grey rounded bar with a › chevron
  - Claude's turn as '● I'll survey the market... Let me launch the
    stock-analyzer agent to do this properly.'  (Claude never says "ready")
  - the subagent block: 'stock-analyzer(Find stocks worth considering today)'
    with indented └ tool calls (Bash / Read / Running… / +1 tool use)
  - an orange '✻ Stewing… (28s · ↓ 636 tokens)' spinner with a '└ Tip:' line
  - the bottom input box and status line 'Opus 4.8 | 📁 <folder> | …'

Reproducible — no live session needed. Output: assets/terminal.gif
Run via the project venv:  ./.venv/bin/python3 scripts/make_terminal_gif.py
"""
import pathlib
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)

# --- palette, matched to real Claude Code screenshots ----------------------
BG = (251, 244, 228)       # #FBF4E4 cream
BAR = (218, 216, 210)      # #DAD8D2 grey prompt bar
INK = (51, 49, 46)         # #33312E primary text / bold
MUTED = (107, 105, 96)     # #6B6960 dim prose, Running…, paths
ORANGE = (200, 116, 46)    # #C8742E spinner, $, /passes
BLUE = (91, 127, 176)      # #5B7FB0 model name, underlined paths
RULE = (227, 220, 201)     # #E3DCC9 hairlines
CURSOR = (107, 105, 96)

W, H = 900, 620
PADX = 26
LINE_H = 26
FS = 16


def load_font(size, bold=False):
    bold_cands = [
        "/System/Library/Fonts/SFNSMono.ttf",  # SF Mono has weights in one file via index; fallback below
        "/System/Library/Fonts/Menlo.ttc",
    ]
    reg_cands = [
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
    ]
    cands = bold_cands if bold else reg_cands
    for c in cands:
        p = pathlib.Path(c)
        if p.exists():
            try:
                if c.endswith(".ttc"):
                    # Menlo.ttc index 0 = Regular, 1 = Bold
                    return ImageFont.truetype(c, size, index=1 if bold else 0)
                return ImageFont.truetype(c, size)
            except OSError:
                continue
    return ImageFont.load_default()


FONT = load_font(FS)
FONT_B = load_font(FS, bold=True)


# Each segment: (text, color, font). A line is a list of segments + indent px.
def seg(text, color=INK, bold=False):
    return (text, color, FONT_B if bold else FONT)


# The transcript, in render order. Built up line by line so the GIF can reveal
# it. 'kind' drives spacing/animation.
#   ('prompt', segments)        -> rendered inside the grey bar (user input)
#   ('line', indent, segments)  -> a normal transcript line
#   ('gap',)                    -> blank line
TRANSCRIPT = [
    ("promptbar", [seg("› ", MUTED), seg("what stocks are worth considering today")]),
    ("gap",),
    ("line", 0, [seg("● ", INK), seg("I'll survey the market for stocks worth a closer look today. Let me", MUTED)]),
    ("line", 0, [seg("  launch the ", MUTED), seg("stock-analyzer", MUTED, bold=True), seg(" agent to do this properly.", MUTED)]),
    ("gap",),
    # subagent block
    ("line", 0, [seg("stock-analyzer", INK, bold=True), seg("(Find stocks worth considering today)", MUTED)]),
    ("line", 0, [seg("  └ ", MUTED), seg("Bash", INK, bold=True), seg("(ls -la .claude/ && find .claude -name \"*.md\" …)", MUTED)]),
    ("line", 0, [seg("    Running…", MUTED)]),
    ("line", 0, [seg("    ", MUTED), seg("Read", INK, bold=True), seg("(.claude/skills/ensure-deps/SKILL.md)", BLUE)]),
    ("line", 0, [seg("    ", MUTED), seg("Bash", INK, bold=True), seg("(./.venv/bin/python3 .claude/skills/ensure-deps/scripts/check.py)", MUTED)]),
    ("line", 0, [seg("    Running…", MUTED)]),
    ("line", 0, [seg("    … +1 tool use (ctrl+o to expand)", MUTED)]),
    ("gap",),
    ("line", 0, [seg("● ", INK), seg("Here's a shortlist worth a closer look today. Approve it before I", MUTED)]),
    ("line", 0, [seg("  spend analysis time going deeper:", MUTED)]),
    ("line", 0, [seg("    NVDA", INK, bold=True), seg("  data-center guidance raised after hours", MUTED)]),
    ("line", 0, [seg("    AVGO", INK, bold=True), seg("  custom-silicon 8-K filed pre-market", MUTED)]),
    ("line", 0, [seg("    LLY", INK, bold=True), seg("   PDUFA decision due this week", MUTED)]),
    ("gap",),
    ("spinner", [seg("✻ ", ORANGE), seg("Stewing… ", ORANGE), seg("(28s · ↓ 636 tokens)", MUTED)]),
    ("line", 0, [seg("  └ Tip: Share Claude Code and earn ", MUTED), seg("$10", ORANGE), seg(" in usage credits · ", MUTED), seg("/passes", ORANGE)]),
]


def base():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_segments(d, x, y, segments):
    for text, color, font in segments:
        d.text((x, y), text, font=font, fill=color)
        x += d.textlength(text, font=font)
    return x


def draw_chrome(d):
    """The persistent bottom input box + status line."""
    # separator above input
    d.line([(PADX, H - 96), (W - PADX, H - 96)], fill=RULE)
    # input box
    d.text((PADX, H - 78), "›", font=FONT, fill=MUTED)
    d.rectangle([PADX + 22, H - 80, PADX + 34, H - 60], fill=CURSOR)
    d.line([(PADX, H - 44), (W - PADX, H - 44)], fill=RULE)
    # status line
    sy = H - 32
    x = draw_segments(d, PADX, sy, [seg("Opus 4.8", BLUE), seg("  |  ", MUTED)])
    # small folder glyph (Menlo can't render the color emoji)
    fx = x
    d.rectangle([fx, sy + 5, fx + 17, sy + 16], fill=(214, 178, 92))
    d.rectangle([fx, sy + 3, fx + 8, sy + 7], fill=(214, 178, 92))
    x = fx + 23
    x = draw_segments(d, x, sy, [seg("getting-started-with-claude-agents", MUTED),
                                 seg("  |  ", MUTED),
                                 seg("▓░░░░░░░ ~10%", MUTED)])


def render(visible, spinner_phase=0, typed=None):
    """visible: list of TRANSCRIPT entries to draw fully.
    typed: (entry, nchars) to animate the user prompt being typed."""
    img, d = base()
    y = 28
    for kind, *rest in visible:
        if kind == "gap":
            y += LINE_H // 2 + 4
            continue
        if kind == "promptbar":
            segs = rest[0]
            # grey rounded bar spanning width
            d.rounded_rectangle([PADX - 8, y - 4, W - PADX, y + 24], radius=7, fill=BAR)
            draw_segments(d, PADX, y, segs)
            y += LINE_H + 6
            continue
        if kind == "spinner":
            segs = rest[0]
            # animate the asterisk glyph
            glyph = ["✻", "✺", "✹", "✸"][spinner_phase % 4]
            segs = [(glyph + " ", ORANGE, FONT)] + segs[1:]
            draw_segments(d, PADX, y, segs)
            y += LINE_H
            continue
        # normal line
        indent, segs = rest[0], rest[1]
        draw_segments(d, PADX + indent, y, segs)
        y += LINE_H

    # typed prompt animation (only used for the very first entry)
    if typed:
        entry, n = typed
        segs = entry[1]
        # first segment is the chevron, second is the typed text
        chev = segs[0]
        text_seg = segs[1]
        d.rounded_rectangle([PADX - 8, 24, W - PADX, 52], radius=7, fill=BAR)
        x = draw_segments(d, PADX, 28, [chev])
        shown = text_seg[0][:n]
        d.text((x, 28), shown, font=text_seg[2], fill=text_seg[1])
        cw = d.textlength(shown, font=text_seg[2])
        d.rectangle([x + cw + 1, 30, x + cw + 11, 48], fill=CURSOR)

    draw_chrome(d)
    return img


def build_frames():
    frames, durations = [], []

    # 1) type the user prompt
    prompt_entry = TRANSCRIPT[0]
    text = prompt_entry[1][1][0]
    for n in range(0, len(text) + 1):
        frames.append(render([], typed=(prompt_entry, n)))
        durations.append(40 if n < len(text) else 450)

    # 2) reveal transcript line by line
    for i in range(1, len(TRANSCRIPT)):
        visible = TRANSCRIPT[: i + 1]
        kind = TRANSCRIPT[i][0]
        frames.append(render(visible))
        if kind == "gap":
            durations.append(120)
        elif TRANSCRIPT[i][0] == "line" and "NVDA" in str(TRANSCRIPT[i]):
            durations.append(650)
        elif kind == "spinner":
            durations.append(300)
        else:
            durations.append(300)

    # 3) animate the spinner a few cycles on the final view
    full = TRANSCRIPT[:]
    for phase in range(8):
        frames.append(render(full, spinner_phase=phase))
        durations.append(180)
    # hold
    for _ in range(4):
        frames.append(render(full, spinner_phase=7))
        durations.append(400)
    return frames, durations


def main():
    frames, durations = build_frames()
    out = ASSETS / "terminal.gif"
    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True, disposal=2,
    )
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB, {len(frames)} frames)")
    if shutil.which("gifsicle"):
        subprocess.run(
            ["gifsicle", "-O3", "--colors", "80", "-o", str(out), str(out)],
            check=True,
        )
        print(f"optimized → {out.stat().st_size // 1024} KB")
    else:
        print("gifsicle not found — skipped optimization")


if __name__ == "__main__":
    main()

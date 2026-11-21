"""Build the profile header from the addobari.com homepage hero:
'Building products / that get you.' in Inter Tight, each line rising into
place once on load (the site's LineReveal), still for reduced motion.

Run by hand when the header changes:  python scripts/header.py
"""
from pathlib import Path

from typeset import SANS, THEMES, frame, text, text_path

OUT = Path(__file__).resolve().parent.parent / "assets"

LINES = ["Building products", "that get you."]
W, H = 800, 236
SIZE = 88
LEADING = SIZE * 1.04
FIRST_BASELINE = 140


def build(theme: str) -> str:
    c = THEMES[theme]
    css = """
.l{transform:translateY(105%);animation:rise 1.25s cubic-bezier(.22,1,.36,1) forwards}
.l1{animation-delay:.1s}.l2{animation-delay:.22s}
@keyframes rise{to{transform:none}}
@media (prefers-reduced-motion:reduce){.l{transform:none;animation:none}}
"""
    parts = [
        f'<rect x="0" y="0" width="{W}" height="1" fill="{c["ink"]}"/>',
        text("Addo Bari Alyfathin", SANS, 15, 0, 30, c["muted"], tracking=-0.005),
        text("Product manager, Tokyo", SANS, 15, W, 30, c["muted"], tracking=-0.005, align="right"),
    ]
    clips = []
    for i, line in enumerate(LINES, start=1):
        y = FIRST_BASELINE + (i - 1) * LEADING
        d, _ = text_path(line, SANS, SIZE, -4, y, tracking=-0.045)
        top = y - SIZE * 0.82
        clips.append(f'<clipPath id="c{i}"><rect x="-20" y="{top:.1f}" width="{W + 40}" '
                     f'height="{SIZE * 1.1:.1f}"/></clipPath>')
        parts.append(f'<g clip-path="url(#c{i})"><g class="l l{i}" style="transform-box:fill-box">'
                     f'<path fill="{c["ink"]}" d="{d}"/></g></g>')
    defs = "".join(clips) + f"<style>{css}</style>"
    label = "Building products that get you. Addo Bari, product manager in Tokyo."
    return frame("".join(parts), W, H, theme, label, defs)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(build(theme))
    print("header written")

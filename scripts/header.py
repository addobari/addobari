"""Build the animated profile header: 'What I ___' with the verb cycling
build → write → watch → listen → eat, as on the link-in-bio page.
Styled after the addobari.com studio homepage.

Run by hand when the header changes:  python scripts/header.py
"""
from pathlib import Path

from typeset import SANS, SERIF, THEMES, frame, text, text_path

OUT = Path(__file__).resolve().parent.parent / "assets"

VERBS = ["build", "write", "watch", "listen", "eat"]
STEP = 3.0                      # seconds each verb holds the stage
PERIOD = STEP * len(VERBS)
W, H = 800, 262
VERB_SIZE = 168
BASELINE = 232


def arrow(x, y, colour):
    s = 24
    return (f'<g stroke="{colour}" stroke-width="2.6" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">'
            f'<path d="M{x} {y} L{x + s} {y - s}"/>'
            f'<path d="M{x + 7} {y - s} L{x + s} {y - s} L{x + s} {y - s + 17}"/></g>')


def build(theme: str) -> str:
    c = THEMES[theme]
    pct_in = 0.6 / PERIOD * 100
    pct_hold = STEP / PERIOD * 100
    pct_out = pct_hold + pct_in
    css = f"""
.v{{opacity:0;animation:cycle {PERIOD}s cubic-bezier(.22,1,.36,1) infinite both}}
.v0{{opacity:1}}
@keyframes cycle{{
0%{{transform:translateY(120px);opacity:0}}
{pct_in:.3f}%{{transform:translateY(0);opacity:1}}
{pct_hold:.3f}%{{transform:translateY(0);opacity:1}}
{pct_out:.3f}%{{transform:translateY(-80px);opacity:0}}
100%{{transform:translateY(-80px);opacity:0}}}}
{''.join(f'.v{i}{{animation-delay:{i * STEP - 0.6:.1f}s}}' for i in range(len(VERBS)))}
@media (prefers-reduced-motion:reduce){{.v{{animation:none;opacity:0}}.v0{{opacity:1}}}}
"""
    parts = [
        f'<rect x="0" y="0" width="{W}" height="1" fill="{c["ink"]}"/>',
        text("Addo Bari Alyfathin", SANS, 15, 0, 30, c["muted"], tracking=-0.005),
        text("Product manager, Tokyo", SANS, 15, W, 30, c["muted"], tracking=-0.005, align="right"),
        text("What I", SANS, 46, -1, 104, c["ink"], tracking=-0.045),
        '<g clip-path="url(#stage)">',
    ]
    for i, verb in enumerate(VERBS):
        d, width = text_path(verb, SERIF, VERB_SIZE, -4, BASELINE, tracking=-0.03)
        parts.append(f'<g class="v v{i}"><path fill="{c["ink"]}" d="{d}"/>'
                     f'{arrow(width + 18, BASELINE - 78, c["accent"])}</g>')
    parts.append("</g>")
    defs = (f'<clipPath id="stage"><rect x="-20" y="114" width="{W + 40}" height="{H - 114 + 30}"/></clipPath>'
            f'<style>{css}</style>')
    label = f"What I {', '.join(VERBS)}. Addo Bari, product manager in Tokyo."
    return frame("".join(parts), W, H, theme, label, defs)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(build(theme))
    print("header written")

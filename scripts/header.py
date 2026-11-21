"""Build the animated profile header: 'What I ___' with the verb cycling
build → write → watch → listen → eat, as on the link-in-bio page.

Run once by hand when the header changes:  python scripts/header.py
"""
from pathlib import Path

from typeset import MONO, SERIF, SERIF_ITALIC, THEMES, measure, text, text_path

OUT = Path(__file__).resolve().parent.parent / "assets"

# verb, accent (the platform colour of each verb on the link-in-bio page)
VERBS = [
    ("build", "#7B6EE0"),
    ("write", "#FF6B1A"),
    ("watch", "#3AB85A"),
    ("listen", "#6B5FE0"),
    ("eat", "#1A8C6E"),
]
STEP = 3.0                      # seconds each verb holds the stage
PERIOD = STEP * len(VERBS)
W, H = 880, 284
VERB_SIZE = 132
BASELINE = 236


def arrow(x, y, colour):
    """A small north-east arrow drawn as strokes, sitting at the verb's x-height."""
    s = 22
    return (f'<g stroke="{colour}" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">'
            f'<path d="M{x} {y} L{x + s} {y - s}"/>'
            f'<path d="M{x + 6} {y - s} L{x + s} {y - s} L{x + s} {y - s + 16}"/></g>')


def build(theme: str) -> str:
    c = THEMES[theme]
    pct_in = 0.6 / PERIOD * 100         # slide-in takes 0.6s
    pct_hold = STEP / PERIOD * 100      # visible until the next verb arrives
    pct_out = pct_hold + pct_in
    css = f"""
.v{{opacity:0;animation:cycle {PERIOD}s cubic-bezier(.22,.8,.24,1) infinite both}}
.v0{{opacity:1}}
@keyframes cycle{{
0%{{transform:translateY(64px);opacity:0}}
{pct_in:.3f}%{{transform:translateY(0);opacity:1}}
{pct_hold:.3f}%{{transform:translateY(0);opacity:1}}
{pct_out:.3f}%{{transform:translateY(-64px);opacity:0}}
100%{{transform:translateY(-64px);opacity:0}}}}
{''.join(f'.v{i}{{animation-delay:{i * STEP - 0.6:.1f}s}}' for i in range(len(VERBS)))}
@media (prefers-reduced-motion:reduce){{.v{{animation:none;opacity:0}}.v0{{opacity:1}}}}
"""
    parts = [
        text("ADDO BARI ALYFATHIN", MONO, 12.5, 0, 30, c["muted"], tracking=0.14),
        text("PRODUCT MANAGER  ·  TOKYO", MONO, 12.5, W, 30, c["muted"], tracking=0.14, align="right"),
        f'<rect x="0" y="48" width="{W}" height="1" fill="{c["rule"]}"/>',
        text("What I", SERIF, 40, 2, 112, c["muted"]),
        '<g clip-path="url(#stage)">',
    ]
    for i, (verb, accent) in enumerate(VERBS):
        d, width = text_path(verb, SERIF_ITALIC, VERB_SIZE, 0, BASELINE)
        parts.append(f'<g class="v v{i}"><path fill="{c["ink"]}" d="{d}"/>'
                     f'{arrow(width + 22, BASELINE - 58, accent)}</g>')
    parts.append("</g>")
    parts.append(f'<rect x="0" y="{H - 1}" width="{W}" height="1" fill="{c["rule"]}"/>')
    verbs = ", ".join(v for v, _ in VERBS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="What I {verbs}. Addo Bari, product manager in Tokyo.">'
            f'<defs><clipPath id="stage"><rect x="-10" y="122" width="{W + 20}" height="150"/></clipPath>'
            f'<style>{css}</style></defs>' + "".join(parts) + "</svg>")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(build(theme))
    print("header written")

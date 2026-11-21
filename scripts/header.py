"""Profile header: the addobari.com hero type under a band of the site's own
shaders. A MeshGradient film loop (the project-tile palette) is rendered frame
by frame through the fluted-glass shader in headless Chrome, crossfaded into a
seamless loop, laid over the typeset panel, and written as animated WebP.

Each day the film starts from a different point, so the band is never the
same twice. A static PNG is written too for visitors who prefer reduced motion.

usage: python scripts/header.py [--chrome PATH] [--date YYYY-MM-DD]   (writes to out/)
"""
import argparse
import datetime as dt
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

import cairosvg
from PIL import Image

from typeset import SANS, THEMES, text, text_path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"            # published to the `output` branch, never committed to main
SHADER = Path(__file__).resolve().parent / "shader"

SCALE = 2                     # render at 2x for sharp type on retina screens
W, PAD, RADIUS = 880, 40, 14
BAND_H = 150
LINES = ["Building products", "that get you."]
SIZE, LEADING = 88, 88 * 1.04
TEXT_TOP = BAND_H + 36        # rule sits here
H = round(TEXT_TOP + 122 + LEADING + 48)

FPS, SECONDS, FADE = 12, 8, 2  # 8 s loop, 2 s crossfade to hide the seam
SHADER_SPEED = 0.6             # shader-ms per real ms, close to the site's hover speed


def text_layer(theme: str) -> Image.Image:
    c = THEMES[theme]
    x0 = PAD
    parts = [
        f'<rect width="{W}" height="{H}" rx="{RADIUS}" fill="{c["bg"]}"/>',
        f'<rect x="{x0}" y="{TEXT_TOP}" width="{W - 2 * PAD}" height="1" fill="{c["ink"]}"/>',
        text("Addo Bari Alyfathin", SANS, 15, x0, TEXT_TOP + 30, c["muted"], tracking=-0.005),
        text("Product manager, Tokyo", SANS, 15, W - PAD, TEXT_TOP + 30, c["muted"],
             tracking=-0.005, align="right"),
    ]
    for i, line in enumerate(LINES):
        d, _ = text_path(line, SANS, SIZE, x0 - 4, TEXT_TOP + 122 + i * LEADING, tracking=-0.045)
        parts.append(f'<path fill="{c["ink"]}" d="{d}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">' + "".join(parts) + "</svg>")
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W * SCALE)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def band_mask() -> Image.Image:
    """Full-bleed band with the card's top corners rounded."""
    w, h, r = W * SCALE, BAND_H * SCALE, RADIUS * SCALE
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
           f'<path d="M0 {h} V{r} A{r} {r} 0 0 1 {r} 0 H{w - r} A{r} {r} 0 0 1 {w} {r} V{h} Z" fill="#fff"/></svg>')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("L")


def render_band(chrome: str, day: dt.date, workdir: Path) -> list[Image.Image]:
    loop, fade = FPS * SECONDS, FPS * FADE
    total = loop + fade
    span = (total / FPS) * 1000 * SHADER_SPEED
    start = (day.toordinal() % 997) * 9_000          # a different stretch of film each day
    subprocess.run(["node", str(SHADER / "render.mjs"), str(workdir), str(total), str(span),
                    str(start), chrome], check=True)
    raw = [Image.open(p).convert("RGB") for p in sorted(workdir.glob("f*.png"))]
    crop = (80 * SCALE, 12 * SCALE, (80 + W) * SCALE, (12 + BAND_H) * SCALE)   # drop the overscan edges
    raw = [im.crop(crop) for im in raw]
    # Seamless loop: frame i of the loop fades from the tail (loop+i) into the head (i).
    return [Image.blend(raw[loop + i], raw[i], i / fade) if i < fade else raw[i]
            for i in range(loop)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chrome", default=shutil.which("google-chrome") or "/usr/bin/google-chrome")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()
    day = dt.date.fromisoformat(args.date)
    OUT.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        band = render_band(args.chrome, day, Path(tmp))
    mask = band_mask()
    for theme in THEMES:
        base = text_layer(theme)
        out = []
        for f in band:
            im = base.copy()
            im.paste(f, (0, 0), mask)
            out.append(im)
        out[0].save(OUT / f"header-{theme}.webp", save_all=True, append_images=out[1:],
                    duration=round(1000 / FPS), loop=0, quality=82, method=6)
        out[0].save(OUT / f"header-{theme}-still.png", optimize=True)
        print(theme, (OUT / f"header-{theme}.webp").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()

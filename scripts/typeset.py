"""Shared typesetting: shape text with HarfBuzz and emit it as SVG outlines,
so every image renders identically with no font dependency."""
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"
SERIF = FONTS / "cormorant-garamond-latin-500-normal.woff2"
SERIF_ITALIC = FONTS / "cormorant-garamond-latin-500-italic.woff2"
MONO = FONTS / "ibm-plex-mono-latin-500-normal.woff2"

THEMES = {
    "light": {"ink": "#16150F", "muted": "#7A766C", "rule": "#D9D5CC", "faint": "#E6E2DA"},
    "dark": {"ink": "#EDEAE3", "muted": "#8E897F", "rule": "#3A3832", "faint": "#2A2925"},
}


def _num(v: float) -> str:
    return ("%.1f" % v).rstrip("0").rstrip(".")


@lru_cache(maxsize=None)
def _load(path: Path):
    tt = TTFont(str(path))
    tt.flavor = None
    buf = BytesIO()
    tt.save(buf)
    font = hb.Font(hb.Face(buf.getvalue()))
    return tt, font, tt["head"].unitsPerEm


def measure(text: str, path: Path, size: float, tracking: float = 0.0) -> float:
    return text_path(text, path, size, 0, 0, tracking)[1]


def text_path(text, path, size, x, y, tracking=0.0, align="left"):
    """Return (svg path data, width in px). `tracking` is in em."""
    tt, font, upem = _load(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    infos, positions = buf.glyph_infos, buf.glyph_positions
    scale = size / upem
    track = tracking * upem
    total = sum(p.x_advance for p in positions) + track * max(len(positions) - 1, 0)
    width = total * scale
    if align == "right":
        x -= width
    elif align == "center":
        x -= width / 2
    glyphs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    pen = SVGPathPen(glyphs, ntos=_num)
    cursor = 0.0
    for info, pos in zip(infos, positions):
        transform = (scale, 0, 0, -scale,
                     x + (cursor + pos.x_offset) * scale, y - pos.y_offset * scale)
        glyphs[order[info.codepoint]].draw(TransformPen(pen, transform))
        cursor += pos.x_advance + track
    return pen.getCommands(), width


def text(content, path, size, x, y, fill, tracking=0.0, align="left", extra=""):
    d, _ = text_path(content, path, size, x, y, tracking, align)
    return f'<path fill="{fill}" d="{d}"{extra}/>'

"""Daily refresh of the profile README.

- Writing: latest essays from Be Present (Substack RSS)
- Lately: last film logged on Letterboxd (diary RSS); section hides when empty
- Activity: weekly contribution chart, rendered as light/dark SVGs

Each source fails soft: if a fetch breaks, that section keeps its last content.
"""
import datetime as dt
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

from typeset import SANS, SERIF_ITALIC, THEMES, frame, measure, text

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ASSETS = ROOT / "assets"

GITHUB_USER = "addobari"
SUBSTACK_FEED = "https://addobari.substack.com/feed"
LETTERBOXD_USER = "dobari"
UA = {"User-Agent": "Mozilla/5.0 (profile-readme; github.com/addobari/addobari)"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def replace_section(md: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    if not pattern.search(md):
        raise SystemExit(f"README is missing the {name} markers")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}" if body else
                       f"{m.group(1)}\n{m.group(3)}", md)


# ── Writing ──────────────────────────────────────────────────────────────────
def writing_section(limit: int = 3) -> str:
    root = ET.fromstring(fetch(SUBSTACK_FEED))
    rows = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip().replace("[", "\\[").replace("]", "\\]")
        link = (item.findtext("link") or "").strip()
        date = parsedate_to_datetime(item.findtext("pubDate")).strftime("%-d %b %Y").upper()
        if title and link:
            rows.append(f"**[{title}]({link})**<br>\n<sub>{date}</sub>")
        if len(rows) == limit:
            break
    rows.append("<sub>[ALL ESSAYS ON BE PRESENT &ensp;→](https://addobari.substack.com)</sub>")
    return "\n\n".join(rows)


# ── Lately (Letterboxd) ──────────────────────────────────────────────────────
def lately_section() -> str:
    root = ET.fromstring(fetch(f"https://letterboxd.com/{LETTERBOXD_USER}/rss/"))
    ns = {"lb": "https://letterboxd.com"}
    for item in root.iter("item"):
        film = item.findtext("lb:filmTitle", namespaces=ns)
        if not film:
            continue                     # lists and other non-diary items
        year = item.findtext("lb:filmYear", namespaces=ns) or ""
        rating = item.findtext("lb:memberRating", namespaces=ns)
        link = item.findtext("link") or f"https://letterboxd.com/{LETTERBOXD_USER}/"
        stars = ""
        if rating:
            r = float(rating)
            stars = " &ensp;" + "★" * int(r) + ("½" if r % 1 else "")
        year = f" ({year})" if year else ""
        return (f"### Lately\n\nLast watched **[{html.escape(film)}]({link})**{year}{stars}"
                f" &ensp;<sub>[LETTERBOXD →](https://letterboxd.com/{LETTERBOXD_USER}/)</sub>")
    return ""                            # nothing logged yet: hide the section


# ── Activity chart ───────────────────────────────────────────────────────────
def contributions() -> list[tuple[dt.date, int]]:
    page = fetch(f"https://github.com/users/{GITHUB_USER}/contributions")
    dates = dict(re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="([^"]+)"', page))
    counts = {}
    for target, label in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', page):
        m = re.match(r"\s*(No|[\d,]+) contribution", label)
        if m:
            counts[target] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    days = sorted((dt.date.fromisoformat(d), counts.get(i, 0)) for d, i in dates.items())
    if len(days) < 300:
        raise RuntimeError(f"unexpected contribution page shape ({len(days)} days)")
    return days


def weekly(days):
    weeks, current, start = [], 0, None
    for day, n in days:
        if day.weekday() == 6 and start is not None:      # weeks run Sun–Sat, like GitHub
            weeks.append((start, current))
            current, start = 0, None
        start = start or day
        current += n
    weeks.append((start, current))
    return weeks


def chart(days, theme: str) -> str:
    c = THEMES[theme]
    weeks = weekly(days)
    total = sum(n for _, n in days)
    peak_start, peak = max(weeks, key=lambda w: w[1])
    W, H = 800, 250
    top, base = 134, 214                  # bar area
    gap = W / len(weeks)
    bar = max(gap * 0.42, 3)
    figure = f"{total:,}"
    fig_w = measure(figure, SERIF_ITALIC, 72, tracking=-0.035)
    parts = [
        f'<rect x="0" y="0" width="{W}" height="1" fill="{c["ink"]}"/>',
        text("Activity", SANS, 15, 0, 30, c["muted"], tracking=-0.005),
        text("github.com/addobari", SANS, 15, W, 30, c["muted"], tracking=-0.005, align="right"),
        text(figure, SERIF_ITALIC, 72, -2, 98, c["ink"], tracking=-0.035),
        text("contributions in the last 12 months", SANS, 22, fig_w + 14, 96, c["ink"], tracking=-0.03),
        f'<rect x="0" y="{base}" width="{W}" height="1" fill="{c["rule"]}"/>',
    ]
    for i, (start, n) in enumerate(weeks):
        cx = gap * i + gap / 2
        if n == 0:
            parts.append(f'<circle cx="{cx:.1f}" cy="{base - 4}" r="1.4" fill="{c["rule"]}"/>')
            continue
        h = max((n / peak) ** 0.75 * (base - top), bar)   # gentle compression so quiet weeks still read
        is_peak = (start, n) == (peak_start, peak)
        fill = c["accent"] if is_peak else c["muted"]
        parts.append(f'<rect x="{cx - bar / 2:.1f}" y="{base - h:.1f}" width="{bar:.1f}" '
                     f'height="{h:.1f}" rx="{bar / 2:.1f}" fill="{fill}"/>')
        if is_peak:
            label = f"{peak} in the week of {start.strftime('%-d %b')}"
            align = "right" if cx > W * 0.6 else "left"
            lx = cx + (-14 if align == "right" else 14)
            parts.append(text(label, SANS, 14, lx, top + 4, c["accent"], tracking=-0.005, align=align))
    seen = set()
    for i, (start, _) in enumerate(weeks):                 # month ticks
        if start.month in seen or start.day > 7:
            continue
        seen.add(start.month)
        parts.append(text(start.strftime("%b"), SANS, 13, gap * i + gap / 2, base + 26,
                          c["muted"], align="center"))
    label = f"{total:,} GitHub contributions in the last 12 months, by week. Busiest week: {peak}."
    return frame("".join(parts), W, H, theme, label)


def main() -> int:
    md = README.read_text()
    failures = 0
    for name, build in (("WRITING", writing_section), ("LATELY", lately_section)):
        try:
            md = replace_section(md, name, build())
        except Exception as e:                       # keep the last good content
            failures += 1
            print(f"{name}: skipped ({e})", file=sys.stderr)
    try:
        days = contributions()
        for theme in THEMES:
            (ASSETS / f"activity-{theme}.svg").write_text(chart(days, theme))
    except Exception as e:
        failures += 1
        print(f"ACTIVITY: skipped ({e})", file=sys.stderr)
    README.write_text(md)
    print(f"done, {failures} source(s) skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# How this profile is made

Everything on the profile is generated. One workflow, `.github/workflows/refresh.yml`, runs every morning at 06:17 Tokyo time.

**Header.** `header.py` drives headless Chrome through `shader/render.mjs`, which uses the same `@paper-design/shaders` as addobari.com. Each frame renders the site's MeshGradient film loop, in its project-tile palette, then passes that frame as a texture into the site's fluted-glass shader. Chrome runs WebGL in software (SwiftShader) because the runner has no GPU, and frames are fixed in time, so a given date always renders the same band. The script renders 120 frames and crossfades the last 2 s into the first 2 s so the 8 s loop has no seam. It sets the band over the typeset panel and encodes animated WebP for light and dark, plus a still for reduced motion. The start point in the film moves every day.

The renders are force-pushed to the `output` branch, which keeps no history, so a year of daily images never builds up in the repo.

**Type.** `typeset.py` shapes text with HarfBuzz and writes it out as SVG outlines. Inter Tight and Instrument Serif (SIL OFL, in `fonts/`) then render identically everywhere, with no font loading.

**Activity and Writing.** `update.py` reads the public contribution calendar and draws the weekly chart. It also pulls the latest essays from the Be Present RSS feed. Each source fails soft and keeps its last good output.

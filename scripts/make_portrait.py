
from __future__ import annotations

import argparse
import os
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from svgkit import CHAR_RATIO, PLAY_ONCE, document, esc, write

STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"

FS = 12.9
CHAR_W = FS * CHAR_RATIO
ASPECT = 0.48
LINE_H = CHAR_W / ASPECT

def to_rows(img: Image.Image, cols: int, gamma: float, contrast: float, invert: bool) -> list[str]:
    rows = max(1, round(cols * (img.height / img.width) * ASPECT))
    small = img.resize((cols, rows), Image.LANCZOS)

    rgba = np.asarray(small.convert("RGBA")).astype(np.float32) / 255.0
    lum = rgba[..., 0] * 0.2126 + rgba[..., 1] * 0.7152 + rgba[..., 2] * 0.0722
    alpha = rgba[..., 3]

    h, w = lum.shape
    core = lum[round(h * 0.18) : round(h * 0.72), round(w * 0.22) : round(w * 0.78)]
    core_a = alpha[round(h * 0.18) : round(h * 0.72), round(w * 0.22) : round(w * 0.78)]
    sample = core[core_a > 0.5]
    if sample.size < 32:
        sample = lum[alpha > 0.5]
    if sample.size:
        lo, hi = np.percentile(sample, (4, 96))
        if hi > lo:
            lum = np.clip((lum - lo) / (hi - lo), 0, 1)

    ink = lum if invert else 1.0 - lum
    ink = np.clip((ink - 0.5) * contrast + 0.5, 0, 1) ** gamma
    idx = np.rint(ink * (len(RAMP) - 1)).astype(int)
    idx[alpha <= 0.5] = 0

    return ["".join(RAMP[i] for i in row) for row in idx]

def trim(*variants: list[str]) -> tuple[list[list[str]], int]:
    rows = len(variants[0])
    cols = len(variants[0][0])

    def drawn(r: int, ch: int) -> bool:
        return any(v[r][ch] != " " for v in variants)

    top = next((r for r in range(rows) if any(drawn(r, c) for c in range(cols))), 0)
    bottom = next((r for r in range(rows - 1, -1, -1) if any(drawn(r, c) for c in range(cols))), rows - 1)
    left = next((c for c in range(cols) if any(drawn(r, c) for r in range(rows))), 0)
    right = next((c for c in range(cols - 1, -1, -1) if any(drawn(r, c) for r in range(rows))), cols - 1)

    cropped = [[row[left : right + 1] for row in v[top : bottom + 1]] for v in variants]
    return cropped, right - left + 1

def build(rows_light: list[str], rows_dark: list[str], cols: int, title: str) -> str:
    n = len(rows_light)
    width = round(cols * CHAR_W) + 2
    height = round(n * LINE_H) + 6
    wipe_w = cols * CHAR_W

    step = 0.075
    dur = 0.9

    clips, groups, cursors = [], [], []
    for i in range(n):
        y = 6 + i * LINE_H
        delay = i * step
        clips.append(
            f'<clipPath id="c{i}"><rect class="wp" x="1" y="{y - FS:.2f}" '
            f'width="{wipe_w if STATIC else 0:.2f}" height="{LINE_H:.2f}" '
            f'style="animation-delay:{delay:.3f}s"/></clipPath>'
        )
        light = esc(rows_light[i]).replace(" ", " ")
        dark = esc(rows_dark[i]).replace(" ", " ")
        groups.append(
            f'<g clip-path="url(#c{i})">'
            f'<text class="lt" x="1" y="{y:.2f}">{light}</text>'
            f'<text class="dk" x="1" y="{y:.2f}">{dark}</text>'
            f"</g>"
        )
        if not STATIC:
            cursors.append(
                f'<rect class="cu" x="1" y="{y - FS + 1:.2f}" width="{CHAR_W:.2f}" '
                f'height="{FS:.2f}" style="animation-delay:{delay:.3f}s,{delay + dur:.3f}s"/>'
            )

    css = (
        f"text{{font-family:'JBMRamp',ui-monospace,monospace;font-size:{FS}px;"
        f"white-space:pre;fill:var(--pt)}}"
        ".dk{display:none}"
        "@media(prefers-color-scheme:dark){.lt{display:none}.dk{display:inline}}"
        ".cu{fill:var(--accent)}"
    )
    if not STATIC:
        css += (
            f"@keyframes wp{{from{{width:0}}to{{width:{wipe_w:.2f}px}}}}"
            f"@keyframes rd{{from{{transform:translateX(0)}}"
            f"to{{transform:translateX({wipe_w:.2f}px)}}}}"
            "@keyframes cf{to{opacity:0}}"
            f".wp{{animation:wp {dur}s steps({cols},end);{PLAY_ONCE}}}"
            f".cu{{animation:rd {dur}s steps({cols},end),cf .18s linear;"
            "animation-fill-mode:both,forwards}"
        )

    body = f"<defs>{''.join(clips)}</defs>{''.join(groups)}{''.join(cursors)}"
    return document(
        width,
        height,
        body,
        css,
        ("ramp",),
        title=title,
        extra_vars={"dark": {"pt": "#c9d1d9"}, "light": {"pt": "#2a3038"}},
    )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", type=pathlib.Path)
    ap.add_argument("--out", default="portrait.svg")
    ap.add_argument("--cols", type=int, default=90)
    ap.add_argument("--gamma", type=float, default=0.80)
    ap.add_argument("--contrast", type=float, default=1.12)
    ap.add_argument("--title", default="Retrato ASCII")
    args = ap.parse_args()

    img = Image.open(args.photo)
    light = to_rows(img, args.cols, args.gamma, args.contrast, invert=False)
    dark = to_rows(img, args.cols, args.gamma, args.contrast, invert=True)
    (light, dark), cols = trim(light, dark)

    svg = build(light, dark, cols, args.title)
    write(args.out, svg)

    print(f"  {args.cols} cols sampled, trimmed to {cols} x {len(light)}"
          f"  ->  {round(cols * CHAR_W)}x{round(len(light) * LINE_H)} px natural")
    return 0

if __name__ == "__main__":
    sys.exit(main())

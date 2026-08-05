
from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from svgkit import PALETTE, PLAY_ONCE, ROOT, document, esc, write

STATIC = os.environ.get("STATIC") == "1"

W_BANNER = 860

W_CARD = 860

FS = 12.5

def anim(css: str) -> str:
    return "" if STATIC else css

def typed(text: str, x: int, y: int, fs: float, spans: list[tuple[str, str]], uid: str) -> tuple[str, str]:
    ch = fs * 0.6
    n = len(text)
    w = n * ch
    dur = max(0.9, n * 0.045)

    parts, cx = [], x
    for chunk, cls in spans:
        parts.append(f'<tspan class="{cls}">{esc(chunk)}</tspan>')
        cx += len(chunk) * ch

    css = anim(
        f"@keyframes t{uid}{{from{{width:0}}to{{width:{w:.1f}px}}}}"
        f"@keyframes c{uid}{{from{{transform:translateX(0)}}to{{transform:translateX({w:.1f}px)}}}}"
        f"@keyframes b{uid}{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
        f"#clip{uid} rect{{animation:t{uid} {dur}s steps({n},end);{PLAY_ONCE}}}"
        f"#cur{uid}{{animation:c{uid} {dur}s steps({n},end),"
        f"b{uid} .5s {dur:.2f}s steps(1,end) 4 forwards;animation-fill-mode:both}}"
    )
    body = (
        f'<clipPath id="clip{uid}"><rect x="{x}" y="{y - fs}" width="{0 if not STATIC else w:.1f}" '
        f'height="{fs * 1.5:.1f}"/></clipPath>'
        f'<g clip-path="url(#clip{uid})">'
        f'<text x="{x}" y="{y}" font-size="{fs}">{"".join(parts)}</text>'
        f"</g>"
        + (
            ""
            if STATIC
            else f'<rect id="cur{uid}" class="cur" x="{x}" y="{y - fs + 1.5:.1f}" '
            f'width="{ch:.1f}" height="{fs:.1f}"/>'
        )
    )
    return body, css

def banner(c: dict) -> None:
    h = 132
    line = f'{c["handle"]}@{c["host"]}:~$ {c["prompt"]}'
    spans = [
        (c["handle"], "u"),
        ("@", "p"),
        (c["host"], "hst"),
        (":~", "p"),
        ("$ ", "d"),
        (c["prompt"], "cmd"),
    ]
    body, tcss = typed(line, 0, 26, 15, spans, "b")

    body += (
        f'<text class="nm" x="0" y="86">{esc(c["name"])}</text>'
        f'<text class="tg" x="0" y="112">{esc(c["tagline"])}</text>'
    )

    css = (
        ".u{fill:var(--accent);font-weight:700}"
        ".hst{fill:var(--ink)}"
        ".p{fill:var(--faint)}"
        ".d{fill:var(--accent)}"
        ".cmd{fill:var(--dim)}"
        ".cur{fill:var(--accent)}"
        ".nm{font-size:38px;font-weight:700;fill:var(--ink);letter-spacing:-.02em}"
        ".tg{font-size:13px;fill:var(--dim)}"
        + tcss
        + anim(
            "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
            f".nm{{animation:up .7s 1.5s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".tg{{animation:up .7s 1.7s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
        )
    )
    write(
        "banner.svg",
        document(W_BANNER, h, body, css, ("ui", "ui-bold"), title=f'{c["name"]} — {c["tagline"]}'),
    )

def card(c: dict, p: dict) -> None:
    pad = 0
    key_w = 132
    body, delay = [], 0.15

    head = f'{c["handle"]}@{c["host"]}'
    body.append(f'<text class="hd" x="{pad}" y="20">{esc(head)}</text>')
    body.append(f'<line class="rule" x1="{pad}" y1="32" x2="{W_CARD - pad}" y2="32"/>')

    rows = list(c["rows"])
    if c.get("contact"):
        rows = rows + [{"key": "contacto", "value": c["contact"]}]

    y = 60
    for row in rows:
        delay += 0.09
        body.append(
            f'<g class="rw" style="animation-delay:{delay:.2f}s">'
            f'<text class="k" x="{pad}" y="{y}">{esc(row["key"])}</text>'
            f'<text class="v" x="{pad + key_w}" y="{y}">{esc(row["value"])}</text>'
            f"</g>"
        )
        y += 21
        if row.get("sub"):
            body.append(
                f'<g class="rw" style="animation-delay:{delay + 0.05:.2f}s">'
                f'<text class="s" x="{pad + key_w}" y="{y}">{esc(row["sub"])}</text></g>'
            )
            y += 19
        y += 7

    fy = y + 18
    t = p["totals"]
    foot = (
        f'{t["repos"]} repos públicos · {len(p["languages"])} lenguajes · '
        f'{t["year"]} contribuciones en el último año'
    )
    body.append(f'<line class="rule" x1="{pad}" y1="{fy - 16}" x2="{W_CARD - pad}" y2="{fy - 16}"/>')
    body.append(f'<text class="ft" x="{pad}" y="{fy}">{esc(foot)}</text>')

    sw, sg = 28, 5
    for i in range(5):
        body.append(
            f'<rect class="sw" x="{W_CARD - pad - (5 - i) * (sw + sg) + sg}" y="{fy - 10}" '
            f'width="{sw}" height="10" rx="2" fill="var(--heat{i})" '
            f'style="animation-delay:{1.0 + i * 0.06:.2f}s"/>'
        )
    h_card = fy + 14

    css = (
        f".hd{{font-size:14px;font-weight:700;fill:var(--accent)}}"
        f".k{{font-size:{FS}px;fill:var(--dim)}}"
        f".v{{font-size:{FS}px;fill:var(--ink)}}"
        f".s{{font-size:11px;fill:var(--faint)}}"
        ".ft{font-size:10.5px;fill:var(--dim)}"
        ".rule{stroke:var(--rule);stroke-width:1}"
        + anim(
            "@keyframes rw{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
            "@keyframes sw{from{opacity:0;transform:scaleX(0)}to{opacity:1;transform:none}}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".rw{{animation:rw .5s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".sw{{transform-box:fill-box;transform-origin:left;"
            f"animation:sw .4s cubic-bezier(.2,.8,.3,1);{PLAY_ONCE}}}"
            f".hd,.rule,.ft{{animation:fade .6s .1s linear;{PLAY_ONCE}}}"
        )
    )
    write(
        "card.svg",
        document(W_CARD, h_card, "".join(body), css, ("ui", "ui-bold"), title=f"Ficha de {c['name']}"),
    )

def main() -> int:
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    p = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    banner(c)
    card(c, p)
    return 0

if __name__ == "__main__":
    sys.exit(main())

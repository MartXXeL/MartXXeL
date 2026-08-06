
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from svgkit import PLAY_ONCE, ROOT, document, esc, write

DATA = ROOT / "data" / "profile.json"
STATIC = os.environ.get("STATIC") == "1"

W_FULL = 860
W_HALF = 426
H_HALF = 224

MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
WEEKDAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

def anim(css: str) -> str:
    return "" if STATIC else css

def d(date: str) -> dt.date:
    return dt.date.fromisoformat(date)

def human(date: str | None) -> str:
    if not date:
        return "—"
    x = d(date)
    return f"{x.day} {MONTHS[x.month - 1]} {x.year}"

def thousands(n: int) -> str:
    return f"{n:,}".replace(",", ".")

def heading(slug: str, label: str, note: str = "") -> None:
    h, fs = 30, 13
    x = 0
    label_w = len(label) * fs * 0.6
    note_w = len(note) * 11 * 0.6
    rule_x0 = x + label_w + 14
    rule_x1 = W_FULL - (note_w + 14 if note else 0)

    css = (
        f".l{{font-size:{fs}px;font-weight:700;fill:var(--ink);letter-spacing:.08em}}"
        f".n{{font-size:11px;fill:var(--faint);letter-spacing:.06em}}"
        ".r{stroke:var(--rule);stroke-width:1}"
        + anim(
            "@keyframes hl{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
            "@keyframes hr{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}"
            "@keyframes hn{from{opacity:0}to{opacity:.999}}"
            f".l{{animation:hl .5s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".r{{stroke-dasharray:var(--len);animation:hr .9s .15s cubic-bezier(.3,.8,.3,1);{PLAY_ONCE}}}"
            f".n{{animation:hn .5s .7s linear;{PLAY_ONCE}}}"
        )
    )
    body = (
        f'<text class="l" x="{x}" y="{h / 2 + 5:.0f}">{esc(label)}</text>'
        f'<line class="r" x1="{rule_x0:.0f}" y1="{h / 2:.0f}" x2="{rule_x1:.0f}" y2="{h / 2:.0f}" '
        f'style="--len:{rule_x1 - rule_x0:.0f}"/>'
    )
    if note:
        body += f'<text class="n" x="{W_FULL}" y="{h / 2 + 4:.0f}" text-anchor="end">{esc(note)}</text>'

    write(f"h-{slug}.svg", document(W_FULL, h, body, css, ("ui", "ui-bold"), title=label))

def heatmap(p: dict) -> None:
    cell, gap = 12, 3
    pitch = cell + gap
    y0 = 30
    days = p["days"]

    first = d(days[0]["date"])
    lead = first.weekday()
    grid: list[dict | None] = [None] * lead + list(days)
    weeks = (len(grid) + 6) // 7
    grid += [None] * (weeks * 7 - len(grid))

    width = W_FULL
    x0 = round((width - (weeks * pitch - gap)) / 2)
    height = y0 + 7 * pitch + 46

    def level(count: int) -> int:
        if count == 0:
            return 0
        if count <= 2:
            return 1
        if count <= 5:
            return 2
        if count <= 9:
            return 3
        return 4

    cells, months, seen_month = [], [], set()
    for i, day in enumerate(grid):
        w, dow = divmod(i, 7)
        x = x0 + w * pitch
        y = y0 + dow * pitch
        if day is None:
            continue
        date = d(day["date"])
        lv = level(day["count"])
        delay = w * 0.012 + dow * 0.026
        cells.append(
            f'<rect class="c l{lv}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'style="animation-delay:{delay:.3f}s"><title>{day["count"]} · {day["date"]}</title></rect>'
        )
        key = (date.year, date.month)
        if date.day <= 7 and key not in seen_month:
            seen_month.add(key)
            months.append(f'<text class="ax" x="{x}" y="{y0 - 9}">{MONTHS[date.month - 1]}</text>')

    rows = "".join(
        f'<text class="ax" x="{x0 - 8}" y="{y0 + i * pitch + cell - 2}" text-anchor="end">{WEEKDAYS[i]}</text>'
        for i in (0, 2, 4, 6)
    )

    lg_x = width - 8 - (5 * pitch + 74)
    lg_y = y0 + 7 * pitch + 20
    legend = f'<text class="ax" x="{lg_x}" y="{lg_y + cell - 2}">menos</text>'
    for i in range(5):
        legend += (
            f'<rect class="c l{i} lg" x="{lg_x + 40 + i * pitch}" y="{lg_y}" '
            f'width="{cell}" height="{cell}" rx="2"/>'
        )
    legend += f'<text class="ax" x="{lg_x + 40 + 5 * pitch + 6}" y="{lg_y + cell - 2}">más</text>'

    t = p["totals"]
    foot = (
        f'<text class="ft" x="{x0}" y="{lg_y + cell - 2}">'
        f'{thousands(t["year"])} contribuciones · {t["active_days"]} días activos · '
        f'pico {t["best_day"]["count"]} el {human(t["best_day"]["date"])}</text>'
    )

    css = (
        ".ax{font-size:9px;fill:var(--faint);letter-spacing:.04em}"
        ".ft{font-size:10px;fill:var(--dim)}"
        ".c{stroke:rgba(127,127,127,.10)}"
        + "".join(f".l{i}{{fill:var(--heat{i})}}" for i in range(5))
        + anim(
            "@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:none}}"
            f".c{{transform-box:fill-box;transform-origin:center;"
            f"animation:pop .42s cubic-bezier(.2,.9,.3,1.3);{PLAY_ONCE}}}"
            ".lg{animation-delay:1.05s}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".ax,.ft{{animation:fade .6s 1.1s linear;{PLAY_ONCE}}}"
        )
    )
    body = "".join(months) + rows + "".join(cells) + legend + foot
    write(
        "heatmap.svg",
        document(
            width,
            height,
            body,
            css,
            ("ui",),
            title=f'Calendario de contribuciones: {t["year"]} en el último año',
        ),
    )

def stats(p: dict) -> None:
    h = 200
    weeks = p["weeks"]
    t, s = p["totals"], p["streak"]

    left = [
        f'<text class="huge" x="0" y="72">{thousands(t["year"])}</text>',
        '<text class="cap" x="0" y="94">contribuciones · últimos 12 meses</text>',
    ]
    figures = [
        ("días activos", f'{t["active_days"]}', f'de {p["window"]["days"]}'),
        ("racha máxima", f'{s["longest"]["length"]} d', human(s["longest"]["end"])),
        ("racha actual", f'{s["current"]["length"]} d', "en curso" if s["current"]["length"] else "—"),
        ("repos públicos", f'{t["repos"]}', f'desde {d(p["created_at"]).year}'),
    ]
    for i, (label, value, note) in enumerate(figures):
        y = 128 + i * 18
        left.append(f'<text class="fl" x="0" y="{y}">{esc(label)}</text>')
        left.append(f'<text class="fv" x="150" y="{y}" text-anchor="end">{esc(value)}</text>')
        left.append(f'<text class="fn" x="162" y="{y}">{esc(note)}</text>')

    cx0, cy1, ch = 322, 158, 104
    bar, bgap = 6, 3
    peak = max((w["total"] for w in weeks), default=1) or 1
    bars = []
    for i, w in enumerate(weeks):
        x = cx0 + i * (bar + bgap)
        hgt = max(2, round(ch * w["total"] / peak)) if w["total"] else 2
        cls = "b" if w["total"] else "b z"
        bars.append(
            f'<rect class="{cls}" x="{x}" y="{cy1 - hgt}" width="{bar}" height="{hgt}" rx="1.5" '
            f'style="--h:{hgt}px;animation-delay:{0.25 + i * 0.011:.3f}s">'
            f'<title>{w["total"]} · semana del {w["start"]}</title></rect>'
        )
    cx1 = cx0 + len(weeks) * (bar + bgap) - bgap

    ticks = []
    seen = set()
    for i, w in enumerate(weeks):
        m = d(w["start"]).month
        if m not in seen and i % 4 == 0:
            seen.add(m)
            ticks.append(
                f'<text class="ax" x="{cx0 + i * (bar + bgap)}" y="{cy1 + 14}">{MONTHS[m - 1]}</text>'
            )

    right = [
        f'<text class="cap" x="{cx0}" y="26">actividad semanal</text>',
        f'<text class="ax" x="{cx1}" y="26" text-anchor="end">pico {peak} / semana</text>',
        f'<line class="base" x1="{cx0}" y1="{cy1 + 1}" x2="{cx1}" y2="{cy1 + 1}"/>',
        *bars,
        *ticks,
    ]

    css = (
        ".huge{font-size:58px;font-weight:700;fill:var(--ink);letter-spacing:-.02em}"
        ".cap{font-size:11px;fill:var(--dim);letter-spacing:.04em}"
        ".fl{font-size:11px;fill:var(--dim)}"
        ".fv{font-size:11px;font-weight:700;fill:var(--ink)}"
        ".fn{font-size:10px;fill:var(--faint)}"
        ".ax{font-size:9px;fill:var(--faint)}"
        ".base{stroke:var(--rule);stroke-width:1}"
        ".b{fill:var(--accent)}.b.z{fill:var(--rule)}"
        + anim(
            "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
            "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".b{{transform-box:fill-box;transform-origin:bottom;"
            f"animation:grow .5s cubic-bezier(.2,.8,.3,1);{PLAY_ONCE}}}"
            f".huge{{animation:rise .7s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".cap,.fl,.fv,.fn,.ax,.base{{animation:fade .6s .35s linear;{PLAY_ONCE}}}"
        )
    )
    write(
        "stats.svg",
        document(
            W_FULL,
            h,
            "".join(left + right),
            css,
            ("ui", "ui-bold"),
            title=f'{t["year"]} contribuciones en los últimos 12 meses',
        ),
    )

def rhythm(p: dict) -> None:
    h = H_HALF
    days = p["days"]

    by_dow = [0] * 7
    by_month = [0] * 12
    for day in days:
        date = d(day["date"])
        by_dow[date.weekday()] += day["count"]
        by_month[date.month - 1] += day["count"]

    pad = 14
    inner = W_HALF - pad * 2

    def group(title: str, values: list[int], labels: list[str], top: int, hgt: int, delay: float) -> str:
        n = len(values)
        pitch = inner / n
        bar = min(22, pitch - 6)
        peak = max(values) or 1
        base_y = top + 22 + hgt
        out = [f'<text class="cap" x="{pad}" y="{top}">{esc(title)}</text>']
        for i, v in enumerate(values):
            x = pad + i * pitch + (pitch - bar) / 2
            bh = max(2, round(hgt * v / peak)) if v else 2
            y = base_y - bh
            out.append(
                f'<rect class="{"b" if v else "b z"}" x="{x:.1f}" y="{y}" width="{bar:.1f}" '
                f'height="{bh}" rx="2" style="animation-delay:{delay + i * 0.045:.3f}s">'
                f"<title>{v} · {labels[i]}</title></rect>"
            )
            out.append(
                f'<text class="ax" x="{x + bar / 2:.1f}" y="{base_y + 13}" '
                f'text-anchor="middle">{esc(labels[i])}</text>'
            )
            if v:
                out.append(
                    f'<text class="vv" x="{x + bar / 2:.1f}" y="{y - 5}" '
                    f'text-anchor="middle">{v}</text>'
                )
        out.append(f'<line class="base" x1="{pad}" y1="{base_y + 1}" x2="{W_HALF - pad}" y2="{base_y + 1}"/>')
        return "".join(out)

    body = group("por día de la semana", by_dow, WEEKDAYS, 22, 46, 0.20) + group(
        "por mes", by_month, MONTHS, 124, 36, 0.55
    )

    css = (
        ".cap{font-size:11px;fill:var(--dim);letter-spacing:.04em}"
        ".ax{font-size:9px;fill:var(--faint)}"
        ".vv{font-size:9px;font-weight:700;fill:var(--dim)}"
        ".base{stroke:var(--rule);stroke-width:1}"
        ".b{fill:var(--accent)}.b.z{fill:var(--rule)}"
        + anim(
            "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".b{{transform-box:fill-box;transform-origin:bottom;"
            f"animation:grow .5s cubic-bezier(.2,.8,.3,1);{PLAY_ONCE}}}"
            f".cap,.ax,.vv,.base{{animation:fade .6s .3s linear;{PLAY_ONCE}}}"
        )
    )
    write(
        "rhythm.svg",
        document(W_HALF, h, body, css, ("ui", "ui-bold"), title="Ritmo de actividad por día y por mes"),
    )

def langs(p: dict) -> None:
    h = H_HALF
    pad = 14
    inner = W_HALF - pad * 2
    top = p["languages"][:7]

    if not top:
        body = '<text class="cap" x="14" y="40">sin lenguajes públicos todavía</text>'
        write("langs.svg", document(W_HALF, h, body, ".cap{font-size:11px;fill:var(--dim)}"))
        return

    bar_y, bar_h = 36, 12
    x = pad
    segments = []
    total_pct = sum(l["pct"] for l in top) or 1
    for i, l in enumerate(top):
        w = inner * l["pct"] / total_pct
        segments.append(
            f'<rect class="sg" x="{x:.1f}" y="{bar_y}" width="{max(w - 1.5, 1):.1f}" '
            f'height="{bar_h}" rx="3" fill="{l["color"]}" '
            f'style="animation-delay:{0.25 + i * 0.09:.2f}s">'
            f'<title>{l["name"]} · {l["pct"]}%</title></rect>'
        )
        x += w

    rows = []
    row_y = 74
    for i, l in enumerate(top):
        y = row_y + i * 19
        rows.append(
            f'<g class="rw" style="animation-delay:{0.45 + i * 0.07:.2f}s">'
            f'<circle cx="{pad + 4}" cy="{y - 4}" r="4" fill="{l["color"]}"/>'
            f'<text class="nm" x="{pad + 16}" y="{y}">{esc(l["name"])}</text>'
            f'<text class="pc" x="{pad + 176}" y="{y}" text-anchor="end">{l["pct"]}%</text>'
            f'<text class="mt" x="{pad + 190}" y="{y}">'
            f'{l["bytes"] / 1024:.0f} KB · {l["repos"]} repo{"s" if l["repos"] != 1 else ""}</text>'
            f"</g>"
        )

    nrepos = max((l["repos"] for l in p["languages"]), default=0)
    body = (
        f'<text class="cap" x="{pad}" y="24">lenguajes</text>'
        f'<text class="ax" x="{W_HALF - pad}" y="24" text-anchor="end">'
        f"de los proyectos en los que he trabajado</text>"
        + "".join(segments)
        + "".join(rows)
        + f'<text class="ax" x="{pad}" y="{h - 12}">'
        f"peso del código de cada repo, no autoría de cada línea</text>"
    )

    css = (
        ".cap{font-size:11px;fill:var(--dim);letter-spacing:.04em}"
        ".ax{font-size:9px;fill:var(--faint)}"
        ".nm{font-size:12px;font-weight:700;fill:var(--ink)}"
        ".pc{font-size:11px;fill:var(--ink)}"
        ".mt{font-size:10px;fill:var(--faint)}"
        + anim(
            "@keyframes wipe{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
            "@keyframes rw{from{opacity:0;transform:translateX(-5px)}to{opacity:1;transform:none}}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".sg{{transform-box:fill-box;transform-origin:left;"
            f"animation:wipe .55s cubic-bezier(.2,.8,.3,1);{PLAY_ONCE}}}"
            f".rw{{animation:rw .5s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".cap,.ax{{animation:fade .5s .2s linear;{PLAY_ONCE}}}"
        )
    )
    write("langs.svg", document(W_HALF, h, body, css, ("ui", "ui-bold"), title="Lenguajes por bytes"))

def wrap(text: str, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > width and line:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines

def uni(p: dict, content: dict) -> None:
    entries = {e["repo"]: e for e in content.get("collaborations", [])}
    rows = [c for c in p.get("collaborations", []) if c["repo"] in entries]
    if not rows:
        return

    left_w, right_x = 560, 596
    bar_w = W_FULL - right_x
    desc_cols = int(left_w / (10.5 * 0.6))

    body: list[str] = []
    y = 24
    for i, c in enumerate(rows):
        meta = entries[c["repo"]]
        share = c["mine"] / c["total"] if c["total"] else 0
        delay = 0.2 + i * 0.1

        body.append(f'<g class="rw" style="animation-delay:{delay:.2f}s">')
        body.append(
            f'<text class="nm" x="0" y="{y}">'
            f'<tspan class="ow">{esc(c["owner"])}/</tspan>{esc(c["name"])}</text>'
        )
        body.append(f'<text class="st" x="0" y="{y + 16}">{esc(meta["stack"])}</text>')

        for j, line in enumerate(wrap(meta["what"], desc_cols)[:2]):
            body.append(f'<text class="ds" x="0" y="{y + 34 + j * 14}">{esc(line)}</text>')

        body.append(
            f'<rect class="tr" x="{right_x}" y="{y - 9}" width="{bar_w}" height="6" rx="3"/>'
            f'<rect class="fl" x="{right_x}" y="{y - 9}" width="{max(bar_w * share, 3):.1f}" '
            f'height="6" rx="3" style="animation-delay:{delay + 0.15:.2f}s"/>'
        )
        body.append(
            f'<text class="num" x="{right_x}" y="{y + 12}">'
            f'{c["mine"]} de {c["total"]} commits</text>'
        )
        body.append(
            f'<text class="sub" x="{right_x}" y="{y + 28}">'
            f'{c["people"]} personas · {human(c["from"])[-8:]} → {human(c["to"])[-8:]}</text>'
        )
        body.append("</g>")

        if i < len(rows) - 1:
            body.append(f'<line class="sep" x1="0" y1="{y + 56}" x2="{W_FULL}" y2="{y + 56}"/>')
        y += 76

    css = (
        ".nm{font-size:13px;font-weight:700;fill:var(--ink)}"
        ".ow{font-weight:400;fill:var(--faint)}"
        ".st{font-size:10px;fill:var(--accent);letter-spacing:.03em}"
        ".ds{font-size:10.5px;fill:var(--dim)}"
        ".num{font-size:10.5px;font-weight:700;fill:var(--ink)}"
        ".sub{font-size:9.5px;fill:var(--faint)}"
        ".tr{fill:var(--rule)}.fl{fill:var(--accent)}"
        ".sep{stroke:var(--rule);stroke-width:1}"
        + anim(
            "@keyframes rw{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
            "@keyframes gw{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
            "@keyframes fade{from{opacity:0}to{opacity:.999}}"
            f".rw{{animation:rw .55s cubic-bezier(.2,.7,.3,1);{PLAY_ONCE}}}"
            f".fl{{transform-box:fill-box;transform-origin:left;"
            f"animation:gw .6s cubic-bezier(.2,.8,.3,1);{PLAY_ONCE}}}"
            f".sep{{animation:fade .6s .5s linear;{PLAY_ONCE}}}"
        )
    )
    write(
        "universidad.svg",
        document(W_FULL, y - 12, "".join(body), css, ("ui", "ui-bold"),
                 title="Proyectos de carrera y participación en cada uno"),
    )

def stack(content: dict) -> None:
    items = content.get("stack", [])
    if not items:
        return

    fs, dot, pad_x, gap_x, gap_y, ph = 11.5, 5, 11, 7, 9, 25
    rows, line, x = [], [], 0.0
    for it in items:
        w = pad_x * 2 + dot + 7 + len(it["name"]) * fs * 0.6
        if line and x + w > W_FULL:
            rows.append(line)
            line, x = [], 0.0
        line.append((it, x, w))
        x += w + gap_x
    if line:
        rows.append(line)

    body, i = [], 0
    for r, line in enumerate(rows):
        used = sum(w for _, _, w in line) + gap_x * (len(line) - 1)
        off = (W_FULL - used) / 2
        y = r * (ph + gap_y)
        for it, lx, w in line:
            i += 1
            cx = off + lx
            body.append(
                f'<g class="pl" style="animation-delay:{0.15 + i * 0.028:.3f}s">'
                f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{ph}" rx="{ph / 2}" '
                f'fill="{it["color"]}" fill-opacity=".10" stroke="{it["color"]}" '
                f'stroke-opacity=".45"/>'
                f'<circle cx="{cx + pad_x + dot / 2:.1f}" cy="{y + ph / 2}" r="{dot / 2}" '
                f'fill="{it["color"]}"/>'
                f'<text class="tx" x="{cx + pad_x + dot + 7:.1f}" y="{y + ph / 2 + 4}">'
                f'{esc(it["name"])}</text></g>'
            )

    css = (
        f".tx{{font-size:{fs}px;fill:var(--ink)}}"
        + anim(
            "@keyframes pl{from{opacity:0;transform:translateY(5px) scale(.94)}"
            "to{opacity:1;transform:none}}"
            f".pl{{transform-box:fill-box;transform-origin:center;"
            f"animation:pl .45s cubic-bezier(.2,.8,.3,1.1);{PLAY_ONCE}}}"
        )
    )
    h = len(rows) * (ph + gap_y) - gap_y
    write(
        "stack.svg",
        document(W_FULL, h, "".join(body), css, ("ui",),
                 title="Tecnologías: " + ", ".join(i["name"] for i in items)),
    )


def main() -> int:
    if not DATA.exists():
        print("  data/profile.json missing -- run scripts/github_data.py first", file=sys.stderr)
        return 1
    p = json.loads(DATA.read_text(encoding="utf-8"))
    content = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

    heatmap(p)
    stats(p)
    rhythm(p)
    langs(p)
    uni(p, content)
    stack(content)

    n = len(p.get("collaborations", []))
    heading("stats", "stats", "generadas por este repo, cada noche")
    heading("year", "year", f'{p["window"]["from"]} → {p["window"]["to"]}')
    heading("work", "work", "lo que estoy construyendo")
    heading("universidad", "universidad", f"{n} proyectos" if n else "Deusto")
    heading("how", "how", "cómo se dibuja esta página")
    return 0

if __name__ == "__main__":
    sys.exit(main())

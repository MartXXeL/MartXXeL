
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / ".preview"

IMG = re.compile(r'<img\s+src="\./(?P<src>[^"]+)"\s+width="(?P<w>\d+)"[^>]*>')

PAGE = """<!doctype html><meta charset="utf-8">
<style>
  body{{margin:0;padding:32px 0;background:{bg};display:flex;justify-content:center}}
  main{{width:900px}}
  .row{{text-align:center;margin:16px 0;font-size:0}}
  .row img{{vertical-align:top;max-width:100%}}
  .row img + img{{margin-left:8px}}
  .gap{{height:26px}}
  .missing{{font-size:12px;color:#f85149;font-family:monospace;text-align:center;
            padding:20px;border:1px dashed #f85149;border-radius:6px}}
</style>
<main>{rows}</main>
"""

def rows_from_readme() -> list[list[tuple[str, int]]]:
    rows: list[list[tuple[str, int]]] = []
    for block in ROOT.joinpath("README.md").read_text(encoding="utf-8").split("\n\n"):
        found = [(m["src"], int(m["w"])) for m in IMG.finditer(block)]
        if found:
            rows.append(found)
    return rows

def build(theme: str) -> str:
    bg = "#0d1117" if theme == "dark" else "#ffffff"
    html = []
    for row in rows_from_readme():
        cells = []
        for src, w in row:
            path = ROOT / src
            if not path.exists():
                cells.append(f'<div class="missing">falta {src}</div>')
            else:
                cells.append(f'<img src="{path.as_uri()}" width="{w}">')
        html.append(f'<div class="row">{"".join(cells)}</div>')
        html.append('<div class="gap"></div>')
    return PAGE.format(bg=bg, rows="".join(html))

def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        for theme in ("dark", "light"):
            html = OUT / f"page-{theme}.html"
            html.write_text(build(theme), encoding="utf-8")
            page = browser.new_page(
                viewport={"width": 960, "height": 2900},
                device_scale_factor=1,
                color_scheme=theme,
            )
            page.goto(html.as_uri())
            page.wait_for_timeout(7000)
            page.screenshot(path=str(OUT / f"{theme}.png"))
            print(f"  .preview/{theme}.png")
            page.close()
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())

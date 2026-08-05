
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent

EXPECTED = ["img", "div", "sub", "samp", "details", "summary", "blockquote", "hr", "br"]

def render(md: str, token: str | None) -> str:
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": md, "mode": "markdown"}).encode(),
        headers={
            "User-Agent": "profile-generator/1.0",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")

def main() -> int:
    md = (ROOT / "README.md").read_text(encoding="utf-8")
    html = render(md, os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))

    problems = []

    src_in = re.findall(r'<img[^>]+src="\./([^"]+)"', md)
    src_out = re.findall(r"<img[^>]+src=\"[^\"]*?([^/\"]+\.svg)\"", html)
    missing = [s for s in src_in if s not in src_out]
    if missing:
        problems.append(f"imágenes que no sobrevivieron: {missing}")

    widths_in = len(re.findall(r"<img[^>]+width=", md))
    widths_out = len(re.findall(r"<img[^>]+width=", html))
    if widths_out < widths_in:
        problems.append(f"atributos width perdidos: {widths_in} enviados, {widths_out} devueltos")

    for tag in EXPECTED:
        if f"<{tag}" in md and f"<{tag}" not in html:
            problems.append(f"la etiqueta <{tag}> fue eliminada por el sanitizador")

    for s in set(src_in):
        if not (ROOT / s).exists():
            problems.append(f"referenciado pero no existe: {s}")

    print(f"  {len(set(src_in))} imágenes referenciadas, {len(set(src_out))} renderizadas")
    print(f"  {widths_in} atributos width enviados, {widths_out} conservados")
    print(f"  etiquetas presentes tras el sanitizador: "
          f"{', '.join(t for t in EXPECTED if f'<{t}' in html)}")

    if problems:
        print("\n  PROBLEMAS:", file=sys.stderr)
        for p in problems:
            print(f"    - {p}", file=sys.stderr)
        return 1

    print("  todo el marcado sobrevive al sanitizador de GitHub")
    return 0

if __name__ == "__main__":
    sys.exit(main())

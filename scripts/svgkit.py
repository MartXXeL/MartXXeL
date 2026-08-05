
from __future__ import annotations

import base64
import functools
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

CHAR_RATIO = 0.6

PALETTE = {
    "dark": {
        "ink": "#e6edf3",
        "dim": "#8b949e",
        "faint": "#484f58",
        "rule": "#30363d",
        "panel": "#161b22",
        "accent": "#39d353",
        "accent_dim": "#1f6f3f",
        "heat": ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "light": {
        "ink": "#1f2328",
        "dim": "#59636e",
        "faint": "#8c959f",
        "rule": "#d1d9e0",
        "panel": "#f6f8fa",
        "accent": "#1a7f37",
        "accent_dim": "#aceebb",
        "heat": ["#ebedf0", "#aceebb", "#4ac26b", "#2da44e", "#116329"],
    },
}

@functools.lru_cache(maxsize=None)
def font_face(slice_name: str, family: str = "JBM", weight: int = 400) -> str:
    data = (ASSETS / slice_name).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return (
        "@font-face{"
        f"font-family:'{family}';font-style:normal;font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
        "}"
    )

def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def theme_vars(extra: dict[str, dict[str, str]] | None = None) -> str:
    def block(theme: str) -> str:
        p = PALETTE[theme]
        decls = [f"--{k}:{v};" for k, v in p.items() if not isinstance(v, list)]
        decls += [f"--heat{i}:{c};" for i, c in enumerate(p["heat"])]
        if extra:
            decls += [f"--{k}:{v};" for k, v in extra.get(theme, {}).items()]
        return "".join(decls)

    return f":root{{{block('light')}}}" f"@media(prefers-color-scheme:dark){{:root{{{block('dark')}}}}}"

def document(
    width: int,
    height: int,
    body: str,
    css: str = "",
    fonts: tuple[str, ...] = ("ui",),
    title: str = "",
    extra_vars: dict[str, dict[str, str]] | None = None,
) -> str:
    faces = []
    for f in fonts:
        if f == "ui":
            faces.append(font_face("ui.woff2", "JBM", 400))
        elif f == "ui-bold":
            faces.append(font_face("ui-bold.woff2", "JBM", 700))
        elif f == "ramp":
            faces.append(font_face("ramp.woff2", "JBMRamp", 400))
        else:
            raise ValueError(f"unknown font slice: {f}")

    label = f"<title>{esc(title)}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{esc(title)}" font-family="JBM,ui-monospace,monospace">'
        f"{label}"
        f"<style>{''.join(faces)}{theme_vars(extra_vars)}{css}</style>"
        f"{body}"
        "</svg>"
    )

def write(name: str, svg: str) -> None:
    out = ROOT / name
    out.write_text(svg, encoding="utf-8")
    print(f"  {name:<16} {out.stat().st_size / 1024:6.1f} KB")

PLAY_ONCE = "animation-iteration-count:1;animation-fill-mode:both;"

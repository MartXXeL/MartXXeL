
from __future__ import annotations

import io
import pathlib
import sys
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CACHE = ROOT / ".cache"

VERSION = "2.304"
ZIP_URL = f"https://github.com/JetBrains/JetBrainsMono/releases/download/v{VERSION}/JetBrainsMono-{VERSION}.zip"

RAMP = " .`:-=+*cs#%@"

UI = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "·"
    + "—–"
    + "→←↑↓"
    + "─│┌┐└┘├┤┬┴┼"
    + "█▇▆▅▄▃▂▁"
    + "●○▸▪•"
    + "áéíóúüñÁÉÍÓÚÜÑ¿¡"
    + "°ºª€"
)

SLICES = [
    ("ramp.woff2", "JetBrainsMono-Regular.ttf", RAMP),
    ("ui.woff2", "JetBrainsMono-Regular.ttf", UI),
    ("ui-bold.woff2", "JetBrainsMono-Bold.ttf", UI),
]

def source_zip() -> zipfile.ZipFile:
    CACHE.mkdir(exist_ok=True)
    local = CACHE / f"JetBrainsMono-{VERSION}.zip"
    if not local.exists():
        print(f"  downloading {ZIP_URL}")
        with urllib.request.urlopen(ZIP_URL, timeout=120) as r:
            local.write_bytes(r.read())
    return zipfile.ZipFile(local)

def main() -> int:
    from fontTools import subset
    from fontTools.ttLib import TTFont

    ASSETS.mkdir(exist_ok=True)
    zf = source_zip()

    licence = next(n for n in zf.namelist() if n.upper().endswith("OFL.TXT"))
    (ASSETS / "OFL.txt").write_bytes(zf.read(licence))

    total = 0
    for out_name, ttf_name, text in SLICES:
        member = next(n for n in zf.namelist() if n.endswith(f"ttf/{ttf_name}"))
        font = TTFont(io.BytesIO(zf.read(member)))

        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = []
        opts.hinting = False
        opts.desubroutinize = True
        opts.name_IDs = ["*"]
        opts.notdef_outline = True

        subsetter = subset.Subsetter(options=opts)
        subsetter.populate(text=text)
        subsetter.subset(font)

        out = ASSETS / out_name
        font.flavor = "woff2"
        font.save(out)
        size = out.stat().st_size
        total += size
        print(f"  {out_name:<14} {len(set(text)):>4} glyphs  {size / 1024:6.1f} KB")

    print(f"  {'total':<14} {'':>4}         {total / 1024:6.1f} KB")
    return 0

if __name__ == "__main__":
    sys.exit(main())

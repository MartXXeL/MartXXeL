
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable

def run(*args: str) -> None:
    print(f"\n$ python {' '.join(args)}")
    r = subprocess.run([PY, *args], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="skip the API call")
    ap.add_argument("--portrait", type=pathlib.Path, help="rebuild the ASCII portrait from this photo")
    ap.add_argument("--fonts", action="store_true", help="rebuild the woff2 slices")
    ap.add_argument("--check", action="store_true", help="verify the markup against GitHub")
    args = ap.parse_args()

    if args.fonts:
        run("scripts/build_fonts.py")

    if args.portrait:
        # El dibujo es un coche, no una cara: se recorta a su silueta en vez de
        # cuadrar alrededor de una cabeza. Y 160 columnas, no 120: a 120 el
        # costado salía como un bloque macizo, y a 160 se separan los cristales,
        # las llantas y la línea de cintura.
        run("scripts/prep_photo.py", str(args.portrait),
            "--object", "--clahe", "2.0", "--size", "1500")
        prepped = ROOT / ".work" / f"{args.portrait.stem.replace(' ', '_')}.prep.png"
        run(
            "scripts/make_portrait.py", str(prepped),
            "--out", "portrait.svg", "--cols", "160", "--contrast", "1.35",
            "--title", "Mercedes-Benz 190E de perfil, dibujado carácter a carácter",
        )

    if not args.offline:
        run("scripts/github_data.py")

    run("scripts/render.py")
    run("scripts/make_identity.py")
    run("scripts/make_readme.py")

    if args.check:
        run("scripts/check_markdown.py")

    print("\nlisto. `python scripts/preview.py` para verlo en ambos temas.")
    return 0

if __name__ == "__main__":
    sys.exit(main())


from __future__ import annotations

import argparse
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK = ROOT / ".work"

HEAD_SCALE = 1.72
HEAD_RISE = 0.10

def find_face(bgr: np.ndarray) -> tuple[int, int, int, int] | None:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=6, minSize=(120, 120))
    if len(faces) == 0:
        return None
    return max(faces, key=lambda f: f[2] * f[3])

def square_crop(
    img: Image.Image,
    face: tuple[int, int, int, int] | None,
    head_scale: float = HEAD_SCALE,
    head_rise: float = HEAD_RISE,
) -> Image.Image:
    w, h = img.size
    if face is None:
        side = min(w, h)
        return img.crop(((w - side) // 2, 0, (w - side) // 2 + side, side))

    fx, fy, fw, fh = face
    side = int(max(fw, fh) * head_scale)
    cx = fx + fw / 2
    cy = fy + fh / 2 - fh * head_rise

    left = int(cx - side / 2)
    top = int(cy - side / 2)

    side = min(side, w, h)
    left = max(0, min(left, w - side))
    top = max(0, min(top, h - side))
    return img.crop((left, top, left + side, top + side))

def cutout(img: Image.Image) -> Image.Image:
    from rembg import remove

    return remove(img)

def object_crop(img: Image.Image) -> Image.Image:
    """Recorta a lo que quedó tras quitar el fondo, sin cuadrar.

    El recorte cuadrado de arriba está pensado para una cara. Un coche es
    apaisado: cuadrarlo le corta el morro o la cola, y el margen que sobra por
    arriba y por abajo se convierte en filas vacías."""
    box = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return img.crop(box) if box else img

def on_white(img: Image.Image) -> Image.Image:
    if img.mode != "RGBA":
        return img.convert("RGB")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, img).convert("RGB")

def local_contrast(img: Image.Image, clip: float = 3.0, grid: int = 6) -> Image.Image:
    lab = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid)).apply(l)
    return Image.fromarray(cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB))

def sharpen(img: Image.Image, amount: float = 1.2, radius: float = 3.0) -> Image.Image:
    from PIL import ImageFilter

    return img.filter(
        ImageFilter.UnsharpMask(radius=radius, percent=int(amount * 100), threshold=2)
    )

def prep(
    src: pathlib.Path,
    do_cutout: bool = True,
    size: int = 900,
    full_frame: bool = False,
    obj: bool = False,
    suffix: str = "prep",
    head_scale: float = HEAD_SCALE,
    head_rise: float = HEAD_RISE,
    clahe: float = 3.0,
) -> pathlib.Path:
    WORK.mkdir(exist_ok=True)
    img = Image.open(src)
    do_cutout = do_cutout and not full_frame
    img = img.convert("RGBA") if do_cutout else img.convert("RGB")

    if full_frame:
        print(f"  {src.name}: fotograma completo, sin recorte ni silueta")
    elif obj:
        img = object_crop(cutout(img))
        print(f"  {src.name}: silueta recortada a su caja, {img.size[0]}x{img.size[1]}")
    else:
        bgr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
        face = find_face(bgr)
        print(
            f"  {src.name}: "
            f"{'cara en ' + str(tuple(int(v) for v in face)) if face is not None else 'SIN CARA DETECTADA, recorte al centro'}"
        )
        if do_cutout:
            img = cutout(img)
        img = square_crop(img, face, head_scale, head_rise)

    mask = img.getchannel("A") if img.mode == "RGBA" else None
    keep_aspect = full_frame or obj
    target = (size, round(size * img.height / img.width)) if keep_aspect else (size, size)
    img = on_white(img).resize(target, Image.LANCZOS)
    img = local_contrast(img, clip=clahe)
    img = sharpen(img)

    if mask is not None:
        img = img.convert("RGBA")
        img.putalpha(mask.resize(target, Image.LANCZOS))

    out = WORK / f"{src.stem.replace(' ', '_')}.{suffix}.png"
    img.save(out)
    print(f"  -> {out.relative_to(ROOT)}  {img.size[0]}x{img.size[1]}")
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("photos", nargs="+", type=pathlib.Path)
    ap.add_argument("--no-cutout", action="store_true", help="deja el fondo dentro del dibujo")
    ap.add_argument("--full", action="store_true", help="foto entera: sin recorte ni silueta")
    ap.add_argument("--object", action="store_true", dest="obj",
                    help="silueta recortada a su caja, sin cuadrar: para lo que no es una cara")
    ap.add_argument("--head-scale", type=float, default=HEAD_SCALE,
                    help=f"cuánto se abre el recorte alrededor de la cara (def. {HEAD_SCALE})")
    ap.add_argument("--head-rise", type=float, default=HEAD_RISE)
    ap.add_argument("--clahe", type=float, default=3.0,
                    help="contraste adaptativo; bájalo si el fondo entra en el encuadre")
    ap.add_argument("--size", type=int, default=900)
    ap.add_argument("--suffix", default=None)
    args = ap.parse_args()

    suffix = args.suffix or ("full" if args.full else "prep")
    for photo in args.photos:
        if not photo.exists():
            print(f"  no existe: {photo}", file=sys.stderr)
            return 1
        prep(photo, do_cutout=not args.no_cutout, size=args.size,
             full_frame=args.full, obj=args.obj, suffix=suffix,
             head_scale=args.head_scale, head_rise=args.head_rise, clahe=args.clahe)
    return 0

if __name__ == "__main__":
    sys.exit(main())

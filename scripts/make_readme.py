
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent

W_FULL = 860
W_HALF = 426

def intrinsic_width(name: str, cap: int = W_FULL) -> int:
    import xml.etree.ElementTree as ET

    return min(int(float(ET.parse(ROOT / name).getroot().get("width"))), cap)

MEASURE = 76

def wrap(text: str) -> str:
    return "<br>\n".join(
        textwrap.wrap(
            " ".join(text.split()),
            MEASURE,
            break_on_hyphens=False,
            break_long_words=False,
        )
    )

def img(src: str, width: int, alt: str) -> str:
    return f'<img src="./{src}" width="{width}" alt="{alt}">'

def section(slug: str, alt: str) -> str:
    return img(f"h-{slug}.svg", W_FULL, alt)

def build(c: dict, p: dict) -> str:
    t = p["totals"]
    out: list[str] = []

    out.append(f'<div align="center">\n  {img("banner.svg", W_FULL, f"{c["name"]} — {c["tagline"]}")}\n</div>')

    out.append(section("whoami", "whoami"))
    out.append(
        f'<div align="center">\n  '
        f'{img("portrait.svg", intrinsic_width("portrait.svg"), f"Retrato ASCII de {c["name"]}")}\n</div>'
    )
    out.append(img("card.svg", W_FULL, f"Ficha de {c['name']}"))
    if (ROOT / "stack.svg").exists():
        out.append(img("stack.svg", W_FULL, "Tecnologías con las que he trabajado"))

    out.append(section("stats", "stats"))
    out.append(
        img("stats.svg", W_FULL, f'{t["year"]} contribuciones en los últimos doce meses')
    )
    out.append(
        f'<div align="center">\n  {img("rhythm.svg", W_HALF, "Actividad por día de la semana y por mes")} '
        f'{img("langs.svg", W_HALF, "Lenguajes por bytes")}\n</div>'
    )

    out.append(section("year", "year"))
    out.append(
        f'<div align="center">\n  '
        f'{img("heatmap.svg", W_FULL, f"Calendario de contribuciones, {t["year"]} en el último año")}\n</div>'
    )

    out.append(section("work", "work"))
    for proj in c["projects"]:
        block = [f'**{proj["name"]}** &nbsp;<sub>{proj["meta"]}</sub>', "", wrap(proj["what"])]
        if proj.get("why"):
            block += ["", "> " + wrap(proj["why"]).replace("<br>\n", "<br>\n> ")]
        out.append("\n".join(block))

    if p.get("collaborations"):
        out.append(section("universidad", "universidad"))
        out.append(
            "> "
            + wrap(
                "Casi todos son de otra gente: en la carrera se trabaja en equipo y el "
                "repositorio es de quien lo crea. Por eso de cada uno sale la única cifra "
                "honesta que se puede dar sobre el repositorio de otro — cuántos de los "
                "commits son míos."
            ).replace("<br>\n", "<br>\n> ")
        )
        out.append(img("universidad.svg", W_FULL, "Proyectos de carrera y participación en cada uno"))

    out.append(section("how", "how"))
    out.append(
        "> "
        + wrap(
            "Ninguna imagen de esta página viene de un servidor ajeno. Ni tarjetas de "
            "estadísticas, ni gráficos de actividad, ni la serpiente de contribuciones. "
            "Todo lo dibuja este mismo repositorio, cada noche, y se guarda aquí dentro."
        ).replace("<br>\n", "<br>\n> ")
    )
    out.append(
        wrap(
            "El motivo es prosaico: esas tarjetas se caen. Y aunque no se cayeran, no "
            "puedes diseñarlas — te dan la lista de temas de otro, y la página acaba "
            "pareciendo cinco páginas. Generarlas aquí cuesta un script y devuelve el "
            "control de cada píxel."
        )
    )
    out.append(
        "\n".join(
            [
                "<details>",
                "<summary>Cómo está hecho, por dentro</summary>",
                "",
                wrap(
                    "GitHub limpia el HTML del README: fuera <samp>&lt;style&gt;</samp>, "
                    "fuera <samp>style=\"\"</samp>, fuera <samp>&lt;svg&gt;</samp> en línea "
                    "y fuera cualquier script. Lo que no toca es el interior de un SVG "
                    "servido como imagen, porque es otro documento. Así que todo el estilo "
                    "y todo el movimiento viven ahí dentro."
                ),
                "",
                wrap(
                    "El retrato es una foto reducida a una rejilla de 90 columnas sobre una "
                    "rampa de trece caracteres. Cada fila se dibuja dentro de un "
                    "<samp>clipPath</samp> cuyo rectángulo crece de cero a su ancho en pasos "
                    "discretos, con un cursor cabalgando el borde; las filas se escalonan de "
                    "arriba abajo y todo termina con <samp>fill-mode: both</samp>, así que se "
                    "escribe una vez y se queda quieto. Nada en esta página hace bucle."
                ),
                "",
                wrap(
                    "Lleva dos rampas. La estándar convierte lo oscuro en caracteres densos: "
                    "correcto sobre fondo claro, y un negativo fotográfico sobre fondo "
                    "oscuro, que es como se está viendo en realidad la mayoría de retratos "
                    "ASCII de GitHub. Aquí se generan los dos mapeos y se conmutan con "
                    "<samp>prefers-color-scheme</samp>."
                ),
                "",
                wrap(
                    "La tipografía es JetBrains Mono incrustada en base64 dentro de cada "
                    "archivo. Una URL externa no funcionaría: los navegadores no cargan "
                    "subrecursos para documentos que son imágenes. Cada SVG lleva solo los "
                    "glifos que usa — trece caracteres para el retrato — y el total son 13 KB "
                    "en lugar de los 4,5 MB que costaría incrustar la fuente entera en cada uno."
                ),
                "",
                wrap(
                    "Las cifras salen de la API de GitHub con la ventana fijada a días UTC "
                    "completos. Sin eso, «el último año» se mide desde el instante de la "
                    "petición, dos ejecuciones separadas por minutos reparten los días en "
                    "semanas distintas, y acabas con un commit sin sentido cada noche."
                ),
                "</details>",
            ]
        )
    )

    stamp = dt.date.fromisoformat(p["window"]["to"])
    out.append("<hr>")
    out.append(
        f'<div align="center">\n'
        f'  <sub>Datos al {stamp.strftime("%d/%m/%Y")} · '
        f'regenerado cada noche por <samp>.github/workflows/refresh.yml</samp> · '
        f'sin dependencias de terceros</sub>\n'
        f"</div>"
    )

    return "\n\n".join(out) + "\n"

def main() -> int:
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    p = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    md = build(c, p)
    (ROOT / "README.md").write_text(md, encoding="utf-8")
    print(f"  README.md        {len(md.encode()) / 1024:6.1f} KB")
    return 0

if __name__ == "__main__":
    sys.exit(main())

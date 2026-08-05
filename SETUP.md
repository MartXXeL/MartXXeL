# Cómo publicarlo y cómo mantenerlo

Este repositorio genera tu propio README de perfil. No hace ninguna petición a
servidores de terceros: no hay tarjetas de estadísticas, ni gráfico de
actividad remoto, ni serpiente de contribuciones. Todo se dibuja aquí y se
guarda aquí.

---

## 1. Publicarlo

El repositorio tiene que llamarse **exactamente** igual que tu usuario de
GitHub — `MartXXeL` — para que GitHub lo trate como tu README de perfil.

> **Antes del push, activa esto:** en
> [github.com/settings/profile](https://github.com/settings/profile), sección
> *Contributions*, marca **Include private contributions on my profile**. Sin
> ese ajuste tus commits de Telescraperra —25 tuyos, hasta agosto de 2026— no
> aparecen en el calendario, porque el repositorio es privado. El script lee el
> mismo calendario público que ve cualquiera, así que los recogerá en cuanto lo
> marques.
>
> Los **porcentajes de lenguaje** son otra cosa y ese ajuste no los toca: la
> consulta filtra `privacy: PUBLIC` a propósito, porque el token de la Action
> tampoco ve repositorios privados y sin el filtro las cifras cambiarían según
> quién ejecutase el script. Por eso Python aparece al 11%: es solo el de
> Seguro-partes.

```bash
cd "c:/dev/Nueva carpeta"
git init -b main
git add .
git commit -m "perfil: primera versión"
git remote add origin https://github.com/MartXXeL/MartXXeL.git
git push -u origin main
```

Crea el repositorio en <https://github.com/new> antes del `push`, público y
**sin** README inicial (crearía un conflicto con el nuestro).

Dos cosas que no se pueden automatizar, porque no existe mutación de GraphQL ni
alcance de token que lo permita — se hacen a mano en la interfaz web:

- fijar los repositorios destacados (*pinned*)
- la biografía del perfil

Y una advertencia: **un README de perfil recién creado se queda cacheado**. Si
no aparece en tu perfil, edítalo una vez desde la web de GitHub y se refresca.

---

## 2. Qué se actualiza solo

`.github/workflows/refresh.yml` corre a las 05:17 UTC, recalcula las cifras,
redibuja los SVG de datos y hace commit **solo si algo cambió**.

No instala nada. Todo lo que ejecuta esa acción usa únicamente la biblioteca
estándar de Python — una tarea programada que hace `pip install` es una tarea
que un día falla por la publicación de otro.

> **No regeneres en local los archivos que gestiona la acción.** Tu token ve
> repositorios privados y el de la acción no, así que las cifras no coinciden
> exactamente y acabarás resolviendo conflictos de merge cada semana. Si
> quieres ver el resultado antes de subirlo, usa `preview.py` y luego descarta
> los cambios.

---

## 3. Qué se cambia a mano

### El texto

Todo el texto escrito vive en [`content.json`](content.json): la ficha de
identidad, el eslogan, los proyectos de carrera y sus descripciones. Edítalo y:

```bash
python scripts/build.py --offline
```

### Los proyectos de carrera

La lista está en `collaborations`, dentro de `content.json`. De cada uno se
escriben a mano el `stack` y la descripción; los commits, las fechas y los
lenguajes salen solos del historial de git.

Se leen de git y no de la API de GitHub por tres razones concretas:

- La API sin token da 60 peticiones a la hora, y a tres por repositorio se
  agotaban a mitad de ejecución, dejando proyectos fuera de la página.
- `pushed_at` no es «cuándo se trabajó en esto». Añadir un README a un trabajo
  de 2024 lo mueve a hoy, y la página pasaba a afirmar que el proyecto duró dos
  años más de lo que duró. Por eso el rango ignora los commits que solo tocan
  documentación.
- Los nombres de los contribuidores no son personas: la misma persona aparece
  como «Markel Bugallo» y «Markel Bugallo Gonzalez». Se agrupa por correo, y por
  eso hay una lista `identities` en `content.json` — si alguna vez firmaste con
  otro correo, añádelo o esos commits no contarán como tuyos.

Un clon `--bare --filter=blob:none` tarda un segundo y ocupa 250 KB para un
repositorio que pesa 45 MB descargado. Si la API está agotada pero quieres
refrescar solo esta parte:

```bash
python scripts/github_data.py --survey-only
```

Los lenguajes que se muestran son los de **todos** los repositorios en los que
has hecho algún commit, propios o no, descontando dependencias incrustadas —la
amalgama de SQLite dentro de DeustoShop son 9 MB de C que, contados, convertían
un perfil de carrera en un perfil de C. La tarjeta dice explícitamente que mide
el peso del código de cada repositorio, no la autoría de cada línea.

### El retrato

Solo cuando cambies de foto. Necesita las dependencias pesadas:

```bash
pip install -r requirements-tools.txt
python scripts/build.py --portrait "mi-foto.jpg"
```

La primera ejecución descarga un modelo de recorte de fondo de ~176 MB. Una
vez, y queda en caché.

**La foto decide el resultado**, mucho más que cualquier parámetro. El ASCII
dibuja con sombra, no con detalle: tiene trece niveles de brillo y nada más.

- Luz lateral. Una ventana a unos 45°, el resto apagado. La luz frontal plana
  deja la cara como un tono medio uniforme y se renderiza como un agujero.
- Encuadre cerrado, de la barbilla a justo por encima del pelo. El script
  recorta solo alrededor de la cara que detecta, pero no puede inventar
  resolución que la foto no tiene.
- 1200 px o más en el recorte de la cara. Con menos, los rasgos finos —la
  montura de unas gafas— se promedian y desaparecen al reducir.
- Fondo liso, y no vayas de negro contra una pared oscura.
- Ligeramente de perfil, no de frente: da sombra a la nariz y a la mandíbula.

#### El encuadre, y lo que cuesta cada uno

Se probaron cuatro y las diferencias son grandes. El que está montado es el
tercero:

| Encuadre | Tema oscuro | Tema claro |
| --- | --- | --- |
| Cara cerrada, fondo recortado | rasgos nítidos | rasgos nítidos |
| Busto, fondo recortado | bien | bien |
| **Busto, con fondo** ← montado | bien | figura más tenue |
| Foto entera, 160 col | se lee la escena, no la cara | ilegible |

La regla que salió de probarlo: **conservar el fondo cuesta el tema claro.**
Sin recorte de silueta, un fondo brillante (cielo, techo de cabina) mapea a
caracteres dispersos y la figura queda en un contorno pálido. En oscuro
aguanta; en claro se desdibuja. Si algún día prefieres que lea igual de bien en
los dos, quita `--no-cutout` y baja `--head-scale` a 1.7.

La receta exacta que está montada:

```bash
python scripts/prep_photo.py mi-foto.jpg \
    --no-cutout        # deja la cabina dentro del dibujo
    --head-scale 2.7   # cabeza y hombros, no solo la cara
    --clahe 1.6        # bajo a propósito: el contraste adaptativo que rescata
                       # una cara plana también convierte la pared en ruido

python scripts/make_portrait.py .work/mi-foto.prep.png --out portrait.svg \
    --cols 120         # más columnas para compensar el encuadre ancho
    --contrast 1.35    # despega la figura del fondo
    --gamma 0.80       # <1 oscurece: mete la cara en la parte densa de la rampa
```

O de una vez, con esos valores ya puestos:

```bash
python scripts/build.py --portrait "mi-foto.jpg"
```

### La tipografía

Ya está construida y commiteada. Solo si quieres cambiar de fuente:

```bash
python scripts/build_fonts.py
```

Tiene que ser una licencia OFL o similar, porque el archivo acaba en un
repositorio público: JetBrains Mono, IBM Plex Mono, Fira Code, Source Code Pro.
Las fuentes comerciales no valen. El archivo de licencia va al lado, en
`assets/OFL.txt`.

---

## 4. Ver el resultado antes de subirlo

```bash
python scripts/preview.py      # .preview/dark.png y .preview/light.png
python scripts/check_markdown.py
```

`check_markdown.py` manda el README a la API de renderizado de GitHub, que
aplica el mismo sanitizador que el sitio, y comprueba que no se haya caído
ninguna imagen ni ningún atributo `width`.

Una trampa al hacer capturas: **una captura de página completa reinicia las
animaciones** y te salen los SVG en blanco. `preview.py` usa un viewport alto
en lugar de `full_page`, y espera siete segundos a que todo termine de
dibujarse y se congele.

---

## 5. Qué hay en cada archivo

| Archivo | Qué hace |
| --- | --- |
| `content.json` | Todo el texto escrito a mano. Lo único que edita una persona. |
| `scripts/svgkit.py` | Paleta, fuente incrustada, andamiaje de los SVG. |
| `scripts/github_data.py` | Recoge las cifras. GraphQL con token, HTML público sin él. |
| `scripts/repo_stats.py` | Commits, fechas y lenguajes leídos del historial de git. |
| `scripts/render.py` | Calendario, estadísticas, ritmo, lenguajes y titulares. |
| `scripts/make_identity.py` | Cabecera y ficha *neofetch*. |
| `scripts/make_readme.py` | Compone el README con lo que GitHub no elimina. |
| `scripts/make_portrait.py` | Foto prepocesada → retrato ASCII animado. |
| `scripts/prep_photo.py` | Detecta la cara, recorta, quita fondo, sube contraste. |
| `scripts/build_fonts.py` | Corta JetBrains Mono en tres porciones woff2. |
| `scripts/check_markdown.py` | Verifica el marcado contra el sanitizador real. |
| `scripts/preview.py` | Capturas en tema claro y oscuro. |
| `scripts/build.py` | Ejecuta todo lo anterior en orden. |

<div align="center">
  <img src="./banner.svg" width="860" alt="Martxel Asteinza — Estudiante de ingeniería informática en la universidad de Deusto.">
</div>

<img src="./h-whoami.svg" width="860" alt="whoami">

<div align="center">
  <img src="./portrait.svg" width="860" alt="Retrato ASCII de Martxel Asteinza">
</div>

<img src="./card.svg" width="860" alt="Ficha de Martxel Asteinza">

<img src="./h-stats.svg" width="860" alt="stats">

<img src="./stats.svg" width="860" alt="95 contribuciones en los últimos doce meses">

<div align="center">
  <img src="./rhythm.svg" width="426" alt="Actividad por día de la semana y por mes"> <img src="./langs.svg" width="426" alt="Lenguajes por bytes">
</div>

<img src="./h-year.svg" width="860" alt="year">

<div align="center">
  <img src="./heatmap.svg" width="860" alt="Calendario de contribuciones, 95 en el último año">
</div>

<img src="./h-work.svg" width="860" alt="work">

**Telescraperra** &nbsp;<sub>python · playwright · gemini · privado</sub>

Bot de Telegram que detecta tips de apuestas en texto e imagen con un<br>
clasificador de visión, localiza cada partido en Winamax con Playwright +<br>
Camoufox, monta el cupón, lo valida con IA contra el aviso original y lo<br>
deja esperando un clic humano.

> Es el proyecto en el que aprendí que la parte difícil no era el scraping,<br>
> sino decidir qué hace el sistema cuando no está seguro.

<img src="./h-uni.svg" width="860" alt="uni">

> En la carrera se trabaja en equipo y el repositorio es de quien lo crea.<br>
> Aquí su muestran mis contribuciones en aquellos repositorios en los que <br>
> he trabajado.

<img src="./uni.svg" width="860" alt="Proyectos de carrera y participación en cada uno">

<img src="./h-how.svg" width="860" alt="how">

> Ninguna imagen de esta página viene de un servidor ajeno. Ni tarjetas de<br>
> estadísticas, ni gráficos de actividad, ni la serpiente de contribuciones.<br>
> Todo lo dibuja este mismo repositorio, cada noche, y se guarda aquí dentro.

El motivo es prosaico: esas tarjetas se caen. Y aunque no se cayeran, no<br>
puedes diseñarlas — te dan la lista de temas de otro, y la página acaba<br>
pareciendo cinco páginas. Generarlas aquí cuesta un script y devuelve el<br>
control de cada píxel.

<details>
<summary>Cómo está hecho, por dentro</summary>

GitHub limpia el HTML del README: fuera <samp>&lt;style&gt;</samp>, fuera<br>
<samp>style=""</samp>, fuera <samp>&lt;svg&gt;</samp> en línea y fuera<br>
cualquier script. Lo que no toca es el interior de un SVG servido como<br>
imagen, porque es otro documento. Así que todo el estilo y todo el<br>
movimiento viven ahí dentro.

El retrato es una foto reducida a una rejilla de 90 columnas sobre una rampa<br>
de trece caracteres. Cada fila se dibuja dentro de un <samp>clipPath</samp><br>
cuyo rectángulo crece de cero a su ancho en pasos discretos, con un cursor<br>
cabalgando el borde; las filas se escalonan de arriba abajo y todo termina<br>
con <samp>fill-mode: both</samp>, así que se escribe una vez y se queda<br>
quieto. Nada en esta página hace bucle.

Lleva dos rampas. La estándar convierte lo oscuro en caracteres densos:<br>
correcto sobre fondo claro, y un negativo fotográfico sobre fondo oscuro,<br>
que es como se está viendo en realidad la mayoría de retratos ASCII de<br>
GitHub. Aquí se generan los dos mapeos y se conmutan con<br>
<samp>prefers-color-scheme</samp>.

La tipografía es JetBrains Mono incrustada en base64 dentro de cada archivo.<br>
Una URL externa no funcionaría: los navegadores no cargan subrecursos para<br>
documentos que son imágenes. Cada SVG lleva solo los glifos que usa — trece<br>
caracteres para el retrato — y el total son 13 KB en lugar de los 4,5 MB que<br>
costaría incrustar la fuente entera en cada uno.

Las cifras salen de la API de GitHub con la ventana fijada a días UTC<br>
completos. Sin eso, «el último año» se mide desde el instante de la<br>
petición, dos ejecuciones separadas por minutos reparten los días en semanas<br>
distintas, y acabas con un commit sin sentido cada noche.
</details>

<hr>

<div align="center">
  <sub>Datos al 05/08/2026 · regenerado cada noche por <samp>.github/workflows/refresh.yml</samp> · sin dependencias de terceros</sub>
</div>

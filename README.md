<div align="center">
  <img src="./banner.svg" width="860" alt="Martxel Asteinza — Estudiante de Ingeniería Informática en la Universidad de Deusto.">
</div>

<div align="center">
  <img src="./portrait.svg" width="860" alt="Mercedes-Benz 190E de perfil, dibujado en ASCII">
</div>

<img src="./card.svg" width="860" alt="Ficha de Martxel Asteinza">

<img src="./stack.svg" width="860" alt="Tecnologías con las que he trabajado">

<img src="./h-stats.svg" width="860" alt="stats">

<img src="./stats.svg" width="860" alt="219 contribuciones en los últimos doce meses">

<div align="center">
  <img src="./rhythm.svg" width="426" alt="Actividad por día de la semana y por mes"> <img src="./langs.svg" width="426" alt="Lenguajes por bytes">
</div>

<img src="./h-year.svg" width="860" alt="year">

<div align="center">
  <img src="./heatmap.svg" width="860" alt="Calendario de contribuciones, 219 en el último año">
</div>

<img src="./h-work.svg" width="860" alt="work">

**Telescraperra** &nbsp;<sub>python · playwright · gemini · privado</sub>

Bot de Telegram que detecta tips de apuestas en texto e imagen con un<br>
clasificador de visión, localiza cada partido en Winamax con Playwright +<br>
Camoufox, monta el cupón, lo valida con IA contra el aviso original y lo<br>
deja esperando un clic humano.

> Es el proyecto en el que aprendí que la parte difícil no era el scraping,<br>
> sino decidir qué hace el sistema cuando no está seguro.

> **TelegramBot** &nbsp;<sub>python · telethon · gemini · sqlite</sub><br>

> La primera parte de Telescraperra, y la única pública: escucha los grupos<br>
> seleccionados y manda cada mensaje entero —texto, captura o ambos— al<br>
> clasificador de visión, que decide él solo si hay un tip que todavía se<br>
> puede jugar. Lo que encuentra lo guarda en SQLite y lo avisa por un bot de<br>
> Telegram.

**ActionPrufe** &nbsp;<sub>python · playwright · gemini · mit</sub>

Librería que comprueba que cada acción de navegador hizo lo que pretendía.<br>
Compara el estado semántico de la página antes y después, y si el efecto no<br>
corresponde al elemento sobre el que se actuó, lo deshace y reintenta; si no<br>
puede deshacerlo, aborta en vez de seguir operando sobre una página que ya<br>
no es la que se creía.

> En una lista virtualizada, React recicla el nodo<br>
> entre que lo localizas y lo clicas, así que el clic no<br>
> da error y aun así añade otra cosa. Los healer agents reparan selectores<br>
> rotos; esto persigue el fallo contrario, el que no rompe nada.

<img src="./h-universidad.svg" width="860" alt="universidad">

<img src="./universidad.svg" width="860" alt="Proyectos de carrera y participación en cada uno">

<img src="./h-how.svg" width="860" alt="how">

<details>
<summary>Cómo está hecho, por dentro</summary>

GitHub limpia el HTML del README: fuera <samp>&lt;style&gt;</samp>, fuera<br>
<samp>style=""</samp>, fuera <samp>&lt;svg&gt;</samp> en línea y fuera<br>
cualquier script. Lo que no toca es el interior de un SVG servido como<br>
imagen, porque es otro documento. Así que todo el estilo y todo el<br>
movimiento viven ahí dentro.

El coche es una foto reducida a una rejilla de 160 columnas sobre una rampa<br>
de trece caracteres. Cada fila se dibuja dentro de un <samp>clipPath</samp><br>
cuyo rectángulo crece de cero a su ancho en pasos discretos, con un cursor<br>
cabalgando el borde; las filas se escalonan de arriba abajo y todo termina<br>
con <samp>fill-mode: both</samp>, así que se escribe una vez y se queda<br>
quieto. Nada en esta página hace bucle.

La foto de la que sale es [un 190E 2.6 de 1987](https://commons.wikimedia.org/wiki/File:1987_Mercedes_Benz_190_E_(W201)_2.6_sedan_(24084486981).jpg)<br>
de Jeremy, de Sídney, [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) vía Wikimedia Commons. Está en<br>
<samp>assets/portrait-source.jpg</samp>, y el dibujo se rehace con<br>
<samp>python scripts/build.py --portrait assets/portrait-source.jpg</samp>.

Lleva dos rampas. La estándar convierte lo oscuro en caracteres densos:<br>
correcto sobre fondo claro, y un negativo fotográfico sobre fondo oscuro,<br>
que es como se está viendo en realidad la mayoría de retratos ASCII de<br>
GitHub. Aquí se generan los dos mapeos y se conmutan con<br>
<samp>prefers-color-scheme</samp>.

La tipografía es JetBrains Mono incrustada en base64 dentro de cada archivo.<br>
Una URL externa no funcionaría: los navegadores no cargan subrecursos para<br>
documentos que son imágenes. Cada SVG lleva solo los glifos que usa — trece<br>
caracteres para el coche — y el total son 13 KB en lugar de los 4,5 MB que<br>
costaría incrustar la fuente entera en cada uno.

Las cifras salen de la API de GitHub con la ventana fijada a días UTC<br>
completos. Sin eso, «el último año» se mide desde el instante de la<br>
petición, dos ejecuciones separadas por minutos reparten los días en semanas<br>
distintas, y acabas con un commit sin sentido cada noche.
</details>

<hr>

<div align="center">
  <sub>Datos al 21/08/2026 · regenerado cada noche por <samp>.github/workflows/refresh.yml</samp> · sin dependencias de terceros</sub>
</div>

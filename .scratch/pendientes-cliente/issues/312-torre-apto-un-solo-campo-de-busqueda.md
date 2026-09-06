# 312 — Torre/Apto reusa el ÚNICO campo `q` (ya no un segundo input dentro del dropdown)

**Pedido original (cliente):** tras la reubicación de issue 311 (ícono dentro del campo), lo
que aparecía al presionar el ícono seguía siendo un SEGUNDO campo de texto (el input propio de
`picker_apartamento()`) dentro del dropdown -- "la barra de búsqueda es una y esta debe ser la
que reciba el número del apartamento [...] lo que está apareciendo es otra barra de búsqueda
para ingresar nuevamente el apartamento". Pidió además cuidar el debounce para que los íconos
no aparezcan/desaparezcan mientras se sigue escribiendo.

**Status:** removido -- ver issue 309, el cliente pidió deshacer toda la búsqueda por Torre/Apto
después de esta 3ra ronda de UI.

## Cómo se resolvió

`picker_apartamento()` (`_picker_apartamento.html`) gana `mostrar_input=False`: apaga su
`<input>` propio -- el resto del macro (catálogo JSON, grid "¿Cuál Torre?", hidden fields) no
cambia. El listener `input` delegado de `recursos_recibir()` no le importa DÓNDE vive el
elemento con `data-picker-apartamento="{{ prefix }}"`, solo que exista -- así que
`_busqueda_filtros.html` le agrega/quita ese atributo al propio campo `q` mientras dura la
selección (`torreAptoArmarQ`/`torreAptoDesarmarQ` en el JS), reusando el mismo mecanismo que ya
usan Recibir/Asignar apartamento sin duplicar ninguna lógica.

Mientras el modo "elegir Torre/Apto" está armado, `q` dejó de comportarse como texto libre --
`actualizar()` no manda `q` como búsqueda mientras tenga el atributo puesto (evita que dígitos a
medio escribir del apartamento disparen una búsqueda de texto real). Al elegir una Torre, `q`
muestra "Torre X · Apto Y" (deshabilitado) en vez de quedar vacío -- el staff ve qué unidad está
filtrando sin tener que reabrir el dropdown.

"Quitar filtros" limpia SIEMPRE la selección de Torre/Apto (antes solo lo hacía si el panel
seguía visible -- ya no aplica, una vez confirmada la unidad el panel se cierra solo).

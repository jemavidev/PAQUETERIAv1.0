# 320 — Filtro "Sin apartamento asignado" + botón para asignar desde la lista

**Pedido original (cliente):** agregar un botón para filtrar residentes sin apartamento en
`/residentes`, y que cada residente sin apartamento tenga OTRO botón adicional que permita
asociarle uno directo desde ahí. Pidió sugerencia de diseño que se vea consistente con el resto
del aplicativo.

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-05, commit `bcac30d`) --
pendiente que el cliente lo confirme visualmente (extensión de Chrome no disponible en esta
sesión). Verificado contra el servidor real (residente de prueba insertado y eliminado en la
misma verificación) y 8 tests nuevos, suite completa en verde.

## Diseño (mensaje al cliente antes de implementar)

Ambas piezas reusan infraestructura YA existente en el aplicativo, sin inventar nada nuevo:

- **Filtro "Sin apartamento asignado"**: 3ra vista junto a "Principales"/"Agrupado"
  (`filtro_vista_residentes()`), mismo mecanismo de toggle-al-reclick. Color gris intenso
  (`slate-600`/`800`) -- 3ra familia de color bien distinta de ámbar/azul, evoca "dato faltante"
  sin pisar el gris MÁS pálido que ya usan los íconos apagados (issue 315).
- **Botón "Asignar apartamento" por fila**: 6to espacio SIEMPRE presente en la columna Acciones
  (mismo criterio "siempre los mismos espacios" de issue 315) -- activo solo para quien no tiene
  apartamento, apagado para quien ya tiene uno (se cambia desde la ficha, pestaña "Dirección").
  Abre un modal con el MISMO picker de número->Torre que "Recibir"/"Asignar apartamento" de
  `/paquetes`, posteando a la ruta YA existente y probada de la ficha
  (`/residentes/{id}/apartamento`) -- CERO lógica de backend nueva, sin duplicar la lógica de
  reasignación/conflictos que esa ruta ya maneja.

## Implementación

- `_listar_sin_apartamento`/`_buscar_sin_apartamento` (customers_manage.py) -- mismo patrón que
  `_listar_principales`/`_buscar_principales` (filtro a nivel de BD antes de paginar).
- `search.html` reemplaza su `<script>` propio (gateado a ADMIN, solo servía al modal "Eliminar
  residente") por `{{ recursos_recibir() }}` -- ya trae el mismo toggle genérico `data-open`/
  `data-close` SIN gate de rol (el modal nuevo es para cualquier staff), más el JS del picker que
  el modal nuevo necesita. Mismo patrón que ya usa `customers_manage/detail.html` para su pestaña
  "Dirección" -- no es un uso nuevo de `recursos_recibir()`, es el mismo de siempre aplicado a
  esta 2da plantilla.
- Modal simplificado respecto al de `/paquetes`: sin "+ Nuevo residente" (acá `p` ya es una
  Persona real) ni el checkbox "mover de otra unidad" (quien no tiene `apartamento_actual_id` no
  puede a la vez ser Ocupante activo de otra unidad -- el sistema mantiene ese campo sincronizado
  con el padrón real; el caso raro de conflicto lo resuelve igual la ruta mostrando el error en
  la ficha).

## Bug encontrado en el camino (no relacionado al pedido)

Un comentario de Jinja (`{# ... #}`) colocado DENTRO de la expresión `{% set vistas = {...} %}`
rompe el parser (`unexpected char '#'`) -- Jinja no permite comentarios anidados dentro de un tag
de expresión. Se movió el comentario afuera, antes del `{% set %}`. Detectado por un 500 al
probar contra el servidor real (reproducido con un test aislado antes de diagnosticar, ver
disciplina de `diagnosing-bugs`).

## Colisión con tests preexistentes (issue 317)

El nuevo botón de filtro usa "Sin apartamento asignado" como `title`/`aria-label` -- la MISMA
frase que ya usaba el encabezado `<h3>` de la sección "leftover" del modo "agrupado" general
(issue 174). 2 tests de issue 317 que buscaban esa frase suelta en todo el HTML dejaron de ser
precisos (el botón nuevo, SIEMPRE presente en la página, la vuelve trivialmente cierta). Corregidos
para buscar `"Sin apartamento asignado</h3>"` (el cierre de la etiqueta específica), no la frase
sola -- uno de los dos (`test_agrupar_por_numero_exacto_nunca_muestra_sin_apartamento`) directamente
FALLABA con el cambio; el otro (`test_agrupar_por_apartamento_incluye_sin_apartamento_asignado`)
seguía pasando pero había dejado de probar lo que decía probar.

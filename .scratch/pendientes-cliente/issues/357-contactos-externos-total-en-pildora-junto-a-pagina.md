# 357 — `/administracion/contactos-externos`: el total de contactos va en una píldora, a la derecha de "Página X de Y"

**Pedido original (Jesús):** "Necesito que la cantidad de contactos '1041
contactos' lo permitas visualizar en una pildora, esta deberia estar
solamente al lado de por ejemplo la parte donde dice 'Página 1 de 53',
recuerda la pildora debera quedar del lado derecho, todo esto solamente para
la vista /administracion/contactos-externos."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Contexto

Issue 338 puso el total como texto suelto ("1041 contactos") en un `<p>`
sobre la barra de paginación. `components/_paginacion.html` es compartido con
`/paquetes` y `/residentes`, y no renderiza nada con `total_paginas <= 1`.

## Decisiones

- `paginacion()` recibe un parámetro opcional `pildora` (default `none`): si
  viene, la barra desktop la dibuja pegada a la derecha de "Página X de Y".
  Sin el parámetro, `/paquetes` y `/residentes` quedan idénticas.
- El texto suelto de 338 desaparece de la posición de arriba. El total sigue
  visible (regla de 338) donde la barra desktop no aparece: con 1 sola
  página, y en mobile -- ahí como la MISMA píldora, en su propia fila a la
  derecha, porque la barra flotante mobile es demasiado angosta para
  sumarle una píldora.

## Implementación

- `components/_paginacion.html`: macro nuevo `pildora_paginacion(texto,
  clases)` y parámetro opcional `pildora` en `paginacion()`; la barra desktop
  la dibuja tras "Página X de Y" (`ml-2`). Pill neutra gris (dato, no estado).
- `admin/_contactos_externos_resultados.html`: pasa `pildora=etiqueta_total`
  y dibuja la misma píldora suelta a la derecha (`flex justify-end`): siempre
  con 1 sola página, y con `md:hidden` cuando hay barra.
- Interpretación del pedido: "al lado de 'Página X de Y', del lado derecho" =
  inmediatamente a la derecha de ese texto (no en el extremo derecho de la
  barra, después de "Siguiente"). Si se quiso lo segundo, es mover una línea.

## Verificación

- 6 tests nuevos en `tests/web/test_admin_contactos_externos.py` (dentro de la
  barra con 21 contactos; suelta y `md:hidden` en mobile; sin `md:hidden` con
  1 página; ya no hay `<p>` de 338; "encontrado(s)" con búsqueda; el macro
  sin `pildora` no dibuja ninguna).
- Tests de paginación de `/residentes` y `/paquetes` siguen verdes.
- En vivo: "Página 1 de 53" seguido de la píldora "1041 contactos".

## Ronda 2

**Pedido (Jesús):** "La pildora deberia ser un poco mas grande '1041
contactos'". **Status de la ronda:** implementada

Antes: `px-3 py-0.5 text-xs`. Se sube el tamaño de `pildora_paginacion()` (la
misma para la barra desktop y para la píldora suelta de mobile/1 página).

Ahora: `px-3.5 py-1 text-sm` (30px de alto, dentro de los 32px de los botones
de la barra, que no se ensancha) + `align-middle` dentro de la barra. Test:
`test_la_pildora_del_total_es_text_sm`. `tailwind.css` no cambió (todas las
clases ya estaban compiladas), sin nuevo `?v=`. En vivo: la barra sirve
"Página 1 de 53" + píldora "1041 contactos" con esas clases.

## Ronda 3

**Pedido (Jesús):** "se ve mucho mejor, por ultimo ajusta la pildora con la
cantidad de contactos para que este centrada y ajustada al contenido que
tiene a los lados". **Status de la ronda:** implementada

Medido con Playwright/Chromium contra `localhost:8010` (1280px): la píldora
medía 30px y los botones Anterior/Siguiente 32px; y el texto "Página 1 de 53"
quedaba 1.3px más arriba (centro y=272.7) que la píldora y los botones
(y=274), porque la píldora iba inline con `align-middle` (alinea contra la
línea base del texto, no contra el centro).

Interpretación del pedido: "centrada" = mismo eje vertical que lo que la
rodea; "ajustada al contenido que tiene a los lados" = misma altura que los
botones Anterior/Siguiente que la flanquean. Si se quiso otra cosa (ej.
centrado horizontal exacto en la barra), es un cambio aparte.

- `components/_paginacion.html`: con `pildora`, el centro de la barra es una
  fila `flex items-center justify-center gap-2` ("Página X de Y" en su propio
  `<span>` + la píldora); `pildora_paginacion()` pasa de `py-1` a `h-8` con
  `justify-center` (texto centrado). Sin `pildora`, mismo HTML de siempre
  salvo una línea en blanco entre el botón y el texto (comparado contra
  `HEAD`; sin efecto visual).
- Resultado medido: Anterior, píldora y Siguiente `y=258 h=32 cy=274`, el
  texto también `cy=274`. A 768px igual, sin overflow; en mobile (375px) la
  píldora suelta mide 32px, a la derecha, sin overflow.
- Tests: `test_la_pildora_del_total_es_text_sm_y_del_alto_de_los_botones` y
  `test_en_la_barra_el_texto_de_pagina_y_la_pildora_comparten_eje_vertical`;
  el de la barra ajustado a la estructura nueva. `tailwind.css` sin cambios.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado (ronda 3), pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

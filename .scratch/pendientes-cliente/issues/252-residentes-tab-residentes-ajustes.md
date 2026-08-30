# 252 — `/residentes/{id}` tab Residentes: tanda de 7 ajustes

**Pedido original (cliente):**

1. El botón de la tab dice "&lt;Torre y Apartamento&gt;" en vez de "Residentes".
2. Reemplazar "⭐ Residente principal" por solo "⭐" (dentro de la misma
   píldora, ~30% más grande que los demás íconos/emojis) -- la píldora
   azul de cabecera ya dice si es o no el Principal.
3. Agregar "✏️ Editar" y "🔔 Notificaciones" también para el residente
   Principal, misma lógica que ya manejan esos enlaces.
4. Resaltar de alguna forma cuál residente de la lista es la ficha que se
   tiene seleccionada/abierta.
5. Quitar el texto "Si la persona ya tiene su propia ficha, escribí su
   teléfono o WhatsApp para sumarla acá (en vez de crear un registro
   nuevo)."
6. "Agregar un nuevo Residente" -> "Agregar Residente".
7. "Residentes del apartamento" -> "Residentes &lt;Torre y Apartamento&gt;".

**Status:** implementado

## Implementación

1. `_etiqueta_tab_residentes` eliminada (`customers_manage.py`) -- el
   botón de la tab ahora siempre dice "Residentes" (texto fijo en el
   template), sin importar si hay Apartamento asignado.
2. `badge_ocupante` (`_badge.html`) gana el parámetro opcional
   `tam_texto` (default `text-[11px]`) -- la fila de Principal en
   `/residentes` pasa `texto='⭐'` y `tam_texto='text-[14px]'` (~30% más
   grande). `/mis-datos` no se tocó (el pedido era solo para
   `/residentes`).
3. El bloque de acciones (Promover/Editar/Notificaciones) ya no está
   gateado por `{% if not o.es_principal %}` completo -- ahora ese `if`
   envuelve SOLO el botón "⭐ Promover" (y su modal de confirmación);
   Editar y Notificaciones quedan bajo `{% if o.persona_id %}`, aplicando
   a cualquier residente con contacto propio, principal o no.
4. Un `ring-2 ring-indigo-400 ring-offset-1` en la tarjeta, más
   "(ficha actual)" junto al nombre, cuando `o.persona_id == persona.id`
   -- señal distinta del borde/fondo azul de "es Principal" (las dos
   pueden coexistir en la misma fila).
5. Texto (issue 157) retirado del formulario "Agregar Residente"; el test
   que solo verificaba su presencia (`test_ficha_form_agregar_residente_
   explica_que_contacto_suma_a_alguien_existente`) se eliminó.
6. "Agregar un nuevo Residente" -> "Agregar Residente".
7. `<h3>` interpola `apartamento.torre|torre_sin_prefijo` +
   `apartamento.apartamento`, mismo formato "TORRE N APT M" que ya usa el
   modal "Mudarse" de `/mis-datos` (issues 240/241).

6 tests nuevos/actualizados cubriendo los 7 puntos.

## Seguimiento: reposición + tamaño de la estrella

El cliente, tras ver el resultado en vivo, pidió dos ajustes más:

- "✏️ Editar" y "🔔 Notificaciones" pasan de la fila de abajo (donde
  vivían junto a "⭐ Promover") a la fila de ARRIBA, junto al badge
  (⭐/Confirmado/Pendiente) -- mismo slot donde el no-Principal ya tenía
  Confirmar/Rechazar-Eliminar. El modal de Editar se factorizó a un solo
  lugar en el markup (antes hubiera quedado duplicado entre la rama
  Principal y no-Principal); "⭐ Promover" se queda solo, abajo, exclusivo
  de no-Principal.
- La estrella baja de ~30% (`text-[14px]`) a ~15% más grande
  (`text-[13px]`) que el resto de íconos/emoji de la fila (11px).

139 tests en verde, verificado en vivo por curl: el HTML confirma que
"✏️ Editar"/"🔔 Notificaciones" ahora están en el mismo `<div>` que la
estrella `text-[13px]`.

## Seguimiento: quitar el texto "(ficha actual)"

El cliente pidió quitar el texto "(ficha actual)" que acompañaba al
`ring` índigo (punto 4). El `ring-2 ring-indigo-400` en la tarjeta se
queda igual -- solo se retira el texto junto al nombre.

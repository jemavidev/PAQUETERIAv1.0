# 250 — `/residentes/{id}`: quitar el acento rojo de "Secundario"

**Pedido original (cliente):** "Ya que sé cuál es principal y cuál no,
necesito que remuevas esta barra roja que aparece al lado izquierdo
'tab-panel border-l-4 border-red-400 pl-3'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Seguimiento: "Volver a Residentes" más visible/funcional

El cliente preguntó cómo hacer más visible/funcional el link de volver
(hoy solo un ícono con `aria-label`, sin texto visible). Prototipado en
vivo sobre la propia ruta (`?variant=a-f`, patrón ya usado en issue 200)
con 6 variantes -- decisión final del cliente: "🏠 Residentes" como link
de vuelta, seguido de "- <Nombre>" en texto plano, todo en un solo H1.

Implementado: `customers_manage/detail.html` ya no usa
`encabezado_volver` (components/_breadcrumbs.html) para este título --
el link "🏠 Residentes" es parte del texto del H1, no un ícono aparte
compuesto por el macro. El macro se deja intacto (componente de design
system documentado, sin otro llamador hoy, pero no es código muerto
ad-hoc). Bloque de prototipo (6 variantes + switcher flotante) retirado
por completo tras la decisión.

## Alcance

`customers_manage/detail.html` -- el acento rojo (`border-l-4 border-red-
400`, issue 71) era la señal de "Secundario" en las 4 tabs, desde que ese
estado dejó de llevar badge (issue 69). Con el badge "Principal" ya
siempre visible en la cabecera cuando aplica (issue 244/248/249), el
cliente ya tiene la información sin necesitar el acento -- se retira de
las 4 tabs (Datos/Dirección/Notificaciones/Residentes) y se elimina la
variable `es_secundario`, que queda sin ningún otro uso.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

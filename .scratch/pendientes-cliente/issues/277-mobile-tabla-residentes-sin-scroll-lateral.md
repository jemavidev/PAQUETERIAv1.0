# 277 — `/residentes` lista (tabla plana), mobile: quitar scroll lateral

**Pedido original (cliente):** "ahora para la vista de /residentes necesito
que en la opción de dispositivos móviles remuevas la columna Teléfono de
contacto, adicional de que forma se podría comprimir Torre y Apartamento,
la idea de esto es que en una sola línea no sea necesario hacer scroll
lateral y que se pueda tener acceso a los iconos de acción"

**Status:** verificado (desplegado y confirmado en test.papyrus.com.co)

## Alcance

`customers_manage/_resultados.html` — la tabla plana de resultados (la
vista `agrupado`/tarjetas no tiene esta columna, no aplica). Cambios
SOLO visibles en mobile (breakpoint `sm`, 640px, mismo que ya usan issues
264/265 en este archivo) — desktop no cambia:

1. Columna "Teléfono de contacto" (`<th>`+`<td>`): `hidden sm:table-cell`
   — desaparece por completo en mobile, sigue igual en `sm:` en adelante.
2. Columna "Torre y Apartamento": nuevo parámetro `compacto=True` en
   `_etiqueta_torre_apto` (`customers_manage.py`) — mobile muestra
   "T05-302" en vez de "T 05 - APT 302" (~7 vs ~14 caracteres), vía dos
   `<span>` (`sm:hidden` / `hidden sm:inline`) que alternan formato
   completo vs compacto según viewport. Fallback sin apartamento también
   se acorta ("No Asig." vs "No Asignado") en la variante mobile.
3. Padding horizontal de celdas (`px-4` → `px-2 sm:px-4`) en las 3
   columnas que quedan visibles en mobile (Nombre, Torre y Apartamento,
   Acciones) — recupera ancho extra hacia el mismo objetivo (evitar
   scroll lateral, mantener Acciones alcanzable).

Verificado en vivo (dev local, iframe angosto de 359px de ancho útil
inyectado en la página real -- `resize_window` de la automatización de
browser no reproduce un viewport angosto en este entorno, ver issues
274/275; un iframe same-origin sí evalúa los media queries `sm:` contra
SU PROPIO ancho) que con solo los 2 cambios de arriba TODAVÍA sobraban
~101px de scroll -- el nombre completo (`whitespace-nowrap`) y los 4
íconos de Acciones por sí solos ya ocupaban casi todo el ancho. Se
agregaron 3 ajustes más, todos exclusivos de mobile (`sm:` en adelante
vuelve exactamente al look actual):

- Nombre: trunca a un ancho fijo con "…" (`max-w-[90px]`, título completo
  vía `title=` y disponible al tocar -- va a la ficha). Sin esto, un
  nombre largo por sí solo ya fuerza scroll aunque el resto de la fila
  se comprima.
- Acciones: círculos de `chip_icono` bajan de `h-8 w-8` a `h-7 w-7` en
  mobile -- nuevo parámetro opcional `tam` en el macro (default
  `'h-8 w-8'`, sin cambios para los demás 6 usos del macro en
  `detail.html`), gap `gap-1.5` → `gap-1`.
- Padding horizontal `px-2` → `px-1` en mobile en Nombre/Torre/Acciones
  (Teléfono ya no aplica, está oculta).

**Hallazgo real durante la verificación**: en `table-auto` (layout por
defecto de esta tabla) el ancho de columna lo define el contenido MÁS
ANCHO entre `<th>` y `<td>` -- el título completo "Torre y Apartamento"
en el `<th>` seguía forzando el ancho de la columna en mobile aunque las
celdas ya mostraran el formato compacto "T05-102". Se aplicó el mismo
patrón de 2 `<span>` (`sm:hidden`/`hidden sm:inline`) también al
encabezado ("Torre/Apto" en mobile).

Resultado medido tras los 5 ajustes: 0px de overflow en el iframe de
359px (antes: 101px). Confirmado visualmente (zoom) que se ve bien --
nombres largos truncados con "…", nombres cortos completos, badges
Auto/Principal visibles, Torre/Apto compacto, los 4 íconos de Acciones
alcanzables sin scroll. Confirmado también que desktop (`sm:` en
adelante, probado a 900px) no cambió nada visible.

Tailwind recompilado (`npm run build:css`, nuevas utilities: `max-w-[90px]`,
`px-1`, `gap-1`, `h-7 w-7`) y `?v=66` → `?v=67` en `base.html`.

## Verificación

Suite completa (`pytest tests/web/test_customers_manage.py`): 151 passed,
rerun tras los 5 ajustes -- sin regresiones (solo cambios de CSS/markup,
sin lógica Python nueva más allá del parámetro `compacto`, cubierto por
el render existente).

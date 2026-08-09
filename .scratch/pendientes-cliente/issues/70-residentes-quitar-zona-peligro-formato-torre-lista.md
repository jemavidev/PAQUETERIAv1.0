# 70 — `/residentes`: quitar "Zona de peligro" de la ficha + formato compacto en la lista

**Pedido original (cliente):** sobre lo entregado en [[69]]:

1. "Zona de peligro" seguía viviendo dentro de la ficha (tab "Datos") --el
   cliente la considera irrelevante ahí, porque el botón "Eliminar cliente"
   ya existe en la columna Acciones de la lista `/residentes` (issue [[68]]).
   Pidió quitarla de la vista dentro de los tabs.
2. Nuevo (no pedido explícitamente antes): en la lista `/residentes`, la
   columna "Torre y Apartamento" debe mostrar solo el dato compacto (ej.
   "T 05 - APT 105"), igual que el label de la tab "Residentes" de la
   ficha ([[69]]), o "No Asignado" si no tiene unidad -- reemplaza el
   formato largo "Torre TORRE 5 · Apto 105" / "Sin apartamento".

**Feedback pendiente de resolver, sin acción todavía:**
- El aviso de reasignación bloqueada (tab Dirección, [[69]]) no quedó
  claro para el cliente -- va a pedir acceso a la base de datos para hacer
  sus propias pruebas. Sin cambios por ahora.
- La señalización ámbar de apartamentos con Principal en el picker queda
  pendiente a propósito -- el cliente planea un refactor más grande de esa
  zona más adelante.
- El fondo rojizo para Residentes Secundarios (fila de la lista + tabs de
  la ficha) generó dudas ("OK, pero no sé") -- pendiente de una decisión
  más clara, ver conversación.

**Status:** implementado (puntos 1 y 2); ver arriba los 3 puntos que
quedan abiertos sin resolver todavía.

## Decisión de implementación

- "Zona de peligro" se **elimina por completo** de `detail.html` (no se
  reubica a otro lugar de la ficha) -- la acción ya vive en `search.html`
  (columna Acciones, solo ADMIN, mismo modal de confirmación). El import
  `modal_confirmacion` y el script de toggle de modales (`[data-open]`/
  `[data-close]`) también se quitaron de `detail.html`: sin la Zona de
  peligro no queda ningún otro elemento en esa plantilla que los necesite.
- Nueva función compartida `_etiqueta_torre_apto(apartamento, fallback)`
  en `customers_manage.py` -- generaliza lo que antes era
  `_etiqueta_tab_residentes` (solo usaba "Residentes" como fallback) para
  poder reusar el mismo formato en la lista (fallback "No Asignado").

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Verificación visual en navegador real (Playwright): confirmado que
  "Zona de peligro" ya no aparece en ningún lado de la ficha, y que la
  lista muestra "T 05 - APT 105" / "No Asignado" correctamente. Sin
  errores de consola.
- Suite completa (`tests/data_model tests/web`): 689/689, sin
  regresiones. Tests reescritos/nuevos: ausencia total de "Zona de
  peligro" en la ficha, formato compacto de la columna Torre y
  Apartamento (con y sin unidad asignada).
- Sin cambios en Tailwind compilado esta vez (solo se quitó markup que
  usaba clases ya compiladas, no se agregó ninguna nueva) -- `?v=36` sigue
  vigente, sin bump.

# 347 — Modales: siempre empiezan a la misma altura en mobile

**Pedido original (cliente):**
"Seria bueno que en la vista mobil donde aparezcan cualquier modal,
siempre se empiece a cargar desde la misma altura, veo que esto difere
entre vistas o modales"

**Status:** implementado, pendiente confirmar visualmente

## Contexto

`components/_modales.html` (macros `modal()` y `modal_confirmacion()`,
usados por TODA la app -- incluido `modal_recibir`, que llama a `modal()`
internamente) centraba verticalmente (`items-center`) el panel dentro del
overlay fijo de pantalla completa. Con centrado vertical, el borde
superior del panel depende de SU PROPIA altura: un modal corto (una
confirmación) centra más abajo, uno largo (el modal "Ver", con su
timeline) centra más arriba -- inconsistente entre modales, tal como
reportó el cliente. No es un bug de un modal puntual, es el propio
mecanismo de centrado.

## Implementación

- `modal()` y `modal_confirmacion()`: `items-center` -> `items-start
  sm:items-center` -- en mobile, el panel se ancla a un offset FIJO desde
  arriba (`pt-12`, ~altura de `.site-header`) sin importar cuánto
  contenido traiga; desde `sm:` revierte al centrado de siempre (pedido
  explícito acotado a "la vista mobil" -- en desktop hay más alto de
  viewport y el centrado no generaba la queja).
- El panel interno sigue capado (`max-h-[85vh] overflow-y-auto`) para
  contenido largo -- nunca se sale del viewport por abajo, solo cambia
  DÓNDE empieza el borde superior.
- Padding de cada lado spelled out por separado (`px-4 pb-4 pt-12
  sm:pt-4`, no `p-4` + `pt-*` sueltas) -- dos utilities sin prefijo de
  breakpoint para el mismo lado compiten por orden de generación de
  Tailwind, no por orden en el HTML (mismo criterio ya documentado en
  `packages/_acciones.html` para `chip_icono`).
- `_visor_fotos.html` (el lightbox de fotos, overlay distinto) NO se tocó
  -- no es un modal de contenido/formulario, sigue centrado como siempre.

## Alcance

Cubre TODOS los modales que pasan por `modal()`/`modal_confirmacion()` --
confirmado con `grep` que son los únicos 2 wrappers `fixed inset-0 ...
items-center justify-center` de toda la app (fuera del visor de fotos).

## Tests

Suite completa `tests/web/` corriendo en background al momento de este
registro -- ningún test dependía de la clase exacta del wrapper
(`grep` sobre `tests/` no encontró coincidencias).

## Verificación

Pendiente confirmación visual del cliente.

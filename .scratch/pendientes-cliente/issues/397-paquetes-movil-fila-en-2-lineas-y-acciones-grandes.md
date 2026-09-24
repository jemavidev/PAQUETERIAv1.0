# 397 — `/paquetes` móvil: cada paquete en 2 líneas y acciones más grandes

**Pedido original (Jesús):** "en la vista /paquetes para la versión móvil, de qué forma puedes para cada paquete que se
visualice que sea posible que tengas 2 líneas por cada paquete, esto con el fin de redistribuir la información que se
muestra, adicional que se pueda tener los íconos de la columna acción más grandes y fácil de usar por cualquier usuario
en dispositivos móviles. Dame 3 versiones de cómo lo solucionarías".

**Status:** implementado (variante B), pendiente confirmar en vivo (localhost)

## Contexto

Hoy en móvil: nombre + código arriba, apartamento abajo, y 3 íconos de ~30 px a la derecha (WhatsApp, Llamar,
Recibir/Entregar); Modificar, Cancelar y Eliminar no existen en móvil. Lo recomendado para tocar con el dedo: 44-48 px.

## Prototipo (skill `prototype`)

Rama `prototipo/paquetes-movil-2-lineas` (worktree aparte), servidor en `:8011` sobre la BD local,
`/paquetes?variant=A|B|C` + selector flotante. Solo móvil; la tabla de escritorio no cambia.

- **A — Lista en 2 líneas:** nombre + código arriba; apartamento + tiempo abajo, con 3 botones redondos de 44 px.
- **B — Tarjeta + botonera:** datos arriba; abajo 3 botones anchos de 48 px con ícono y TEXTO (WhatsApp, Llamar,
  Recibir/Entregar).
- **C — Acción principal + menú ⋯:** un botón grande (56 px) con la acción del momento y "⋯" que abre una hoja con
  TODAS las acciones en filas grandes, incluidas Modificar, Cancelar y Eliminar (hoy ausentes en móvil).

## Decisión (Jesús, 2026-09-24)

"me quedo con la versión B, pero creo que las letras de información apt/tiempos/paquetes y nombre del residente
podrían ser un poco más grandes, los 3 botones están perfectos".

- Se implementa B en la vista real: tarjeta por paquete con franja de color por estado; arriba código + nombre + línea
  "Torre · Apto · Estado · tiempo"; abajo 3 botones de 48 px con ícono y texto (WhatsApp, Llamar, Recibir/Entregar),
  sin cambios respecto al prototipo.
- Letra más grande que en el prototipo: nombre `text-lg` (antes `text-base`), código `text-base` (antes `text-sm`),
  línea de apartamento/estado/tiempo `text-sm` (antes `text-xs`).
- Solo móvil (< 640 px); la tabla de escritorio no cambia. Se conservan las señales de la fila actual: ícono de
  destinatario eliminado y apartamento en rojo si el destinatario se mudó.
- El prototipo (3 variantes + selector) queda en la rama `prototipo/paquetes-movil-2-lineas` (commit `78a9928`), fuera
  de main.

## Verificación

- `tests/web/test_paquetes_movil_tarjetas.py` (3, fallaban antes): tarjeta por paquete solo en móvil y tabla solo en
  escritorio; código `text-base`, nombre `text-lg`, línea de apartamento/estado `text-sm`; 3 botones `h-12` con texto
  y la acción según el estado (Recibir/Entregar/apagado).
- Ajustadas a propósito en `test_packages.py`: el modal "Ver" tiene 2 disparadores (uno por diseño, nunca visibles a
  la vez); el código de la tarjeta va en píldora `rounded-full` (decisión previa del cliente). 241 en verde.
- Tailwind reconstruido, `?v=104`. Capturas a 390 px (tarjetas) y 1100 px (tabla sin cambios) revisadas.
- Prototipo: servidor `:8011` apagado y worktree quitado; las 3 variantes quedan en la rama
  `prototipo/paquetes-movil-2-lineas` (`78a9928`).

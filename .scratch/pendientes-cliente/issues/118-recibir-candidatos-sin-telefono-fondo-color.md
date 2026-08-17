# 118 — Tarjetas de candidato en Recibir: sin teléfono, "Actual" con fondo de color

**Pedido original (cliente):**
"Remueve el numero de telefono de lo que estas listando en este modal, y
para la seleccion actual seria mejor dejar un fondo de color coo has
venido haciendo."

**Status:** implementado

## Implementación

- `_recibir_paquete.html`: las tarjetas de candidato (issue 117) ya no
  muestran el teléfono, solo el nombre.
- El badge de texto "Actual" se reemplaza por fondo de color
  (`bg-slate-100 border-slate-300`) en la tarjeta del candidato que
  coincide con `recipient_name`/`recipient_phone` -- mismo criterio ya
  usado para Estado/duración (`estado_colores`). Se usa slate, NO azul, a
  propósito: azul (`peer-checked:bg-blue-50`) es el color de "recién
  marcado por el staff" -- si fueran el mismo color, elegir una tarjeta
  DISTINTA a la actual dejaría dos tarjetas iguales en pantalla sin forma
  de distinguir cuál es cuál. Con colores distintos, las dos conviven sin
  ambigüedad. Sigue sin marcar ningún radio como `checked` (issue 117,
  mismo motivo: evitar reactivar `corregir_destinatario` sin cambios
  reales).
- `tailwind.css` recompilado (`?v=45`) -- `peer-checked:text-slate-900`
  no estaba compilado todavía.

## Verificación

- `tests/web/test_packages.py`: test actualizado -- confirma ausencia de
  teléfono en las tarjetas y que el candidato actual lleva `bg-slate-100`
  (no un badge de texto), sin ningún radio `checked`.
- Playwright contra el servidor local real: capturas confirmando fondo
  gris en el candidato actual, y fondo azul en un candidato distinto
  recién clickeado, ambos visibles a la vez sin confundirse.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

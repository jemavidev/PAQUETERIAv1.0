# 266 — Modal genérico: ícono "✕" de cerrar más grande

**Pedido original (cliente):** "Podría hacer las 'x' que cierran los
modales un poco más grande ya que casi no se ve."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Verificación

Suite `test_customers_manage.py` + `test_customer_verify.py`: 213
passed. Ícono `h-6 w-6` + botón `p-1` confirmados renderizados en vivo
(curl contra `/residentes/c75f7cdd-...`, dev local).

## Alcance

`components/_modales.html::modal()` -- el único macro de modal con
ícono X (el otro, `modal_confirmacion`, solo tiene el botón de texto
"Regresar", sin ícono). El SVG de cerrar pasa de `h-5 w-5` (20px) a
`h-6 w-6` (24px), y el botón que lo envuelve gana `p-1` -- área de
click más grande, no solo el ícono más grande. Cambio en el componente
compartido: afecta a TODOS los modales de la app que usan `modal()`
(ej. "Editar" en `/residentes` y `/mis-datos`), no solo uno puntual --
mismo criterio que issue 242 (texto "Regresar" en `modal_confirmacion`,
también componente compartido).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

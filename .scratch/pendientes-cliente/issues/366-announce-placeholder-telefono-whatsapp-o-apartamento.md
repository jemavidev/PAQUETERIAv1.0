# 366 — `/announce`: placeholder del campo único → "Teléfono, WhatsApp o Apartamento"

**Pedido original (cliente):**
"Necesito que para la vista /announce cambien el placeholder 'Teléfono o
usuario de WhatsApp' por 'Teléfono, WhatsApp o Apartamento'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

- Solo el texto del campo único de `announce_new/form.html` (es a la vez
  placeholder y `aria-label`, ver `components/_inputs.html`). El campo ya
  acepta un código Torre+Apto desde `.scratch/announce-rapido` -- el texto
  viejo no lo decía.

## Implementación

- `announce_new/form.html`: el campo único pasa de `input_texto('Teléfono o
  usuario de WhatsApp', ...)` a `input_texto('Teléfono, WhatsApp o
  Apartamento', ...)`. Ese primer argumento es a la vez el placeholder y el
  `aria-label` (`components/_inputs.html`) -- los dos cambian con un solo
  edit.

## Verificación

- `tests/web/test_announce_new.py::test_operador_ve_el_campo_unico`: fija
  `placeholder="Teléfono, WhatsApp o Apartamento"` y
  `aria-label="Teléfono, WhatsApp o Apartamento"`, y que el texto viejo ya no
  aparece.
- Navegador a 390 px (iframe del mismo origen, sesión de Staff real): el
  campo se ve con el texto nuevo, sin desbordar ni provocar scroll horizontal.
- Pendiente: confirmación visual del cliente y deploy a test.papyrus.com.co.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

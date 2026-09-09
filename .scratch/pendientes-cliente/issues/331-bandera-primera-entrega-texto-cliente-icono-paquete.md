# 331 — Bandera "primera entrega": texto a "este cliente" e ícono de caja/paquete

**Pedido original (cliente):** "Cambia este texto en el modal para entregar el paquete 'Primera
entrega a este número de teléfono' a 'Primera entrega a este cliente', adicional a esto remplaza
el icono de la estrella por una caja o paquete."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Diseño

Cambio puramente cosmético (texto + ícono) sobre la macro `bandera_primera_entrega()` (issue 314/
316, `components/_badge.html`). El criterio subyacente (`es_primera_entrega_a_telefono` en
`packages.py`) sigue siendo por teléfono -- no cambia, el cliente pidió solo el texto visible.

Ícono: se reusa `iconos_nav.paquetes` (ya existe en `icons.py`, silueta de caja) en vez de crear un
ícono nuevo -- mismo estilo `stroke` que ya usaba `estrella`, mismo `viewBox="0 0 24 24"`.

## Implementación

- `app/web/templates/components/_badge.html`: macro `bandera_primera_entrega()` -- texto a
  "Primera entrega a este cliente", ícono `iconos_nav.estrella` → `iconos_nav.paquetes`.

## Verificación

- `tests/web/test_packages.py` y `tests/web/test_search.py`: constante
  `_BANDERA_PRIMERA_ENTREGA` actualizada al nuevo texto (ambos archivos referencian la misma
  bandera, ver duplicación de modal documentada en issue 316).

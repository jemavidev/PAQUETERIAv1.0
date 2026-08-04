# 01 — `/anunciar` confirmación: nombre y teléfono en mayúsculas y negrilla

**Pedido original (cliente):** "Necesito que tanto el nombre del cliente
como su numero de telefono este en mayusculas y en negrillas, esto con el
fin de resaltar la informacion que se muestra."

**Vista:** `announce/confirmacion.html` (recibo de éxito tras anunciar un
paquete desde `/anunciar`).

**Status:** verificado

## Qué se hizo

- `fila_dato()` en `components/_confirmacion.html` ganó un parámetro opcional
  `destacado=false` (uppercase vía CSS + `font-bold`) — no afecta otras
  pantallas porque hoy es el único caller real de ese macro.
- `announce/confirmacion.html` pasa `destacado=true` en las filas de
  Nombre y Teléfono únicamente (Apartamento se queda con el peso normal).

## Verificación

- 8/8 `tests/web/test_announce.py`, 436/436 suite completa.
- Desplegado a `test.papyrus.com.co` (commit `58d65fa`).
- Confirmado en vivo vía POST directo a `/anunciar`: ambos `<dd>` renderizan
  con `class="font-bold uppercase ..."`.

## Comments

- 2026-08-01: el cliente reportó que este pedido nunca se implementó y que
  no tenía forma de saber qué otros pedidos suyos se habían quedado sin
  hacer — de ahí nace este directorio de tracking (`spec.md` en este mismo
  directorio explica la regla hacia adelante).

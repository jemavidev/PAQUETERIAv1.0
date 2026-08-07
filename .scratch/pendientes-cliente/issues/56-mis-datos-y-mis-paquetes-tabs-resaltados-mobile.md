# 56 — `/mis-datos` y `/mis-paquetes`: resaltar cada tab en mobile (fondo + borde)

**Pedido original (cliente):** "el tamano es perfecto, en las 2 vistas, lo
que necesito ahora es que se pueda resaltar un poco mas cada tab, esto ya
que al estar los 4 tabs juntos se mezcla con todo lo que es esta vista y
por forma en que colocamos el grid no se nota demaciado que es un grid en
la vista movil [...] recuerda solo en la vista movil todo lo que hagas."

**Status:** implementado

## Contexto

Ajuste directo sobre [[55]] (tamaño confirmado como "perfecto" en las 2
vistas) — el problema restante era puramente visual: cada tab inactivo no
llevaba ningún fondo/borde, solo texto flotando sobre la página blanca, así
que el grid 2x2 no se percibía como tal.

## Implementación

Mismo cambio en `customer/verify.html` y `customer/paquetes.html`:

- Cada tab INACTIVO gana `bg-slate-50 border border-slate-200` (fondo y
  borde sutiles) — se ve como su propia ficha en vez de solo texto.
- `lg:bg-transparent lg:border-0` anula esto en desktop — la vista de
  escritorio queda exactamente igual que antes (pedido explícito: "solo en
  la vista movil").
- El tab ACTIVO no lleva este fondo/borde — el JS se lo saca
  explícitamente (`classList.toggle(..., !activo)`) para que no compita
  con su propio `bg-blue-50` ya existente (evita ambigüedad de cascada
  entre dos utilidades de `background-color` en el mismo elemento).

## Verificación

- Sintaxis Jinja (`Environment.parse()`) y JS (`node --check` sobre el
  `<script>` extraído) verificadas en ambos archivos.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co`, en un dispositivo móvil
  real, que cada tab ahora se distingue como una ficha propia y que
  desktop queda intacto.

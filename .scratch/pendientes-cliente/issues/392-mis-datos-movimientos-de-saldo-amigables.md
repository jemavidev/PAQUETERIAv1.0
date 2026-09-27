# 392 — `/mis-datos`: movimientos del saldo contra entrega más amigables

**Pedido original (Jesús):** "mejora la forma en que se ve esto "19/09/2026 · paquete 49a62449", que sea más amigable".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Cada movimiento dice QUÉ pasó, según su signo y si tiene paquete: negativo con paquete → "Pagado al mensajero"
  (el portero pagó el contra entrega al recibir); positivo con paquete → "Pago recibido" (el residente pagó al
  retirar); positivo sin paquete → "Abono a tu saldo"; negativo sin paquete → "Descuento".
- Debajo: el código del paquete que el residente conoce ("Paquete 7JY7", no el pedazo del UUID) y la fecha y hora en
  español y hora de Colombia ("19 sep. 2026 · 3:40 p. m.").
- Monto con el signo antes del peso: "-$3,500" / "+$12,000" (antes "$-3,500").

## Verificación

- `tests/web/test_portal_saldo_contra_entrega.py::test_los_movimientos_dicen_que_paso_con_el_codigo_del_paquete_y_fecha_amigable` (fallaba antes): los tres conceptos, `Paquete <código>`, sin fragmento del UUID, `-$3,500`/`+$12,000` y fecha `19 sep. 2026 · 3:40 p. m.`. 72 en verde con `test_customer_verify.py`. Filtro nuevo `fecha_amigable` (`templating.py`).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

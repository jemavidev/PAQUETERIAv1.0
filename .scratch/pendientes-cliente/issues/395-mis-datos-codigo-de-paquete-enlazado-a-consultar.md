# 395 — `/mis-datos`: el código del paquete en los movimientos del saldo enlaza a `/consultar`

**Pedido original (Jesús):** en los movimientos del saldo ("Pagado al mensajero · Paquete DFDK · 18 sep. 2026…"),
"cuando aparezcan estos "DFDK, K9QM, F78U o cualquier otro código" lo conviertas a link de la vista
/consultar?q=<código>".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- En cada movimiento con paquete, el código ("DFDK") es un enlace a `/consultar?q=<código>`, misma pestaña. El resto
  del texto ("Paquete", la fecha) queda como está.

## Verificación

- `tests/web/test_portal_saldo_contra_entrega.py::test_el_codigo_del_paquete_en_un_movimiento_enlaza_a_consultar` (fallaba antes); la prueba del 392 ajustada para aceptar el código enlazado. 73 en verde con `test_customer_verify.py`. Sin clases de Tailwind nuevas (`font-medium`, `text-blue-800`, `hover:underline` ya compiladas).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

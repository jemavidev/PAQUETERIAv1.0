# 243 — `/mis-paquetes`: código de acceso al lado derecho de Torre/Apto

**Pedido original (cliente):** "Necesito que en la vista /mis-paquetes
ubiques el código de acceso justo al lado derecho de la torre y el
apartamento, justificado a la derecha."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customer/paquetes.html` -- tarjeta colapsada de cada paquete. La píldora
de código de acceso (issue 207) se movió de la fila superior (junto al
nombre/badge) a la misma fila donde ya vive "Torre X · Apto Y"
(`snapshot_apartamento`), empujada al extremo derecho (`ml-auto`). Cubre
también el caso "Sin apartamento" (`snapshot_apartamento` vacío) -- el
código se alinea a la derecha de ese texto también, para no perderlo en
ningún paquete.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

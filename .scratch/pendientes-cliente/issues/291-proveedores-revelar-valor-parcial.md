# 291 — Revelar parcialmente el valor real de las credenciales configuradas

**Pedido original (cliente):** "por seguridad seria bueno solo ver la
informacion necesaria pero no toda, por ejemplo el access key id is ok,
but hide some characters for the AWS_SECRET_ACCESS_KEY, do the same
hiding the smstp password, and do the same for meta and pbx" — seguido de
"realiza lo que te pido con las llaves de aws, asi lo necesito" (confirma
marcar `AWS_ACCESS_KEY_ID` como no-secreto, visible completo).

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

Revierte parcialmente el criterio original del ticket 05 ("ni la propia
pantalla lee el valor real") -- ahora sí lo lee, pero nunca lo manda
completo al navegador:

- Campo `secreto=True` configurado: el placeholder muestra un enmascarado
  parcial del valor real (`_enmascarar_secreto`, `admin_proveedores.py`) --
  primeros/últimos 4 caracteres visibles, resto con un número FIJO de
  puntos (no proporcional al largo real, para no filtrar cuántos caracteres
  tiene el secreto). Valores de 8 caracteres o menos se enmascaran por
  completo.
- Campo `secreto=False` configurado: el placeholder muestra el valor real
  completo, sin enmascarar (`AWS_REGION`, `SMTP_HOST`, los booleanos, etc.
  -- nunca fueron secretos).
- `AWS_ACCESS_KEY_ID` pasa de `secreto=True` (default) a `secreto=False`
  explícito -- confirmado por el cliente, mismo criterio que la propia
  consola de AWS.
- El `value=` del input real sigue SIEMPRE vacío -- solo cambia el
  `placeholder` (texto de solo lectura, el navegador nunca lo manda de
  vuelta al hacer submit). "Vacío = no cambiar esa credencial" (ticket 05)
  no cambia con esto.

Aplica de forma genérica a TODOS los proveedores (SMS, Email, WhatsApp) vía
el flag `secreto` ya existente en el catálogo -- sin caso especial por
proveedor.

## Implementación

`app/web/routes/admin_proveedores.py`: `_enmascarar_secreto()` +
`_valor_actual()`, consumidos por `_filas_proveedores()`. Plantilla
actualizada para usar `campo.valor_actual` en el `placeholder` (texto/select
booleano). `AWS_ACCESS_KEY_ID` marcado `secreto=False` en
`proveedores_catalogo.py`.

## Verificación

Suite completa: 1316 passed. `tests/web/test_admin_proveedores.py`: 22
passed (incluye 2 tests directos de `_enmascarar_secreto` -- valor normal y
caso límite corto -- y 3 tests de comportamiento HTTP: secreto enmascarado,
no-secreto completo, Access Key ID ya no `type="password"`). Pendiente
confirmar en vivo contra `test.papyrus.com.co` con una credencial real.

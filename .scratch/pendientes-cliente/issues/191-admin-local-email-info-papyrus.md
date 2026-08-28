# 191 — Email del admin local reemplazado por info@papyrus.com.co

**Pedido original (cliente):**
"Necesito que el email del admin sea remplazado por el siguiente
'info@papyrus.com.co'"

(A continuación de la pregunta sobre credenciales del admin — ver issue
190 para el contexto de la vista tocada.)

**Status:** implementado (solo ambiente local — ver Alcance)

## Alcance

Este cambio es puramente de **datos del ambiente local de desarrollo**
(`scripts/paquetex_dev_up.sh` levanta un Postgres persistente propio,
`paquetex_dev_pg`, separado de staging/producción) — la app no tiene
ninguna función para editar el email de una cuenta de staff
(`staff_service.editar_staff` solo cubre nombre/rol), así que no hubo
código de producto que tocar.

## Implementación

- `scripts/paquetex_dev_up.sh`: `ADMIN_EMAIL="admin@local.test"` →
  `ADMIN_EMAIL="info@papyrus.com.co"` — para que un reset futuro de la base
  local siembre el admin con este email directamente.
- La cuenta admin YA existente en el Postgres local persistente
  (`admin@local.test`) se actualizó con un `UPDATE` directo en
  `usuarios.email` -- dato de prueba local, no hay ruta de la app para
  hacerlo, y no aplica ninguna migración (no es un cambio de esquema).

## Verificación

- Login con `info@papyrus.com.co` / `Contrasena1` contra el servidor de
  dev local: `303` (éxito), acceso a `/administracion/notificaciones`
  confirmado (`200`).
- Login con el email viejo (`admin@local.test`): `400` — ya no existe.

## Fuera de alcance

- No toca `test.papyrus.com.co` ni ningún ambiente real — si también se
  quiere ese cambio ahí, es una acción aparte (credenciales de un sistema
  real, no algo para tocar sin pedirlo explícitamente).

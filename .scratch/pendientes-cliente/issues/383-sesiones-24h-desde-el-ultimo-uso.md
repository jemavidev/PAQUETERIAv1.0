# 383 — Sesiones: 24 h desde el último uso

**Pedido original (Jesús):** "las Sesiones podrían ser de máximo 24 horas en caso que no se use la sesión, ya que en cada uso se renovarán 24 horas adicionales" — "perfecto lo de las Sesiones" (hallazgo 9).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Cookie de sesión con `max_age` de 24 h; Starlette la vuelve a firmar en cada respuesta, así que cada uso renueva
  otras 24 h (staff y clientes).
- Cambiar o restablecer la contraseña de un usuario de staff cierra sus demás sesiones (versión de sesión en `Usuario`).
- Cookie `Secure` solo fuera de desarrollo (en `http://localhost` una cookie Secure no viaja).

## Verificación

- `tests/web/test_sesiones_24h.py` (4, fallaban antes): `Max-Age=86400` al ingresar y en cada uso; restablecer la contraseña desde Administración cierra las sesiones de ese usuario; cambiar la propia mantiene la sesión actual y cierra las demás; cookies anteriores (sin versión) siguen valiendo. Migración `0060_usuario_sesion_version`. `Secure` solo con `WEB_ENV` staging/production.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

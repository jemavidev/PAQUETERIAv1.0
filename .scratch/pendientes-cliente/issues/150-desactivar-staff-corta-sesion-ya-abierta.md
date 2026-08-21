# 150 — Desactivar un staff corta su sesión ya abierta, no solo el próximo login

**Pedido original:** tras el pedido "analiza todo el sistema... si tienes el contexto completo,
pregunta ahora o calla para siempre", se auditó toda la app PaqueteX v2 (portal de autoservicio,
`/paquetes`/`/announce`/`/residentes`, `/administracion`) buscando la misma categoría de bug de
[[148]]/[[149]] (una acción que debería reflejarse en otro lado del sistema y no lo hace). Único
hallazgo real fuera del padrón de residentes: `current_staff` nunca releía `usuario.activo`.
Confirmado explícitamente por el usuario ("sí") para arreglarlo.

**Status:** implementado

## Diagnóstico

`set_activo_staff` (`staff_service.py`) solo escribe `usuario.activo = False`. La puerta de TODAS
las rutas de staff (`current_staff`/`require_admin`, `security.py`) releía el `Usuario` completo
de la BD en cada request (sin caché) pero solo chequeaba que la fila existiera -- nunca
`.activo`. Ese campo únicamente se validaba en `staff_service.autenticar`, al hacer login.
Consecuencia real: un ADMIN que desactivaba a alguien con sesión YA abierta (cookie firmada,
default de sesión de Starlette) no le cortaba el acceso -- esa persona seguía pudiendo operar con
normalidad hasta que la cookie expirara o cerrara sesión manualmente. El propio sistema ya sabía
hacer cumplir esto en vivo (los cambios de ROL sí se aplican de inmediato en cualquier request
nuevo, mismo mecanismo de relectura) -- simplemente nunca se extendió a `.activo`.

## Fix

`security.py::current_staff`: agrega `or not usuario.activo` al mismo chequeo que ya existía
para "usuario no encontrado" -- mismo tratamiento (pop de la sesión, 401 → redirect a
`/ingresar`), mismo mensaje genérico "Sesión inválida" (no revela que la cuenta fue desactivada,
igual criterio que ya usa el rechazo de login).

## Verificación

- `tests/web/test_admin_staff.py::test_desactivar_cierra_una_sesion_ya_abierta_en_el_siguiente_request`
  (nuevo): 2 `TestClient` independientes sobre la misma app (sesiones de navegador simuladas,
  admin y operador simultáneos) -- confirma que el operador puede operar ANTES, y que el mismo
  request después de que el admin lo desactiva devuelve 303 a `/ingresar`.
- `tests/web/test_admin_staff.py`: 16/16.
- Suite completa del repo corriendo al momento de escribir este ticket.

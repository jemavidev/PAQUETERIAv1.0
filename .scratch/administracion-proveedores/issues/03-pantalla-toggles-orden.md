# 03 — Pantalla `/administracion/proveedores`: habilitar/deshabilitar y reordenar

**What to build:** la pantalla real donde Jesús puede ver y cambiar qué proveedores
están activos y en qué orden, con efecto inmediato sobre los envíos reales (gracias al
ticket 02). Este es el primer punto donde la feature completa ya resuelve el pedido
original más urgente: poder apagar un proveedor caído (LIWA/Twilio hoy, ver issue
[[288]] de `.scratch/pendientes-cliente`) sin pedir intervención por SSH.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 1-5, 12, 20, 22).

**Blocked by:** 01, 02

**Status:** verificado

- [x] Ruta `/administracion/proveedores`, protegida por `require_admin` (mismo patrón
      que `admin_conjunto_form`/`admin_conjunto_guardar`) — un OPERADOR recibe 403 en
      GET y en POST.
- [x] Por cada canal que tiene al menos un proveedor en el catálogo de código (hoy:
      SMS y Email), la pantalla muestra sus proveedores con un toggle de
      habilitado/deshabilitado (macro `toggle()` ya existente).
- [x] Para canales con más de un proveedor (hoy: SMS), un `<input type="number">` de
      orden editable — Email/SMTP (un solo proveedor) no lo muestra.
- [x] Guardar un cambio de habilitado/orden lo aplica de inmediato (sin restart) —
      `test_guardar_reordena_y_afecta_la_cadena_real_de_inmediato` reordena vía POST y
      luego ejercita `sender.enviar()` de verdad (mock de `httpx.post`), confirmando
      que SOLO Twilio (recién puesto en orden=1) recibe la llamada.
- [x] WhatsApp y Llamadas NO aparecen en la pantalla — sin sección "próximamente".
- [x] Cada cambio queda en el historial de auditoría del ticket 01 (verificado con
      `usuario_id` real del admin logueado, no `None`).
- [x] `tests/web/test_admin_proveedores.py` (8 tests): login admin ve la pantalla con
      el estado del catálogo; login operador 403 (GET y POST); togglear/reordenar vía
      POST persiste (verificado contra la tabla) y afecta el envío real; sin sesión
      redirige a login.

**Nuevo archivo dedicado** (`app/web/routes/admin_proveedores.py`, no agregado a
`admin.py`): decisión explícita para no seguir haciendo crecer un archivo que ya
mezcla personal/notificaciones/conjunto (559 líneas) con una cuarta responsabilidad
no relacionada.

**Code review** (Standards + Spec): 2 hallazgos confirmados — (1) la política "sin
fila en BD → habilitado=True" estaba duplicada entre `armar_candidatos()` (issue 02)
y `_filas_proveedores()`; extraída a `proveedor_config_service.habilitado_orden_
efectivos()`, fuente única para ambas. (2) el test de "aplica de inmediato" solo
verificaba `isinstance()` del sender armado; reforzado para ejercitar `.enviar()` de
verdad con `httpx.post` mockeado, observando qué proveedor recibe la llamada.

**Verificación:** suite completa (1290 passed) tras los fixes del code review.

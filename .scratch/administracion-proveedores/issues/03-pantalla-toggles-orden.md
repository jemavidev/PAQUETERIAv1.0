# 03 — Pantalla `/administracion/proveedores`: habilitar/deshabilitar y reordenar

**What to build:** la pantalla real donde Jesús puede ver y cambiar qué proveedores
están activos y en qué orden, con efecto inmediato sobre los envíos reales (gracias al
ticket 02). Este es el primer punto donde la feature completa ya resuelve el pedido
original más urgente: poder apagar un proveedor caído (LIWA/Twilio hoy, ver issue
[[288]] de `.scratch/pendientes-cliente`) sin pedir intervención por SSH.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 1-5, 12, 20, 22).

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] Ruta `/administracion/proveedores`, protegida por `require_admin` (mismo patrón
      que `/administracion/notificaciones`) — un OPERADOR recibe 403.
- [ ] Por cada canal que tiene al menos un proveedor en el catálogo de código (hoy:
      SMS y Email), la pantalla muestra sus proveedores con un toggle de
      habilitado/deshabilitado.
- [ ] Para canales con más de un proveedor (hoy: SMS), un control de orden de
      precedencia (numérico o de arrastrar) editable.
- [ ] Guardar un cambio de habilitado/orden lo aplica de inmediato (sin restart) —
      demostrable enviando una notificación de prueba real después del cambio y
      viendo que respeta el nuevo estado.
- [ ] WhatsApp y Llamadas NO aparecen en la pantalla (no tienen proveedor real en el
      catálogo todavía) — nada de sección "próximamente".
- [ ] Cada cambio queda en el historial de auditoría del ticket 01 (canal, proveedor,
      quién, cuándo, valor anterior/nuevo).
- [ ] Tests de ruta (`tests/web/test_admin_proveedores.py`): login admin ve la
      pantalla con el estado sembrado por la migración del ticket 01; login operador
      recibe 403; togglear/reordenar vía POST persiste y se refleja en el HTML
      re-renderizado; sin sesión redirige a login (mismo patrón que
      `test_admin_notificaciones.py`).

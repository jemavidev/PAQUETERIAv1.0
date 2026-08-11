# 10 — Notificaciones al Anunciante + preselección en co-residentes

**What to build:** cuando el destinatario de un paquete no tiene contacto propio, `recipient_phone` cae a quien quedó como Anunciante del paquete (en vez de que `telefono_notificacion_ocupante` resuelva su propio fallback-a-principal de forma aislada). En la pantalla de co-residentes de `/announce` (Teléfono/WhatsApp con más de un residente activo), la fila de quien llamó queda preseleccionada por default.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] En `paquete_service.announce()`, para `Destinatario.OCUPANTE` sin `persona_id` propio: `recipient_phone` usa el Teléfono de la Persona `anunciante` ya resuelta en esa misma llamada (`None` si el Anunciante es solo-WhatsApp), no `telefono_notificacion_ocupante`.
- [ ] Camino Torre+Apto directo: sin cambio observable (el Anunciante ya se resolvía al principal vía `anunciante_para_ocupante`).
- [ ] Camino Teléfono/WhatsApp con co-residentes: la notificación cae a quien llamó, no al principal, cuando el destinatario elegido no tiene contacto propio.
- [ ] En `_identificar_unidad.html` (pantalla de co-residentes), la fila de quien se identificó por Teléfono/WhatsApp aparece preseleccionada — el resto de la lista sigue disponible para elegir otro residente o crear uno nuevo.
- [ ] Tests en `test_announce_new.py` cubriendo ambos caminos y la preselección.

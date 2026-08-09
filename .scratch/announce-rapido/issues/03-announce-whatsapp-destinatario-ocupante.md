# 03 — `announce()` acepta un Anunciante solo-WhatsApp + `Destinatario.ocupante()`

**What to build:** `Paquete.announced_by_phone` pasa a nullable (queda `NULL` cuando el Anunciante no tiene Teléfono) — `announced_by_persona_id` **no cambia** (sigue `NOT NULL`, toda Persona real es referenciable por FK tenga o no Teléfono). `paquete_service.announce` gana una vía alterna para identificar al Anunciante: Teléfono (como hoy) o `whatsapp_usuario` (nuevo), exactamente uno de los dos — resuelve internamente con `get_or_create_persona` o `get_or_create_persona_por_whatsapp` (ticket 01) según cuál se pasó.

Nuevo constructor `Destinatario.ocupante(ocupante_id)`: generaliza la resolución que hoy hace `_resolver_ocupante_por_nombre` dentro del caso `DECLARADO_POR_CLIENTE` — dado un Ocupante puntual, resuelve su nombre y su contacto de notificación (Teléfono o WhatsApp propios si los tiene; si no, cae al Teléfono/WhatsApp del Principal activo de la misma unidad, mismo mecanismo que ya usa `telefono_notificacion_ocupante`).

El límite de "máx. 10 anuncios activos por Teléfono" (`MAX_ANUNCIADOS_ACTIVOS_POR_TELEFONO`) simplemente no aplica a un Anunciante solo-WhatsApp por ahora (no hay Teléfono contra el cual contar) — un límite equivalente por WhatsApp queda fuera de esta ficha.

Sin superficie de UI todavía — se verifica llamando `announce()`/`Destinatario.ocupante()` directo desde pytest.

**Blocked by:** 01, 02.

**Status:** ready-for-agent

- [ ] `paquetes.announced_by_phone` es nullable; migración `upgrade head` → `downgrade base` limpia.
- [ ] `announce()` con Anunciante identificado por `whatsapp_usuario` (sin Teléfono) crea el Paquete con `announced_by_phone=NULL` y `announced_by_persona_id` apuntando a la Persona correcta.
- [ ] `announce()` sigue funcionando exactamente igual que hoy cuando el Anunciante se identifica por Teléfono (sin regresión).
- [ ] `Destinatario.ocupante(id)` resuelve `recipient_name`/contacto de notificación igual que hoy hace la resolución por nombre, incluida la caída al Teléfono/WhatsApp del Principal cuando el Ocupante no tiene contacto propio.
- [ ] `contar_anunciados_activos_de_telefono` no cuenta (ni falla) sobre Paquetes con `announced_by_phone=NULL`.

# 06 — Preferencias de notificación: heredadas (sin teléfono) vs propias (con teléfono)

**What to build:** un Ocupante SIN teléfono no tiene ni puede tener su propia fila de preferencias (`PersonaPreferenciaNotificacion` exige `persona_id`, y sin teléfono no hay Persona) — sus notificaciones, al llegarle al teléfono del principal, deben regirse por la matriz YA configurada del PRINCIPAL. Un Ocupante CON teléfono (su propia Persona, vía `get_or_create_persona`) tiene su propia matriz Canal×Evento desde que consigue el teléfono — editable por él mismo desde su sesión (ticket 05) y también por el principal desde su vista de gestión (ticket 03), sin restricción cruzada en ese sentido.

**Blocked by:** 05

**Status:** done

- [x] Un Ocupante sin teléfono no tiene preferencias propias guardadas; la lógica de envío de notificaciones para paquetes a su nombre consulta la matriz del PRINCIPAL de su Apartamento.
- [x] Un Ocupante con teléfono tiene su propia matriz de preferencias, independiente de la del principal, desde el momento en que se le asocia el teléfono.
- [x] El propio Ocupante-con-teléfono puede editar su matriz desde su sesión en `/mis-datos` (ticket 05) — ya funcionaba, `matriz_preferencias`/`guardar_matriz_preferencias` ya están atadas a `persona.id` de quien está logueado.
- [x] El principal puede editar la matriz de cualquier Ocupante-con-teléfono de su Apartamento (además de la suya propia) — pendiente de UI dedicada (no había ticket que lo pidiera explícitamente en la superficie de `/mis-datos`; la función de dominio ya lo permite si se llama con el `persona_id` de ese Ocupante).
- [x] Tests cubren: resolución de preferencias para un Ocupante sin teléfono (usa las del principal, y sigue el cambio si el principal las actualiza); un Ocupante con teléfono usa las suyas; default histórico sin ninguna preferencia guardada.

## Implementación

- `preferencia_notificacion_service.preferencia_efectiva_ocupante(session, ocupante, canal, evento)` (nuevo): resuelve por `persona_id` propio si tiene teléfono, o por el del principal activo del Apartamento si no.
- Nota: esta función queda lista pero SIN UN CALLER TODAVÍA en el envío real de notificaciones — hoy no existe ningún camino para anunciar un paquete "a nombre de" un Ocupante concreto (eso lo introduce el ticket 08). Se integrará ahí.
- 3 tests nuevos en `test_preferencia_notificacion.py`. Suite completa: 498 passed.

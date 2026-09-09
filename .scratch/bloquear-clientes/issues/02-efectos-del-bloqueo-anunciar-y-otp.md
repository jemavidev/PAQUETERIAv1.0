# 02 — Efectos del bloqueo: rechaza anunciar y OTP

**What to build:** un guard único en `announce()`, justo después de resolverse `recipient_phone`,
que rechaza el anuncio si la Persona dueña de ese teléfono está bloqueada — cubriendo también, sin
ninguna consulta nueva, la cascada a Ocupantes sin Persona propia del mismo apartamento (vía el
fallback de teléfono de notificación que ya existe). Más el guard en la elegibilidad de OTP.

**Blocked by:** 01 — Núcleo: bloquear / autorizar desbloqueo.

**Status:** ready-for-agent

- [ ] Anunciar con `PERSONA_REGISTRADA` a un teléfono bloqueado se rechaza
- [ ] Anunciar vía `Destinatario.ocupante(...)` a un Ocupante sin Persona propia cuyo Principal está
      bloqueado también se rechaza (cascada)
- [ ] Un co-residente CON Persona propia en la misma unidad que el Principal bloqueado sigue
      pudiendo recibir paquetes con normalidad
- [ ] Pedir OTP se rechaza si está bloqueado y `desbloqueo_autorizado_en` NO está seteado
- [ ] Pedir OTP funciona con normalidad si `desbloqueo_autorizado_en` sí está seteado

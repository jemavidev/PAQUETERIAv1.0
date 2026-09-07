# 02 — Reactivación automática al Recibir un paquete

**What to build:** cuando un paquete anunciado a nombre de un residente en baja administrativa
llega a estado Recibido, el sistema lo reactiva solo — sin que el staff tenga que acordarse de
hacerlo manualmente. La reactivación NO reconecta al residente como Ocupante de ninguna unidad (eso
sigue siendo una acción manual aparte del staff, si corresponde). Recibir un paquete de alguien que
NO está de baja no dispara nada (no-op).

**Blocked by:** 01 (necesita que exista la columna `baja_administrativa_en` y la función
`reactivar_persona`).

**Status:** ready-for-agent

- [ ] Hook en `paquete_lifecycle.receive()`, mismo lugar y mismo patrón que la promoción automática
      a Principal (`promover_al_recibir`) — se dispara DESPUÉS de la transición exitosa a Recibido,
      nunca bloquea ni falla el recibo en sí.
- [ ] El hook resuelve la Persona destinataria directo por `Paquete.recipient_phone` (mismo patrón
      que `notificacion_service.resolver_destino_notificable`) — NO por el Ocupante activo de la
      unidad (`resolver_ocupante_de_paquete`), porque alguien de baja administrativa ya no tiene
      Ocupante activo por definición.
- [ ] Si esa Persona tiene `baja_administrativa_en` seteado, se llama a `reactivar_persona` —
      limpia el estado, no reconecta ningún Ocupante.
- [ ] Recibir un paquete de un destinatario que NO está de baja no modifica nada en `Persona` (no
      hay reactivación de la que hablar).
- [ ] Recibir un paquete cuyo destinatario no resuelve a ninguna Persona (sin teléfono, o teléfono
      que no coincide con ninguna) no falla ni lanza error — mismo criterio best-effort que
      `promover_al_recibir`.
- [ ] Tests en la máquina de estados de `Paquete` (dondequiera que vivan hoy los tests de
      `receive()`/`promover_al_recibir`): reactivación automática al recibir un paquete a nombre de
      alguien de baja; no-op para alguien que no estaba de baja; no reconecta ningún Ocupante como
      side-effect.

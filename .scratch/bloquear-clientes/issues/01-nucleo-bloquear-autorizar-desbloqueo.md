# 01 — Núcleo: bloquear / autorizar desbloqueo

**What to build:** las columnas nuevas en `Persona` (`bloqueado_en`, `desbloqueo_autorizado_en`,
`terminos_aceptados_en`, motivo) y las acciones de staff — bloquear (con motivo obligatorio del
catálogo) y autorizar desbloqueo — desde la ficha del residente, junto a "dar de baja"/"reactivar",
con un indicador visual del estado para que el staff vea de un vistazo quién está bloqueado.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Staff bloquea a un residente, exigiendo un `motivo_bloqueo_id`
- [ ] Staff autoriza el desbloqueo de un residente ya bloqueado
- [ ] Autorizar desbloqueo sin que la persona esté bloqueada se rechaza
- [ ] Cualquier rol de staff puede bloquear/autorizar desbloqueo (no exclusivo de admin)
- [ ] La ficha/listado de residentes muestra un indicador visual de "bloqueado"
- [ ] Bloquear a una Persona no afecta ningún paquete ya anunciado/recibido/entregado antes del
      bloqueo

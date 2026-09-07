# 03 — Supresión de notificaciones mientras está de baja

**What to build:** un residente en baja administrativa deja de recibir notificaciones (SMS) de
eventos de sus paquetes (Recibido/Entregado/Cancelado). Si el destinatario está de baja, el sistema
cae al mismo fallback que ya existe hoy para un destinatario inalcanzable (notificar al Anunciante
en su lugar) — salvo que el Anunciante TAMBIÉN esté de baja, en cuyo caso tampoco se le notifica a
él.

**Blocked by:** 01 (necesita que exista la columna `baja_administrativa_en`).

**Status:** ready-for-agent

- [ ] `notificacion_service.resolver_destino_notificable`: el candidato Destinatario (resuelto por
      `recipient_phone`) se descarta si tiene `baja_administrativa_en` seteado, cayendo al mismo
      fallback existente hacia el Anunciante.
- [ ] El candidato Anunciante (fallback) también se descarta si tiene `baja_administrativa_en`
      seteado, además del filtro de `eliminado_en` que ya tenía.
- [ ] Si tanto el Destinatario como el Anunciante están de baja (o inalcanzables por cualquier otro
      motivo ya existente), no hay notificación que enviar — mismo comportamiento que hoy cuando no
      queda nadie notificable.
- [ ] Un residente que NO está de baja sigue notificándose con normalidad — sin cambio de
      comportamiento para el caso activo.
- [ ] Tests (`tests/data_model/test_notificacion_service.py`, prior art: los tests existentes que ya
      cubren el fallback a Anunciante para un destinatario anonimizado/inalcanzable): destinatario
      de baja no es notificable y cae al Anunciante; Anunciante de baja tampoco es candidato;
      residente activo sigue notificándose igual que siempre.

# 02 — Pantalla admin con pestañas SMS / Email / WhatsApp por evento

**Qué construir:** `/administracion/notificaciones` (misma ruta, mismo gate `require_admin`) se rediseña: en vez de una lista plana de 8 filas SMS, muestra 8 grupos (uno por evento/motivo: `ANUNCIADO·Cliente`, `ANUNCIADO·Staff`, `RECIBIDO`, `ENTREGADO`, `CANCELADO`×cada motivo), cada uno con 3 pestañas — SMS / Email / WhatsApp. Cada pestaña guarda de forma independiente usando `guardar_plantilla`/`obtener_texto_actual` (ticket 01) con su propio `canal`. La pestaña Email agrega un campo de Asunto además del cuerpo. Las pestañas SMS y WhatsApp mantienen el formato actual: textarea + lista de variables disponibles sin resolver (`{recipient_name}`, `{access_code}`, `{motivo}` según el evento).

**Bloqueado por:** 01.

**Estado:** ready-for-agent

- [ ] La pantalla muestra las 8 filas de evento/motivo, cada una con 3 pestañas (SMS/Email/WhatsApp).
- [ ] Cada pestaña de canal muestra su propio texto vigente (personalizado o default), independiente de los otros 2 canales del mismo evento.
- [ ] La pestaña Email incluye un campo de Asunto (además del cuerpo) que se guarda junto con el texto.
- [ ] Guardar el texto/asunto de un canal de un evento no altera lo guardado en los otros canales del mismo evento.
- [ ] Las pestañas SMS y WhatsApp siguen mostrando la lista de variables disponibles para ese evento, sin resolver.
- [ ] Gate de permisos sin cambios: sin sesión redirige a `/ingresar`; `OPERADOR` recibe 403; `ADMIN` accede.
- [ ] `tests/web/test_admin_notificaciones.py` extendido cubre: las 3 pestañas aparecen por cada evento/motivo; guardar Email de un evento no toca el SMS del mismo evento; el gate de permisos sigue pasando.
- [ ] Suite completa (`pytest`) pasa.

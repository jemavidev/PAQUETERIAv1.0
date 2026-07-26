# 02 — Pantalla de ADMIN para editar plantillas de notificación

**Qué construir:** `/administracion/notificaciones` (solo `ADMIN`) lista una fila por evento (y por motivo, en el caso de `CANCELADO`) con su texto actual (personalizado o el default), y permite editarlo y guardarlo.

**Bloqueado por:** 01 (necesita la tabla de plantillas).

**Estado:** ready-for-agent

- [ ] Ruta protegida por `require_admin` (mismo patrón que `/administracion/personal`).
- [ ] Lista todos los eventos que notifican (`ANUNCIADO`, `RECIBIDO`, `ENTREGADO`) + una fila por cada `MotivoCancelacion` para `CANCELADO`.
- [ ] Cada fila muestra el texto actual (personalizado si existe, si no el default) y un formulario para guardarlo.
- [ ] Guardar crea o actualiza la plantilla de ese `(evento, motivo)`.
- [ ] `tests/web/test_admin_notificaciones.py` (nuevo): solo ADMIN accede; guardar persiste; sin plantilla previa, el campo muestra el default como valor inicial.
- [ ] Suite completa (`pytest`) pasa.

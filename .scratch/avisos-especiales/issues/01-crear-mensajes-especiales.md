# 01 — Crear mensajes especiales en Notificaciones

**What to build:** El Admin ve en `/administracion/notificaciones` una sección nueva, "Mensajes especiales", con la lista de los
mensajes guardados (nombre y extracto del texto). Puede crear uno nuevo con un nombre ("Fin de semana") y un solo
texto que sirve para SMS y WhatsApp. Mientras escribe ve una vista previa con datos de ejemplo y el número de
caracteres. El mensaje queda guardado y su creación queda en un historial append-only (como el de las demás
plantillas).

Ver spec: Implementation Decisions (MensajeEspecial, MensajeEspecialHistorial) y User Stories 52-57, 61-63.

**Blocked by:** None — can start immediately

**Status:** done (2026-10-11)

- [x] La sección "Mensajes especiales" aparece en `/administracion/notificaciones` solo para Admin; el Staff no Admin recibe el mismo rechazo que en el resto de la pantalla
- [x] Crear un mensaje con nombre y texto lo guarda y lo muestra en la lista
- [x] Nombre obligatorio y único entre los mensajes no eliminados (sin distinguir mayúsculas); el duplicado se rechaza con un mensaje claro
- [x] Texto obligatorio; solo se aceptan las variables `{nombre}` y `{codigos}`, cualquier otra llave entre `{}` se rechaza al guardar con un mensaje claro
- [x] La vista previa resuelve `{nombre}` y `{codigos}` con datos de ejemplo y muestra el conteo de caracteres, con un aviso visible al pasar de 160 (más de 1 SMS)
- [x] La creación queda en el historial con usuario, fecha y el texto nuevo
- [x] Migración Alembic para las tablas nuevas (mensaje con eliminación lógica + historial)
- [x] Pruebas por HTTP (TestClient), siguiendo el patrón de `test_admin_notificaciones.py` y de los catálogos de motivos

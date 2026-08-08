# 64 — Correo de recuperación de contraseña de staff: HTML profesional + remitente con nombre

**Pedido original (cliente):** "con relacion a las vistas de '/ingresar y
/entrar' necesito trabajar en el envio del correo de recuperacion de
contraseña, me inficas que tenemos en este momento y que es necesario para
enviar un mensaje mas completo y profesional orientado solamente al
restablecimiento de contraseñas" — seguido de la confirmación: cambiar el
texto a "Recibimos una solicitud para restablecer tu contraseña.", agregar
HTML con el logo de PAPYRUS, remitente "PaqueteX - Papeleria Papyrus".

**Status:** implementado

## Contexto

El correo (`/staff/olvide-password` → `/staff/restablecer-password`) era
texto plano puro (`MIMEText(cuerpo)` sin tipo, 3 líneas + un link pelado),
sin logo, sin botón, sin nombre del destinatario. Encontré un
`src/templates/emails/password_reset.html` con un diseño HTML armado, pero
es del sistema LEGACY de este mismo repo (facturación/CUFE) -- no lo usa
ningún código de la reconstrucción, y ese sistema ni siquiera corre en el
servidor de PaqueteX. Sirvió de referencia de forma, no se reutilizó tal
cual.

## Implementación

**`EmailSender` (puerto de dominio, `app/domain/email_sender.py`)**: gana
un parámetro opcional `cuerpo_html` -- `ConsoleEmailSender` (test/consola)
lo captura sin usarlo.

**`SmtpEmailSender`/`_enviar_correo` (`app/domain/smtp_email_sender.py`)**:
con `cuerpo_html`, arma un `multipart/alternative` (texto plano PRIMERO,
HTML AL FINAL -- RFC 2046, el cliente de correo elige la ÚLTIMA parte que
sepa mostrar) en vez de un único `MIMEText`. El remitente pasa de mostrar
solo la dirección cruda a `formataddr(("PaqueteX - Papelería Papyrus",
from_email))` -- nombre confirmado por el cliente, vive en código (decisión
de producto) separado de `SMTP_FROM_EMAIL` (la dirección real, config de
infraestructura).

**`app/web/password_reset.py`/`app/web/routes/password_reset.py`**
(capa de wiring + ruta): `StagingOverrideEmailSender.enviar` y
`enviar_en_segundo_plano` propagan `cuerpo_html`. Texto plano actualizado
("Recibimos una solicitud para restablecer tu contraseña." -- sin "de
staff de PAQUETEX"). Nueva `_cuerpo_correo_reset_html(nombre, token)`:
logo de PAPYRUS (`{public_base_url()}/static/branding/papyrus-logo.png`,
mismo dominio que ya resuelve el enlace), saludo personalizado con el
nombre del `Usuario` (`html.escape()`'d -- nunca confiar en texto libre
sin escapar dentro de HTML, aunque acá el "atacante" solo se mandaría el
correo a sí mismo), botón real con el link de respaldo debajo, mismos
avisos de vigencia/un solo uso/ignorar-si-no-fuiste-tú que la versión
plana. Estilos 100% inline (`<style>`/clases CSS no son confiables en
clientes de correo).

## Verificación

- `tests/data_model/test_smtp_email_sender.py` (nuevo, mismo patrón que
  `test_twilio_sender.py` -- `smtplib.SMTP` reemplazado por un doble):
  sin HTML manda un solo part de texto plano; con HTML arma
  `multipart/alternative` con las dos partes en el orden correcto; el
  remitente decodificado (RFC 2047 -- el nombre con tilde va encoded en el
  header crudo) es exactamente el confirmado; sin configuración completa
  sigue fallando igual que antes.
- `tests/web/test_password_reset.py`: test nuevo verifica que el HTML
  llega con el logo, el nombre (`ADMIN` -- normalizado a mayúsculas por la
  capa de dominio, issue 32), el enlace, y el texto exacto pedido; el
  texto plano de respaldo sigue sin la frase vieja.
- Suite completa (`tests/data_model tests/web`): 642/642, sin regresiones.
- Sin clases Tailwind nuevas (el email no pasa por ese pipeline) -- no
  hizo falta recompilar `tailwind.css`.
- Pendiente: desplegar y pedir un restablecimiento real en
  `test.papyrus.com.co` para confirmar que el correo llega con el
  render esperado en un cliente de correo real (Gmail/Outlook/etc. -- algo
  que ningún test automatizado puede confirmar).

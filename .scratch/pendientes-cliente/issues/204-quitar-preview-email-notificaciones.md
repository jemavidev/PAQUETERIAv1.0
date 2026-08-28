# 204 — `/administracion/notificaciones`: quitar vista previa de Email

**Pedido original (Jesús, en sesión, mensaje intermedio mientras se
armaba el issue 205):** "Tambien remueve el preview de email, ya que esta
opcion seria mas relista" — en el contexto de pedir "enviar mensaje" de
prueba por SMS/Email/WhatsApp ([[205-notificaciones-enviar-prueba]]): un
envío real de prueba deja obsoleto el iframe con datos de ejemplo
(`Juan Pérez`) que servía de aproximación.

**Status:** implementado

## Implementación

- `admin/notificaciones.html`: se quitó el bloque "Vista previa (con datos
  de ejemplo)" + `<iframe srcdoc="{{ c.preview_html }}">` de cada panel de
  Email.
- `admin.py` (`_canales_de`): se quitó el campo `preview_html` del dict de
  cada canal y la función `_preview_html_de` que lo construía; imports
  ahora sin uso (`resolver_plantilla`, `variables_ejemplo` de
  `notificacion_service`, `envolver_html` de `plantilla_email_html`,
  `public_base_url` de `..config`) se quitaron de `admin.py`.
- `variables_ejemplo`/`resolver_plantilla`/`envolver_html` NO se tocaron en
  el dominio (`notificacion_service.py`, `plantilla_email_html.py`) — tienen
  su propia suite (`tests/data_model/test_plantilla_email_html.py`) y
  `envolver_html` está documentada como la MISMA función que usará el envío
  real de Email el día que se conecte (issue 205), así que sigue siendo
  código vivo, solo dejó de tener un caller en `admin.py`.

## Verificación

- 2 tests de preview en `test_admin_notificaciones.py` se quitaron
  (`test_pestana_email_muestra_preview_con_datos_de_ejemplo`,
  `test_preview_de_un_evento_cancelado_usa_su_propio_motivo`) junto con el
  helper `_primer_srcdoc` -- ya no hay nada que verificar ahí. El resto (16
  tests) sigue pasando.
- Verificado en vivo contra el servidor de dev local: 0 `<iframe>`, 0
  menciones de "Vista previa" en el HTML resultante.

## Pendiente

- Deploy a test.papyrus.com.co (junto con [[205-notificaciones-enviar-prueba]]
  cuando esa quede lista).

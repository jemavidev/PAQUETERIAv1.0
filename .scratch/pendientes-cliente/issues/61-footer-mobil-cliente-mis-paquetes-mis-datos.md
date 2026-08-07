# 61 — Footer móvil de cliente logueado: Anunciar, Mis paquetes, Mis datos, Whatsapp

**Pedido original (cliente):** "necesito que en el footer de la version
mobil solamente incluyas estos enlaces 'Anunciar, Mis Paquetes, Mis Datos
y Whatsapp'."

**Status:** implementado

## Contexto

El footer móvil (`.footer-nav-mobile`) del cliente logueado por OTP era
IDÉNTICO al del visitante público sin sesión: Anunciar/Consultar/Ayuda/
Whatsapp. El pedido es específicamente sobre el cliente logueado --
Consultar/Ayuda no tienen sentido pedirlos ahí para un anónimo (interpretado
así ya que Mis paquetes/Mis datos no existen sin sesión), así que el
footer PÚBLICO se deja intacto y solo se separa el bloque del cliente.

## Implementación

`app/web/templates/base.html`: el `{% if mostrar_nav_publico or
tiene_persona %}` combinado se separa en dos bloques independientes:

- `{% if mostrar_nav_publico %}` -- sin cambios (Anunciar/Consultar/Ayuda/
  Whatsapp).
- `{% if tiene_persona %}` -- nuevo bloque propio: Anunciar/Mis paquetes/
  Mis datos/Whatsapp.

Consultar queda fuera de este footer para un cliente logueado (sigue
disponible en `.site-nav` de escritorio, issue 59); Ayuda también queda
fuera (no se pidió mantenerla).

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- `tests/web/test_layout.py`: el test que afirmaba "el footer del cliente
  es igual al público" quedó reescrito en dos (uno para el público, sin
  cambios; uno nuevo para el cliente, cubriendo también que Whatsapp
  aparece con `WHATSAPP_SOPORTE_NUMERO` configurado) -- 25/25 en el
  archivo.
- Suite completa (`tests/data_model tests/web`): 636/636, sin regresiones.
- Sin clases Tailwind nuevas -- no hizo falta recompilar `tailwind.css`.
- Pendiente: confirmar en `test.papyrus.com.co`, en un dispositivo móvil
  real logueado como cliente, que el footer muestra exactamente esos 4
  enlaces.

# 447 — Anunciar a un teléfono/usuario de WhatsApp desconocido no ofrece notificar (solicitud de autorización)

**Pedido original (Jesús, 2026-10-11):** "Analiza que pasa cuando se intenta anunciar un paquete de un numero de
telefono o usuario de whatsapp que no existe en los clientes actuales o clientes externos, esto ya que al tratar de
anunciar para uno de estos numeros, no se porque pero no aparece la opcion de notificar al cliente que existe un
paquete para el, que acaba un domiciliario de traerlo y que nosotros necesitamos autorizacion para recibirlo."

**Status:** verificado (local, Jesús 2026-10-11: "el resto de cosas sí están funcionando") — falta desplegar

## Diagnóstico

No era una falla de datos sino una regla escrita a propósito. Para un Teléfono o usuario de WhatsApp que **no** es
Persona (formulario "No encontramos a nadie…", la sugerencia de Contacto externo y "Nuevo residente" dentro de una
unidad), `_info_autorizacion(db, None)` devolvía `(False, None, None)`. El formulario de persona nueva traía
**Anunciar + Recibir** fijos, y la tarjeta de Contacto externo forzaba Recibir (`nombre_a_registrar`), con el
argumento de que "no hay bandera que consultar". Pero anunciar registra a esa Persona con
`autoriza_recepcion_automatica=False` (el default). El caso que más necesita el pedido de autorización (alguien que
nunca ha recibido aquí) era el único que no lo ofrecía.

## Decisiones

- Misma regla que una Persona registrada con la bandera apagada: **Anunciar + Pedir autorización** (WhatsApp con el
  mensaje editable de `/administracion/notificaciones`), sin Recibir directo.
- `announce_new._solicitud_para_identidad_nueva(db, tipo, valor)` arma los links a partir de la identidad tecleada ya
  normalizada (Persona transitoria, nunca se guarda), reusando `_info_autorizacion` → `url_whatsapp`/`_desktop`.
- Aplica en los 3 caminos: `/announce/identificar` (sin match y con sugerencia), `/announce/identificar-sugerencia` y
  `/announce/identificar-contacto` (estado `nuevo`).
- Pruebas: 3 nuevas en `tests/web/test_announce_new.py` (bloque "Issue 447"). Se actualizaron las que fijaban el
  Recibir directo y se quitaron 2 que este cambio deja sin sentido (`test_identificar_sin_match_recibir_esta_cableado`,
  `test_identificar_contacto_sin_match_nunca_muestra_recibir`).

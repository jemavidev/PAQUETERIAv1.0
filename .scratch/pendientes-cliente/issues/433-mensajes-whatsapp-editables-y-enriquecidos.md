# 433 — Mensajes de WhatsApp editables desde `/administracion/notificaciones`, con formato enriquecido

**Pedido original (Jesús):** "agrega la opción a las notificaciones para que se pueda editar en cualquier momento,
recuerda que todas estas ediciones deben manejar los mensajes enriquecidos (negrillas, emojis y más)". Contexto: cómo
asociar los mensajes de `/administracion/notificaciones` a los enlaces de WhatsApp.

**Status:** implementado (local, sin desplegar)

## Contexto

- El botón WhatsApp de `/paquetes` tenía el texto fijo en el código (`packages.py::_mensaje_whatsapp`).
- "Solicitar autorización por WhatsApp" (`/announce`) leía una `PlantillaNotificacion` (`PEDIR_AUTORIZACION`,
  WhatsApp), pero no había pantalla para editarla.
- La pestaña WhatsApp de cada estado en `/administracion/notificaciones` se guardaba pero nadie la usaba: las
  notificaciones automáticas solo salen por SMS, con el texto de la pestaña SMS.

## Decisiones (las recomendadas; Jesús pidió avanzar)

- Un texto por estado: la pestaña **WhatsApp** de Anunciado/Recibido/Entregado/Cancelado es el mensaje del botón
  WhatsApp de `/paquetes` según el estado del paquete. Mismas variables: `{recipient_name}`, `{access_code}`,
  `{estado}`, `{link}`, `{motivo}`. Sin editar, el texto de siempre del botón (con negrillas y tildes); Cancelado
  agrega el motivo.
- Fila nueva **"Solicitud de autorización"**, solo pestaña WhatsApp, sin variables (no hay paquete todavía).
- `/residentes`, modal Ver y footer: chat vacío, sin plantilla.
- Formato enriquecido en la pestaña WhatsApp: se guarda y se envía tal cual (negrillas `*`, cursiva `_`, tachado
  `~`, monoespaciado, emojis, tildes, saltos de línea). El SMS no cambia (sigue sin tildes, issue 288). En el editor:
  botones de formato, todas las variables a la vista, contador de 500 caracteres (tope de la columna) y una vista
  previa estilo WhatsApp que se actualiza mientras se escribe.
- Validación al guardar en WhatsApp: variable desconocida o más de 500 caracteres se rechaza con mensaje, en vez de
  guardar un texto que fallaría al usarse.

## Verificación

- `tests/data_model/test_whatsapp_mensajes_editables_dominio.py` (8) y `tests/web/test_whatsapp_mensajes_editables_web.py`
  (6): botón de /paquetes con la pestaña editada (emoji, negrilla, salto de línea en el enlace), default igual al texto
  de siempre del botón, Cancelado con motivo, SMS sin cambios, fila "Solicitud de autorización" solo WhatsApp y usada
  por /announce, `\r\n` normalizado, variable desconocida / >500 rechazados, botones de formato y vista previa.
- Ajustadas a propósito (decisión cambiada): 5 filas con WhatsApp en vez de 4; el default de WhatsApp ya no es igual
  al del SMS; "Variables disponibles" solo en SMS.
- Notificaciones, plantillas, historial, /announce, notifications y WhatsApp de /paquetes: 237 + 19 en verde.
- Vista previa en vivo (JS) comparada con el filtro de Python sobre el mismo texto: HTML idéntico. Sin clases de
  Tailwind nuevas.

## Ajuste (Jesús, 2026-09-27)

- "cambia este texto "Solicitud de autorización" por "SOLICITAR AUTORIZACION"": el título de la fila nueva en
  `/administracion/notificaciones` ahora es **SOLICITAR AUTORIZACION** (en mayúsculas, como ANUNCIADO/RECIBIDO/...).

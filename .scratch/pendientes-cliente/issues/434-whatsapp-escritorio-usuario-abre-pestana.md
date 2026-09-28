# 434 — WhatsApp de escritorio: con usuario de WhatsApp se abre una pestaña en vez de la app instalada

**Pedido original (Jesús, 2026-09-28):** "al usar una de tus sugerencias, cierro todo y presiono el link, si se usa
número de teléfono para WhatsApp, abre el Chrome app y puedo enviar el mensaje correcto, pero si este tiene usuario de
WhatsApp en vez de número, se abre una ventana nueva en el mismo navegador, no sé cómo podrías corregirlo". Luego:
"retomemos lo de WhatsApp, cómo puedes solucionar esto".

**Status:** implementado (local, sin desplegar)

## Causa

`persona_service.url_whatsapp_desktop` le daba prioridad al usuario de WhatsApp sobre el teléfono (misma regla que el
enlace de celular, issue 67). Con usuario armaba `https://wa.me/<usuario>`, porque `web.whatsapp.com/send` solo acepta
números. `wa.me` no está dentro del alcance de la app instalada de WhatsApp Web, así que Chrome lo abre en una pestaña.

## Decisiones

- En escritorio, si la persona tiene teléfono, el enlace usa el teléfono (`web.whatsapp.com/send?phone=`) aunque también
  tenga usuario: es el único que abre la app instalada. El enlace de celular no cambia (sigue prefiriendo el usuario:
  `wa.me` abre la app del teléfono en ambos casos).
- Si solo tiene usuario (sin teléfono), no hay forma de abrir la app instalada: sigue `wa.me/<usuario>` en una pestaña.
  Para esos contactos la salida es registrarles también el número.
- Riesgo aceptado: si el número guardado no es el de su WhatsApp, WhatsApp Web dirá "número no válido".

## Verificación

- `tests/data_model/test_persona_service.py`: la de "prioriza el usuario" pasa a "prioriza el teléfono" en escritorio
  (fallaba antes del cambio), + contacto con solo usuario sigue en `wa.me`. `test_customers_manage.py`: la tabla de
  /residentes con usuario + teléfono arma el enlace de escritorio con el teléfono. 248 + 33 (WhatsApp de /paquetes,
  /announce, footer, notificaciones) en verde.

# 435 — Los emojis del mensaje de WhatsApp llegan como "�" (los daña la redirección de wa.me)

**Pedido original (Jesús, 2026-09-28):** probando en localhost con un contacto de usuario de WhatsApp, el enlace terminó
en `https://api.whatsapp.com/send/?text=Hola+%2ATEST+3%2A%0A%0A%EF%BF%BD+Tu+paquete...&username=...&type=username` y el
mensaje mostró "Hola *TEST 3* � Tu paquete *Y5U8* está *Recibido*...": el 📦 de la plantilla llegó como "�".

**Status:** verificado — probado por Jesús en localhost (escritorio + celular) el 2026-10-07 y desplegado en producción (elclub, `ef434cf` del repo de deploy, 2026-10-07); test.papyrus.com.co ya no existe

## Causa (comprobada con curl)

- La plantilla está bien guardada (el 📦 está intacto en la BD) y PaqueteX lo codifica bien (`%F0%9F%93%A6`).
- `wa.me` responde 302 a `api.whatsapp.com/send/` y en esa redirección reemplaza todo carácter de 4 bytes (emojis) por
  `%EF%BF%BD` (�). Las tildes (2 bytes) pasan bien. Pasa con número y con usuario, en celular y escritorio.
- Entrando directo a `api.whatsapp.com/send/?...&text=%F0%9F%93%A6...`, el botón "Continuar al chat" conserva el emoji
  intacto (solo la vista previa de esa página muestra "�").
- `api.whatsapp.com` está declarado como enlace verificado de la app en Android (`assetlinks.json`, `com.whatsapp`) y en
  iOS (`apple-app-site-association`, rutas `*`), igual que `wa.me`.

## Decisiones

- Todo enlace que hoy sale como `wa.me/...` con mensaje pasa a `https://api.whatsapp.com/send/?phone=<n>&type=phone_number`
  o `?username=<u>&type=username`, + `&text=`: el mismo destino al que redirige `wa.me`, sin la redirección.
- `web.whatsapp.com/send?phone=` (escritorio con número, abre la app instalada) no cambia.
- Falta confirmar en celular (Android) que `api.whatsapp.com` abre la app como `wa.me`.

## Verificación

- `persona_service.url_click_to_chat` arma el enlace directo; lo usan `url_whatsapp` (celular), el caso "solo usuario"
  de `url_whatsapp_desktop` y el teléfono crudo del snapshot en `/paquetes`. El footer de soporte sigue en `wa.me`
  (no lleva mensaje, no le afecta).
- `test_url_whatsapp_no_pasa_por_wa_me_para_no_danar_los_emojis` (fallaba con el código anterior). 32 aserciones que
  esperaban `wa.me` pasadas a `api.whatsapp.com/send/`. Personas, /announce, /residentes, /paquetes, layout, footer y
  WhatsApp: 658 + 4 en verde.

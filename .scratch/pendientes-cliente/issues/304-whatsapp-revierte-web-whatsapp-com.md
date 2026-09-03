# 304 — Revierte [[301]]: `web.whatsapp.com` no abre la app en ningún dispositivo probado

**Pedido original (cliente):** reportó en vivo, tras [[301]] desplegado,
que los enlaces de WhatsApp no abrían la app -- ni desde Chrome de
escritorio, ni desde Android con WhatsApp nativo instalado. Confirmó
ambos casos explícitamente al preguntársele.

**Status:** verificado

## Causa -- la premisa de [[301]] era la inversa de la realidad

El documento de especificación que motivó [[301]] pedía evitar `wa.me`
asumiendo que impedía la captura por la PWA. Verificado en vivo con el
propio cliente en 2 dispositivos reales:

- **Android, WhatsApp nativo instalado**: el sistema operativo solo
  reconoce `wa.me` (y `api.whatsapp.com`, el mismo mecanismo por debajo)
  como "enlace verificado" de la app -- es el mecanismo oficial de Meta
  para "Click to Chat". `web.whatsapp.com` nunca estuvo registrado para
  eso; es el dominio del cliente WEB (pensado para vincular sesión por
  QR desde una compu), así que el celular lo trata como página normal.
- **Chrome de escritorio**: `web.whatsapp.com` solo abre la app instalada
  bajo una configuración manual de 3 pasos por dispositivo (`chrome://apps`
  -> clic derecho -> "Abrir como ventana" + decirle a Chrome que abra
  siempre ese dominio ahí) -- nada de esto pasa por default, y no es
  razonable esperar que usuarios finales lo configuren.

Se evaluaron 2 alternativas adicionales que el cliente trajo:
- `api.whatsapp.com/send?phone=...&text=...` -- funcionalmente idéntico a
  `wa.me` (mismo mecanismo, wa.me es su alias corto oficial), válida pero
  sin ninguna ventaja real sobre mantener `wa.me`.
- `whatsapp://send?phone=...&text=...` (URI scheme directo) -- descartada:
  sin fallback si el destinatario no tiene WhatsApp instalado (el link
  simplemente no abre nada), y no es un mecanismo oficialmente documentado
  por Meta.

## Fix

Revierte el dominio del camino de teléfono de `web.whatsapp.com/send?
phone=` de vuelta a `wa.me/<dígitos>` en los 3 puntos que [[301]] cambió
(`persona_service.url_whatsapp`, `packages._whatsapp_url_destinatario`,
footer de `base.html`) -- se mantiene la limpieza con `re.sub(r"\D","",...)`
(mejora real sobre el `.lstrip('+')` original). El camino de username
(`whatsapp_usuario`) no se tocó -- ya estaba en `wa.me` desde antes y
nunca fue parte del problema. Simplificado de paso el combinador de
`?text=` en `packages.py` (ya no hace falta el `&` defensivo que [[301]]
había agregado, ningún dominio vuelve a traer `?` propio). `target=
"_blank"` retirado en [[301]] se queda retirado -- esa parte nunca fue
el problema, sigue siendo la práctica correcta.

## Verificación

- Suites (`test_persona_service.py`, `test_layout.py`,
  `test_customers_manage.py`, `test_packages.py`): **415 passed**.
- Verificado en vivo (dev local, sesión real de staff): `/residentes`
  vuelve a mostrar `wa.me/573008103849` (antes `web.whatsapp.com/send?
  phone=...`) para el residente solo-teléfono; usuarios con
  `whatsapp_usuario` siguen intactos en `wa.me/<user>`.

Desplegado a `test.papyrus.com.co` 2026-09-03 (CI `jemavidev/PaqueteX` run
33814965989, tests + deploy success) y confirmado en vivo: el enlace
público del footer (`/anunciar`) ya resuelve a `wa.me/573334004007`.
Pendiente: que el cliente confirme en su propio Android que ya abre la
app de verdad (esa parte no se puede probar por curl).

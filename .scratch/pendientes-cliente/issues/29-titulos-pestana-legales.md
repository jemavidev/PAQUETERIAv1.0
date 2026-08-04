# 29 — Títulos de pestaña de /terms, /privacy, /cookies

**Pedido original (cliente):** "a estos 3 puedes colocarle nombres en
español dejando así 'Cookies, Términos y Condiciones, Políticas de
Privacidad'" → corrección inmediata: "Política de Cookies" (no solo
"Cookies").

**Vistas:** `terms/form.html`, `privacy/form.html`, `cookies/form.html`.

**Status:** verificado

## Qué se hizo

Los H1 y las tarjetas legales de `/ayuda` YA usaban exactamente "Política
de Cookies", "Términos y Condiciones", "Políticas de Privacidad"
(confirmado con `grep`) -- el único desajuste real estaba en el `<title>`
de cada página (la pestaña del navegador), que había quedado en minúsculas
y/o singular:

- `/terms`: "Términos y condiciones" → "Términos y Condiciones"
- `/privacy`: "Política de privacidad" → "Políticas de Privacidad"
- `/cookies`: "Política de cookies" → "Política de Cookies"

## Verificación

- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo (título de
      pestaña del navegador en las 3 vistas).

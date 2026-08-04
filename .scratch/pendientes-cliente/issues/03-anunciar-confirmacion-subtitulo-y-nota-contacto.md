# 03 — `/anunciar` confirmación: subtítulo ampliado + nota de contacto bajo el código

**Pedido original (cliente):** "esto tambien te lo habia pedido — MOBILE: Se
ve bastante bien, limpio y sencillo. Modifica el mensaje que aparece en la
descripcion, lo vas a cambiard de 'Guardá este código — lo vas a necesitar
para consultar el estado.' a 'Guardá este código — lo vas a necesitar para
consultar el estado y reclamar tu paquete.'. Necito que en la parte inferior
de donde aparecio el codigo la seccion 'mt-4 rounded-xl border-2
border-dashed border-blue-200 bg-blue-50 py-4' incluyas este texto de asi
mismo como esta la seccion 'text-sm text-slate-500 mt-1', incluye esto 'Nos
pondremos en contacto contigo para confirmarte al recibirlo.'"

**Vista:** `announce/confirmacion.html` (recibo de éxito tras anunciar un
paquete desde `/anunciar`).

**Status:** verificado

## Qué se hizo

- Subtítulo cambiado a "Guardá este código — lo vas a necesitar para
  consultar el estado y reclamar tu paquete."
- Nueva nota bajo el bloque del código, mismas clases que el subtítulo
  (`text-sm text-slate-500 mt-1`): "Nos pondremos en contacto contigo para
  confirmarte al recibirlo."
- `confirmacion_exito()` (`components/_confirmacion.html`) ganó un parámetro
  opcional `nota_codigo=none` (mismo patrón que `destacado` en los tickets
  01/02) — sin romper el único caller real de hoy.

## Verificación

- [x] Render local confirma ambos textos con las clases correctas.
- [x] 8/8 `test_announce.py`, 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `3c2d5cb`) y confirmado en
      vivo vía `POST /anunciar`: ambos `<p class="text-sm text-slate-500
      mt-1">` aparecen con el texto correcto.

## Comments

- 2026-08-01: segundo pedido que el cliente reporta como nunca implementado
  ni registrado — confirma que hace falta terminar de formalizar el proceso
  de tracking (ver conversación / próxima actualización de `CLAUDE.md`).

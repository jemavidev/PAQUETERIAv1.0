# 443 — Enlace "Bancos" en el header de Staff/Admin

**Pedido original (Jesús, 2026-10-10):** "El enlace es https://facturas.papyrus.com.co/bancos, el texto es 'Bancos' y
solo necesito que Staff/Admin sean los únicos que lo vean, restringiendo la visualización de Público/Residente, este
debe quedar posicionado al lado derecho de 'Consultar', ilústrate con relación al ícono."

**Status:** verificado (local, Jesús 2026-10-10: "se ve bien y funciona como debe") — desplegado en producción (elclub, `bcd94f7` del repo de deploy, 2026-10-10); **confirmado en producción por Jesús (2026-10-10: "está funcionando al pelo")**

## Decisiones

- Va en la barra `.site-nav` del bloque `tiene_staff` de `base.html`, justo después de Consultar. Las barras pública
  y de residente no cambian.
- Ícono nuevo `banco` en `ICONOS_NAV` (Heroicons outline "building-library", el edificio con columnas).
- Abre en la **misma pestaña** (`_self`, el comportamiento normal de un enlace). Al principio se puso `_blank`, pero
  Jesús pidió cambiarlo (2026-10-10): "es necesario que al hacer click esto sea _self y no _blank".
- Celular (pedido de Jesús, 2026-10-10: "en la vista móvil remueve Consultar y reemplázalo con Bancos, en la misma
  posición"): en el footer móvil del Staff, Bancos ocupa el 2.º lugar donde estaba Consultar → Anunciar · Bancos ·
  Paquetes · Residentes. En el celular, el Staff ya no tiene Consultar en el footer; los footers público y de residente
  no cambian.

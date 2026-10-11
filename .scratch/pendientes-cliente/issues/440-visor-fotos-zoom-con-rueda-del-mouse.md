# 440 — Zoom con la rueda del mouse en el visor de fotos (escritorio)

**Pedido original (Jesús, 2026-10-07):** "de qué forma podría usar el scroll del mouse para hacer zoom in/out? es
posible que me ayudes con esto?"

**Status:** verificado — desplegado en producción (elclub, `480e9a3` del repo de deploy, 2026-10-07); **confirmado en producción por Jesús (2026-10-11)**

## Decisiones

- `components/_visor_fotos.html`: la rueda del mouse sobre la foto ampliada acerca/aleja (1x-4x, el mismo rango que
  el pinch del celular), centrado en el punto donde está el cursor.
- Con zoom activo, arrastrar con el mouse mueve la foto (sin eso el zoom no sirve en escritorio: no hay forma de ver
  el resto). Cursor de mano (`grab`/`grabbing`) mientras hay zoom; lupa (`zoom-in`) sin zoom.
- Al pasar de foto (flechas, teclado) el zoom vuelve a 1x, como ya pasa con el swipe.

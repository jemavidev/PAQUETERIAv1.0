# 439 — Flechas para pasar entre fotos en el visor (escritorio)

**Pedido original (Jesús, 2026-10-07):** "para los controladores de las imágenes puedas agregar unas flechas para ir
pasando entre imágenes, esto especialmente en la versión de desktop, mejora esta experiencia de usuario".

**Status:** verificado — probado por Jesús en localhost el 2026-10-07 y desplegado en producción (elclub, `baa751c` del repo de deploy, 2026-10-07)

## Decisiones

- Visor único `components/_visor_fotos.html` (lo usan `/consultar` y la vista del residente `customer/paquetes.html`).
- Flechas ‹ › a los lados de la foto ampliada, solo con más de una foto, y **solo desde `md` (escritorio/tablet)**: el
  2026-08-06 el cliente pidió quitar los botones anterior/siguiente en celular y dejar solo el swipe; eso se respeta.
- Al hacer clic, la foto pasa con la misma animación de salida/entrada que el swipe. Teclado (← →) sigue igual.

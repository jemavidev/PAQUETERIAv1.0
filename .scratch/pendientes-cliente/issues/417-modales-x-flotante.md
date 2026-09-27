# 417 — La "x" de cerrar de los modales queda flotante al hacer scroll

**Pedido original (Jesús, 2026-09-27):** "cada uno de los modales que manejas tienen una "x" en la parte superior derecha,
necesito que esta x sea flotante [...] algunos modales tienen el scroll invisible para subir y bajar para ver mas contenido,
lo que pasa actualmente es que al bajar a ver mas contenido la "x" se queda en la parte superior [...] la "x" necesito que
sea una forma facil y que se sigan manteniendo las otras formas de cerrarlo".

**Status:** implementado (local), pendiente desplegar

## Alcance

- En todos los modales, la "x" sigue visible arriba a la derecha aunque se haga scroll dentro del contenido.
- Las demás formas de cerrar (clic fuera, Escape, botones propios del modal) no cambian.

# 416 — Administración → Posiciones: desactivar filas del estante

**Pedido original (Jesús, 2026-09-27):** "lo que necesito ahora es que generes una forma para desactivar las filas,
posiblemente desactivar filas 1 y 2, o solo desactivar 4 y 7, la idea es que en caso que se desactive no sea posible
seleccionarla en la lista del modal de recibir, este nuevo controlador necesito que lo agregues a una nueva vista para el
administardor llamado posicion..... lo que pido es tan sensillo como te lo digo". Sigue a `.scratch/posicion-almacenamiento`.

**Status:** verificado (desplegado en test `f17c396`, confirmado por Jesús 2026-09-27)

## Alcance

- Vista nueva solo ADMIN, **Administración → Posiciones** (`/administracion/posiciones`): las 7 filas del estante, cada una
  con un interruptor activa/desactivada. Una fila = sus dos lados (x1 y x2).
- Fila desactivada: en el modal Recibir sus dos botones salen grises y no se pueden elegir; la ruta de Recibir también la
  rechaza (por si llega igual).
- No se puede desactivar la ÚLTIMA fila activa: la Posición es obligatoria al recibir, sin ninguna activa no se podría recibir.
- Los paquetes que ya están en una fila desactivada no cambian (siguen mostrando su "📍 NN").

# 445 — `/paquetes` escritorio con el look de tarjetas del celular (propuesta)

**Pedido original (Jesús, 2026-10-11):** "En la version de dispositivos moviles el ver la lista de paquetes en la vista
/paquetes, estas estan separadas por un espacio entre tarjetas el cual se ve bastante bien, incluyendo sus bordes
redondeados, lo que necesito es que me muestres como se puede aplicar ese mismo look and feel en la version de desktop
de /paquetes."

**Status:** pendiente — prototipo listo, falta que Jesús elija variante

## Prototipo

Rama `prototipo/paquetes-escritorio-tarjetas` (commit `665ddec`, solo local, no va a main), worktree
`/home/stk/Documents/GIT/MATT-prototipo-445`, servido en `http://localhost:8011/paquetes?variante=A..D`, con barra
flotante y flechas ← → del teclado:

- **A**: tabla actual (referencia).
- **B**: filas separadas. La misma tabla con columnas y encabezado, pero cada fila es una tarjeta blanca con aire entre
  filas, bordes redondeados y la franja de color del Estado.
- **C**: tarjetas en cuadrícula. Las mismas tarjetas del celular, en 2 columnas (3 en pantallas anchas), con las
  acciones de escritorio (Ver, Modificar, Cancelar…) al pie.
- **D**: una tarjeta ancha por paquete, en una sola línea: nombre y apartamento · Estado · tiempo | Posición | código |
  acciones.

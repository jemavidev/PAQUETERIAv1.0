# 441 — Tarjeta móvil de `/paquetes`: 4 botones abajo (con el código) y "Asignar apartamento" junto a la Posición

**Pedido original (Jesús, 2026-10-07):** "en la vista de /paquetes en la versión móvil, cada paquete se compone de
(código de acceso, Nombre, ... y en la segunda fila 3 botones), la idea es que en la parte inferior se tengan 4 botones
así mismo como funciona en la vista de /residentes. Los 4 botones que necesito son (WhatsApp, Llamar, Código de Acceso,
Botón para el cambio de estados "Recibir/Entregar") [...] agregues el botón de "Asignar Apartamento" al lado del icono
o sección de "Posición en el estante"". Confirmado: el código es una **reubicación** (sale de la primera fila) y
"Asignar apartamento" se comporta **igual que en escritorio**.

**Status:** verificado — desplegado en producción (elclub, `dc2f001` del repo de deploy, 2026-10-07); **confirmado en producción por Jesús (2026-10-11)**

## Decisiones

- Fila inferior `grid-cols-4`: WhatsApp · Llamar · Código de acceso · Recibir/Entregar (o el apagado de
  Entregado/Cancelado, como hoy). El código se ve como texto con el color de su estado y abre `/consultar?q=`.
- El código sale de la primera fila: el nombre y la línea de dirección/estado quedan con todo el ancho.
- "Asignar apartamento" a la izquierda de la Posición (📍), solo si el paquete no tiene apartamento y está Anunciado o
  Recibido (mismo criterio que la columna de escritorio); en los demás casos no se muestra nada (sigue lo de 345/346:
  nada de 🏠 apagado en celular). Abre el mismo modal `modal-asignar-apto-<id>`.

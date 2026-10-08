# 442 — Colores por Estado en `/paquetes` con más contraste (variante B)

**Pedido original (Jesús, 2026-10-07):** "de qué forma puedes ajustar los colores de fondo de cada estado de los
paquetes, esto ya que se ven muy sutiles y no se diferencian lo suficiente entre alguno de ellos". Luego: "arma varias
alternativas y te diré cuál seleccionar" → eligió **B** ("B se ve bien, impleméntalo").

**Status:** implementado (local, sin desplegar)

## Prototipo

Rama `prototipo/colores-estado-paquetes` (commit `478b214`, solo local, no va a main): 4 paletas sobre `/paquetes`
con `?variante=A..D` — A actual (todo `-100` pastel), **B píldoras sólidas + franja**, C tonos bien separados
(Cancelado gris), D contorno.

## Decisiones (variante B)

- Código de acceso (píldora de la tabla, botón de la tarjeta móvil, título del modal Ver, chip de duración): color
  sólido — Anunciado `amber-400` con texto oscuro, Recibido `blue-600`, Entregado `emerald-600`, Cancelado `red-600`,
  con texto blanco.
- Filas de la tabla: fondo blanco + franja de 6 px a la izquierda con el color del estado (sombra interna, no borde,
  para no correr el contenido); hover suave del color. Ya no hay fondo de color en toda la fila (issue 348, ronda 4:
  el color en un área grande cansaba).
- Tarjeta móvil: blanca, franja izquierda de 8 px (`border-l-8`) con el mismo color sólido.
- Fuera de alcance: el badge de Estado de `_badge.html` (se usa también en `/consultar` y `/mis-paquetes`) y los
  íconos de filtro.

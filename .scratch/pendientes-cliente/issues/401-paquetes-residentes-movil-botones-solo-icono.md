# 401 — `/paquetes` y `/residentes` móvil: botones solo con ícono (sin nombre)

**Pedido original (Jesús):** "en las vistas /paquetes y /residentes, específicamente en la versión móvil ... los
botones ... conserven la misma forma y las mismas dimensiones que tienen ahora, pero vas a remover el nombre (por
ejemplo whatsapp, llamar, recibir...), solo se conserve el ícono relacionado a esta acción". Luego: "podría tener los
íconos un poco más grande ya que no vas a tener las palabras".

**Status:** implementado (localhost), pendiente confirmar en vivo

## Decisiones (acordadas)

- Mismo tamaño, forma y color de cada botón (`h-12`, mismas grillas de 3 y 4); solo se quita el texto.
- Íconos más grandes: /paquetes de 20 a 28 px; /residentes de 14 a 28 px.
- /paquetes: WhatsApp y Llamar apagados hoy no tienen ícono (solo texto) -> mismo ícono en gris.
- /paquetes: tercer botón en estado final (Entregado/Cancelado...) hoy es texto -> ícono de estado en gris.
- El nombre se conserva para lectores de pantalla (`aria-label`) y el motivo del apagado en `title`.
- La tabla de escritorio no cambia.

## Verificación

- Tests ajustados a propósito: `test_paquetes_movil_tarjetas.py` y `test_residentes_movil_tarjetas.py` ahora exigen
  que no haya nombre visible en los botones y que cada uno conserve su `aria-label`. 440 pruebas de vistas relacionadas
  en verde antes del ajuste (solo fallaban esas 2, por el texto quitado); las 8 de tarjetas móviles en verde después.
- Tailwind reconstruido, `?v=106`.

# 431 — La Posición al lado de la píldora del código (modal Ver) y de la de días (/consultar)

**Pedido original (Jesús):** "en la vista /paquetes en el modal "Ver" ubiques la posición "Posición en el estante" al
lado derecho de la píldora con el código de los paquetes. Adicional en la vista /consultar ubiques la posición de
"Posición en el estante" al lado derecho de la píldora con la cantidad de días."

**Status:** implementado (local, sin desplegar)

## Contexto

Ajuste del 427: en el modal Ver el chip quedó junto al badge de estado, y en /consultar en su propia línea encima de
la píldora de días.

## Decisiones

- Modal Ver: el chip "📍 NN" / "Sin ubicación" pasa al título, justo a la derecha de la píldora del código.
- /consultar (con sesión de staff): el chip pasa a la misma línea que la píldora de días, a su derecha. Sin píldora de
  días (no Recibido), no hay chip -- la Posición solo aplica a Recibido.

## Verificación

- `tests/web/test_posicion_visible_staff.py`: las pruebas del 427 ahora exigen el lugar -- en el `<h2>` del modal Ver
  justo después de la píldora del código, y en /consultar justo después de la píldora de días. 9 en verde;
  `/paquetes` + `/consultar`: 298 en verde. Sin clases de Tailwind nuevas.

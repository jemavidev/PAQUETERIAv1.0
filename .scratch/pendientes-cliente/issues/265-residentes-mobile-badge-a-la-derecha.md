# 265 — `/residentes` tab Residentes, mobile: badge (Confirmado/Pendiente/Principal) ajustado a la derecha

**Pedido original (cliente):** "ahora la palabra 'Confirmado, Pendiente
y Principal' que ya están en una píldora, deberían estar ajustadas a la
derecha en la versión mobil."

**Status:** implementado

## Verificación

Suite `test_customers_manage.py`: 213 passed. Clase `flex items-center
justify-between gap-2 sm:justify-start` confirmada renderizada en vivo
(curl contra `/residentes/c75f7cdd-...`, dev local).

## Alcance

`customers_manage/detail.html`, roster de la tab Residentes -- la fila
nombre+badge (`flex items-center gap-2`) hoy deja el badge pegado
justo a la derecha del nombre (issue 254), no al borde derecho de la
tarjeta. Cambio: `justify-between` en esa fila para mobil (`<sm`,
mismo punto de quiebre que issue 264), volviendo a `justify-start` de
`sm:` en adelante (badge otra vez pegado al nombre, comportamiento
actual sin cambios en desktop).

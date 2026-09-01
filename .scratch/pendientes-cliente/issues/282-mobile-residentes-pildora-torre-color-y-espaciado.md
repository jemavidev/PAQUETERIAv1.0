# 282 — Seguimiento a [[281]]: color de la píldora, ocultar "No Asig.", espaciado

**Pedido original (cliente):** "Cambiale el color a la pildora de los
aprtamentos, en caso que no tenga asignado no coloques la pildora con
el valor 'No Asig.', ajusta los margenes/padding de los valores en la
columna de Nombre"

**Status:** implementado

## Alcance

`customers_manage/_resultados.html`, mobile only (celda Nombre de la
tabla plana):

1. Píldora de Torre/Apto ([[281]]): color `slate` (gris) → `indigo`
   (`bg-indigo-50 text-indigo-700 border-indigo-200`) -- mismo color ya
   usado en este archivo para todo lo relacionado a unidad/apartamento
   (el ícono 👫 "comparte apartamento" ya es indigo), consistente con
   el resto del lenguaje visual de la vista.
2. Cuando `p.apartamento` es `None`, la píldora ya NO se renderiza
   (antes mostraba "No Asig."). La fila de badges (Auto/Principal/
   Torre-Apto) vuelve a ser condicional -- se restaura el guard que
   [[281]] había quitado (Torre/Apto dejó de ser incondicional), ahora
   cubriendo las 3 píldoras: si ninguna aplica, no se renderiza ni el
   wrapper vacío.
3. Espaciado en la celda Nombre: gap entre la fila del nombre y la fila
   de píldoras, y entre píldoras entre sí, sube de `gap-1` a `gap-1.5`;
   padding interno de las píldoras sube de `px-1.5` a `px-2` en mobile
   (antes solo desde `sm:`) -- más aire ahora que la columna Torre/Apto
   completa quedó liberada desde [[281]].

## Verificación

Iframes same-origin en dev local a 360/375/390/414px (mismo método de
[[277]]-[[281]]): 0px de overflow en los 4. Confirmado visualmente
(zoom): píldora en `indigo`, y el residente sin apartamento ("TEST 2")
no muestra ninguna píldora. Confirmado en desktop (900px) que la
píldora sigue sin aparecer ahí (`display:none` verificado explícitamente,
no solo `textContent` -- un chequeo inicial por `textContent` daba falso
positivo porque ese método no distingue elementos ocultos).

Suite completa (`pytest tests/web/test_customers_manage.py`): sin
regresiones (ningún test dependía de "No Asig." en el listado -- el
único match de "No Asignado" en la suite es el fallback de desktop, que
no cambió).

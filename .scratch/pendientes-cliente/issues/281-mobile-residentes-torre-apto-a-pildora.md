# 281 — Seguimiento a [[280]]: Torre/Apto pasa a píldora en mobile

**Pedido original (cliente):** "PARA LA VISTA DE residentes que
posibilidad existe en que escondas la columna de Torre/Apt y lo
referente a este lo crees una pildora que estara al laso de
Auto/Principal/Torre-Apt?, dime si es posible y asi optimizamos espacio
y mejoramos los padings y margenes"

**Status:** implementado

## Alcance

`customers_manage/_resultados.html`, tabla plana de `/residentes`,
mobile only (desktop sin cambios):

1. Columna "Torre/Apto" (`<th>`+`<td>`) oculta en mobile
   (`hidden sm:table-cell`, mismo patrón que Teléfono desde [[277]]).
2. Su valor compacto (`etiqueta_torre_apto(..., compacto=True)`, ya
   existente desde [[277]]) se agrega como una píldora nueva dentro de
   la fila de badges creada en [[278]] (`sm:contents`) -- queda junto a
   Auto/Principal cuando aplican. A diferencia de esas dos, la píldora
   de Torre/Apto es incondicional (todo residente tiene o no
   apartamento) -- la fila de badges deja de ser condicional a
   Auto/Principal y pasa a renderizarse siempre en mobile.
3. La píldora de Torre/Apto lleva `sm:hidden` individual -- desaparece
   desde `sm:` (desktop sigue mostrando la columna dedicada de siempre,
   sin duplicarlo).
4. Con la columna completa liberada, se reevalúan paddings/anchos
   (`clamp()` de nombre e íconos, padding de celdas) para aprovechar el
   espacio ganado -- mismo método iterativo de medición en vivo que
   [[277]]/[[278]].

## Verificación

Iframes same-origin en dev local (mismo método de [[277]]-[[280]]) a
360/375/390/414px: **0px de overflow** en los 4 -- y esta vez sin
slack sobrante (el ancho de fila usa exactamente el disponible, ni de
más ni de menos). Con la columna completa liberada, el padding
horizontal de Nombre/Acciones subió de `px-0.5` a `px-1` en mobile
("mejoramos los paddings y márgenes", pedido explícito).

Confirmado visualmente (zoom en Chrome): en mobile solo quedan las
columnas Nombre y Acciones -- Torre/Apto aparece como píldora gris
junto a Auto/Principal, en la misma segunda fila de [[278]]. Confirmado
en desktop (probado a 900px) que la píldora NO se duplica -- Torre y
Apartamento sigue viendo su columna dedicada de siempre, sin cambios.

Suite completa (`pytest tests/web/test_customers_manage.py`): 154
passed, sin regresiones.

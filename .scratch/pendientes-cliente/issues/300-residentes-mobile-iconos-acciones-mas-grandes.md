# 300 — `/residentes` mobile: íconos de Acciones más grandes, distribuidos en toda la columna

**Pedido original (cliente):** "en la vista de dispositivos mobiles de esta vista se muestran
todos los datos repartidos en 2 columnas, especificamente para la coluna Acciones necesito que
los icono esten distribuido en todo el espacio de esa columna ya que veo que el espacio que
sobra es entre un 10 a 15 % del total de vista total, analiza y dime que puedes hacer para que
estos iconos se vean mas grande y que no se afecte la columna de Nombre"

**Status:** verificado

## Análisis

`customers_manage/_resultados.html`, mobile only (columnas Nombre + Acciones, Teléfono/Torre
ocultas desde [[277]]/[[281]]). Medido con Playwright contra el dev local en varios viewports
(320-428px):

- Los íconos de Acciones ya ocupaban el 100% del ancho disponible de su `<td>` -- el "espacio
  que sobra" no estaba libre DENTRO de la columna, sino que la columna Nombre estaba más ancha
  de lo que casi ninguna fila necesita: su ancho lo fija la fila EXCEPCIONAL con las 3 píldoras
  juntas (Auto + Principal + Torre/Apto, ej. residente Auto+Principal+con unidad), no el nombre
  en sí. Confirmado: la fila con más texto de nombre (18 caracteres) sólo necesita ~149px,
  pero la columna se reservaba 194.5px por esa fila de 3 píldoras.
- Además los íconos estaban agrupados a la izquierda (`justify-start`, default) sin usar el
  ancho ganado.
- Bug preexistente encontrado en el camino (no reportado antes): a 320-340px de viewport la
  tabla YA tenía overflow horizontal real (50px y 30px respectivamente) -- nunca estuvo limpia
  ahí, solo se había verificado/documentado desde 359px en adelante ([[277]]-[[283]]).

## Cambio

1. La fila de píldoras (Auto/Principal/Torre-Apto) gana `flex-wrap` + `max-w-[150px]` -- ya no
   fuerza la columna Nombre más ancha de lo que el nombre visible necesita; en la fila
   excepcional de 3 píldoras, la tercera pasa a una segunda línea en vez de ensanchar toda la
   columna para todos.
2. El contenedor de íconos de Acciones pasa de agrupado a la izquierda a `justify-between`
   (mobile only, `sm:justify-start` preserva desktop intacto) -- usa el ancho ganado para
   distribuir los 4 íconos a lo largo de toda la columna.
3. `tam_icono`: `clamp(1.625rem,7.5vw,2rem)` → `clamp(1.625rem,7.8vw,2.15rem)` -- mismo piso
   (26px, sin cambio bajo ~330px de viewport), techo más alto (32px→34.4px) y curva más
   pronunciada, calibrado para no reabrir overflow horizontal en ningún viewport probado.

Nombre no pierde ningún nombre real: la única fila afectada es la de 3 píldoras, que ahora usa
una segunda línea en vez de forzar la columna -- el texto del nombre nunca se acota ni se
trunca (`nombre_mobile()` sigue igual, sin tocar).

## Verificación

Verificado en vivo (dev local + Playwright headless, iPhone-range 320/340/359/375/390/414/428px,
usuario admin real, datos reales incluyendo el caso de 3 píldoras "JESUS VILLALOBOS"):

- 359px en adelante: 0px de overflow horizontal (igual que antes).
- 340px: overflow baja de 30px (preexistente) a 2px.
- 320px: overflow baja de 50px (preexistente) a 20px -- mejora, aunque no queda en 0 (viewport
  nunca antes verificado/soportado en este historial, ver [[277]] que fija 359px como piso).
- Íconos crecen de 28.1px → 31.9px a 375px de viewport (+13%), y de 31px → 35.2px a 414px, sin
  overflow.
- Columna Acciones gana ancho real: 134.5px → ~146-155px según viewport (antes exactamente
  igual al contenido de los íconos, sin margen).
- Screenshots antes/después + badge de 3 píldoras confirmado envolviendo a 2 líneas sin
  solaparse ni recortarse.
- Tailwind reconstruido (`npm run build:css`) -- clases nuevas (`max-w-[150px]`,
  `justify-between`, `sm:justify-start`, clamp `7.8vw`/`2.15rem`) confirmadas en el CSS
  compilado antes de verificar.
- `pytest tests/web/test_customers_manage.py`: 154 passed, sin regresiones.
- Desktop verificado sin cambios (screenshot 1280px, íconos agrupados a la izquierda, 32px fijo,
  igual que siempre).

Desplegado a `test.papyrus.com.co` 2026-09-03 (CI `jemavidev/PaqueteX` run 33803818157, tests +
deploy success) y confirmado en el CSS servido en producción (`7.8vw,2.15rem` presente).

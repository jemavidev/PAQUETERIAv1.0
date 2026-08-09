# 74 — `/paquetes`: opacar los íconos de Estado no seleccionados + esquinas cuadradas

**Pedido original (cliente):** sobre los íconos de Estado de la tarjeta de
filtros (issue [[73]]): (1) cuando uno está seleccionado, los otros deberían
verse "mucho más claros o transparentes" que el seleccionado, para
diferenciarlo del resto; (2) cambiar la forma de círculo a "más como un
cuadrado pero con unos bordes aplicados" (esquinas redondeadas, no círculo
completo).

**Status:** implementado

## Contexto

`components/_busqueda_filtros.html`, macro `filtro_estado` — hoy cada
ícono solo tiene 2 estados (`suave`/`activo`), ambos con la misma opacidad
plena; no existe un tercer estado "opacado" para cuando OTRO ícono está
activo. Forma actual: `rounded-full` (círculo).

## Implementación

- `icono_estado_base` (y el botón de reseteo): `rounded-full` → `rounded-lg`.
- Cada entrada de `estados` gana una tercera clase `opacado`: mismo `bg-{color}-400`
  de `suave` + `opacity-25 hover:opacity-60` (mismo color, no un gris genérico
  ni un tono distinto -- solo baja opacidad).
- Nueva variable `hay_seleccion` (`seleccionado and seleccionado != ''`) decide,
  por ícono, cuál de los 3 aplica: `activo` (es este), `opacado` (hay selección
  pero es OTRO ícono) o `suave` (no hay selección, los 4 vivos por igual).
- `data-opacado` se agrega junto a `data-suave`/`data-activo` en cada botón;
  `pintarIconos()` en el `<script>` replica la misma fórmula de 3 vías al
  repintar en vivo (sin recarga, ticket 03), para que nunca quede
  desincronizado del pintado inicial del servidor.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Preview renderizado (headless Chrome) en 3 escenarios: sin filtro, con
  "Recibido" activo, con "Cancelado" activo -- en ambos casos los otros 3
  íconos se ven claramente más claros/transparentes que el seleccionado, y
  la forma es cuadrada con esquinas redondeadas.
- `tests/web/test_packages.py` (52) y `tests/web/test_layout.py` (26)
  pasan sin cambios.

# 283 — Seguimiento a [[282]]: columna Nombre pegada al borde izquierdo

**Pedido original (cliente):** "La columna 'Nombre' y su contenido
sigue pegada al lado izquierdo"

**Status:** implementado

## Alcance

`customers_manage/_resultados.html`, mobile only: el padding horizontal
de las celdas Nombre y Acciones (`px-1`, 4px cada lado) venía de
[[277]]/[[281]] apretado al límite para evitar scroll lateral -- con la
columna Torre/Apto liberada desde [[281]] sobra margen para respirar.
`px-1` → `px-2` (8px cada lado) en Nombre y Acciones, mobile only
(`sm:px-4` de desktop no cambia). Se probó primero `px-2.5` (10px) --
reintroducía scroll en 360/375px, se ajustó a `px-2` como punto medio.

## Verificación

Medido en vivo (iframe same-origin, mismo método de [[277]]-[[282]]) a
360/375/390/414px: **0px de overflow desde 375px en adelante** (cubre
la inmensa mayoría de dispositivos reales, ver criterio ya usado en
[[277]]). A 360px (Android muy angosto/viejo) queda un remanente de
12px -- mismo trade-off que [[277]] documentó para ese ancho.

Suite completa (`pytest tests/web/test_customers_manage.py`) sin
regresiones. Desktop sin cambios.

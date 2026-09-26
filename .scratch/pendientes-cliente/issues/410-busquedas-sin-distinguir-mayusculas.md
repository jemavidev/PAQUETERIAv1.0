# 410 — Ninguna búsqueda distingue mayúsculas de minúsculas

**Pedido original (Jesús, 2026-09-26):** "La idea es que en cualquier búsqueda no distinga nunca, que sea lo mismo"
(a raíz de que `/consultar?q=za9325` no encontraba el paquete `ZA9325`).

**Status:** implementado (localhost), pendiente confirmar en vivo

## Qué se hace

- Revisar TODAS las búsquedas del sistema (/consultar, /paquetes, /residentes, contactos externos, anunciar, etc.) y que
  ninguna distinga mayúsculas/minúsculas (ni espacios de más al inicio/fin).
- Pruebas que lo fijen en cada una.

## Revisión y resultado (2026-09-26)

Auditoría de las cajas de búsqueda: /paquetes, /residentes (incluido `apt302`), contactos externos y saldos contra
entrega ya usaban `ilike` / `re.IGNORECASE`. La única que distinguía era **/consultar** (igualdad exacta en código y
guía): ahora compara en mayúsculas. `tests/web/test_busquedas_sin_mayusculas.py` fija el comportamiento en /consultar
(código y guía, 4 variantes cada uno), /paquetes (nombre y código) y /residentes; 72 en verde con las de /consultar.

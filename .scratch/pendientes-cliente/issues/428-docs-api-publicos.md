# 428 — `/docs`, `/redoc` y `/openapi.json` públicos

**Origen:** análisis de enlaces (`.scratch/analisis-enlaces/mapa-de-enlaces.md`, hallazgo 1). Jesús: "corrige los 3
problemas que encontraste".

**Status:** verificado (`a3bda27`, confirmado por Jesús en test 2026-09-28)

## Decisiones

- FastAPI los crea por defecto: respondían 200 sin sesión en test, con el mapa completo de rutas y parámetros.
- Se apagan cuando `WEB_ENV` es `staging` o `production` (404). En desarrollo local siguen disponibles.

## Verificación

- `tests/web/test_arranque_produccion.py`: 404 en `/docs`, `/redoc` y `/openapi.json` con `production` y `staging`
  (fallaban antes: 200); siguen en desarrollo. Afectadas + infra: 347 en verde.

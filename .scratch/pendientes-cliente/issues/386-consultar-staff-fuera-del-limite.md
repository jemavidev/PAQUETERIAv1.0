# 386 — `/consultar`: el staff con sesión no cuenta en el límite de consultas

**Pedido original (Jesús):** "el punto 4 lo veo bien" (hallazgo 4).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Con sesión de staff, `/consultar` no aplica el límite de 10/min (la usa para recibir y entregar).
- `--proxy-headers` en uvicorn queda para cuando se hable del servidor de test (en localhost no hay proxy).

## Verificación

- 3 pruebas nuevas en `tests/web/test_search.py`: el staff consulta más de 10 veces por minuto; el público sigue limitado; las consultas del staff no gastan el cupo del público de la misma IP.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

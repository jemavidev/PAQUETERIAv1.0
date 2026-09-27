# 381 — CSV de contactos externos: tildes en Excel

**Pedido original (Jesús):** "arregla lo de CSV" (hallazgo 10).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Exportar y plantilla con BOM UTF-8 y `charset=utf-8`: Excel en Windows abre bien las tildes.
- Celdas que empiezan por `=`, `+`, `-`, `@` se prefijan con `'` (inyección de fórmulas) al exportar.

## Verificación

- `tests/web/test_admin_contactos_externos.py` (3 nuevas + 2 ajustadas, fallaban antes): BOM y `charset=utf-8` en plantilla y exportación; nombre `=...` exportado como `'=...` sin tocar teléfonos; reimportar quita el apóstrofo; importar acepta un CSV de Excel en ANSI (cp1252) y separado por `;`. Se mantiene la coma al exportar (Google Contacts y otras fuentes usan coma).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

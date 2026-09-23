# 381 — CSV de contactos externos: tildes en Excel

**Pedido original (Jesús):** "arregla lo de CSV" (hallazgo 10).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- Exportar y plantilla con BOM UTF-8 y `charset=utf-8`: Excel en Windows abre bien las tildes.
- Celdas que empiezan por `=`, `+`, `-`, `@` se prefijan con `'` (inyección de fórmulas) al exportar.

## Verificación

- `tests/web/test_admin_contactos_externos.py` (3 nuevas + 2 ajustadas, fallaban antes): BOM y `charset=utf-8` en plantilla y exportación; nombre `=...` exportado como `'=...` sin tocar teléfonos; reimportar quita el apóstrofo; importar acepta un CSV de Excel en ANSI (cp1252) y separado por `;`. Se mantiene la coma al exportar (Google Contacts y otras fuentes usan coma).

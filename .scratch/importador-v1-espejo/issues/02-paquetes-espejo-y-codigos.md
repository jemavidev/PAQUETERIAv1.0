# 02 — Paquetes espejo con sus códigos

**What to build:** cada paquete de la v1 aparece en la v2 y se puede consultar con el mismo código de 4 caracteres que el residente recibió por SMS. Los anuncios activos de la v1 que todavía no son paquete aparecen como `ANUNCIADO`, y cuando la v1 los recibe, el mismo paquete de la v2 avanza sin cambiar de código ni de identidad (ver `../spec.md`, historias 22-30).

**Blocked by:** 01 — Bala trazadora: Personas espejo de punta a punta

**Status:** done

- [x] Migración: `origen_v1_id` en `paquetes` (id del paquete de la v1, o `anuncio:<id>` para los anuncios sin paquete), con índice único parcial.
- [x] Anunciante = la Persona del cliente. `recipient_name` = `display_name`, o el nombre del cliente si `display_name` está vacío. `recipient_phone` = el teléfono del cliente.
- [x] Snapshot sin conjunto, torre ni apartamento, y nunca se reescribe aunque la Persona declare su apartamento después (ADR-0001).
- [x] Estado, tipo, condición y `guide_number` se copian tal cual. `announced_at`, `received_at`, `delivered_at` y `cancelled_at` se guardan en UTC.
- [x] `tracking_number` pasa a `access_code` solo al crear el paquete. El importador nunca lo vuelve a escribir, y un código con sufijo de año de "Migrar año" se conserva (prueba junto a `test_migrar_codigos_del_anio.py`).
- [x] Choque: si un paquete nativo tiene el código, se le asigna uno nuevo con el generador existente y el choque queda en el reporte. El paquete de la v1 conserva su código.
- [x] Anuncios activos sin procesar → paquete `ANUNCIADO`. Cuando la v1 los convierte en paquete, se actualiza el mismo registro (reconocido por el `package_id` del anuncio): cambian su `origen_v1_id` y su estado, sin crear ni borrar nada.
- [x] La v1 gana en los campos importados. Los paquetes nativos no se tocan. Una segunda pasada idéntica no cambia nada.
- [x] Sin avisos: la escritura no pasa por el ciclo de vida que notifica.
- [x] `posicion` y el `access_code` de 8 caracteres de la v1 se descartan.

# 06 — Fotos espejo

**What to build:** las fotos de recepción de los paquetes de la v1 se ven en la v2 (detalle del paquete y `/consultar`). Se copian del bucket privado de la v1 al bucket configurado de la v2 (ver `../spec.md`, historias 39-42).

**Blocked by:** 02 — Paquetes espejo con sus códigos

**Status:** done

- [x] Migración: `origen_v1_id` en `paquete_fotos` (id de `file_uploads`), con índice único parcial.
- [x] Puerto copiador de fotos con una implementación falsa para pruebas y una real de S3 a S3: lee de `elclub-paqueteria` con las credenciales de la v1 y escribe en el bucket de fotos de la v2 con `public-read`.
- [x] El destino se deriva de la key de la v1 (`<prefijo-fotos-v2>legacy_<nombre-original>`, la convención del 2026-08-20). Si el destino ya existe, no se vuelve a copiar.
- [x] El bucket de destino sale de la configuración de la v2, sin cambiar código.
- [x] Una foto que falla queda en el reporte, no frena el resto y se reintenta en la siguiente pasada.
- [x] `--simular` no llama al copiador, ni al real ni al falso.
- [x] Validación manual del copiador real con una tanda chica (fotos de los paquetes `RECIBIDO`) antes de escalar, confirmando HTTP 200 público.

## Comments

**2026-09-23.** La validación manual con S3 real quedó en la guía de puesta en marcha (§5.1): necesita las credenciales de la v1 en el servidor v2, lo que requiere autorización.

**2026-09-24.** Validado en vivo: 7.475 fotos en el bucket de la v2, y una nueva responde HTTP 200 pública. Hizo falta el fix `8cec947` (403 sin `s3:ListBucket`).

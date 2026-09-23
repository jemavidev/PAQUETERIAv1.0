# 389 — Fotos: Recibir sin esperar fotos, cola con reintentos, orientación y validaciones

**Pedido original (Jesús):** "que este no sea un sistema bloqueante de una recepción basado en una foto que falló, debería correr en paralelo e intentar sincronizar ... equipos con poco procesamiento y poca memoria"; "comprimidas pero con calidad para leerlas"; validaciones: "me parece perfecto" (hallazgos 7 y 12).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- Recibir nunca espera ni lleva fotos: las pendientes quedan en una cola del equipo (IndexedDB, en disco) y se suben
  solas con reintentos (al volver la red, en cualquier página de staff), asociándose directo al paquete.
- Aviso discreto en el encabezado mientras haya fotos por subir.
- Miniaturas livianas, liberando memoria (antes cada refresco retenía una copia completa de cada foto).
- Servidor: corrige la orientación EXIF, comprime legible (lado mayor 2048 px, JPEG calidad 85), rechaza lo que no sea
  imagen y archivos de más de 15 MB; `fotos_urls` solo acepta URLs del propio almacenamiento.

## Verificación

- `tests/web/test_fotos_cola_y_validaciones.py` (8), `tests/data_model/test_imagen_service.py` (orientación, 2048 px, rechazo), `test_s3_foto_storage.py` (URLs propias) y `tests/browser/test_fotos_cola.py` (2): Recibir sale al instante con una subida colgada, la foto queda en la cola del equipo, el aviso del encabezado aparece y, al volver la conexión, la cola la sube y la asocia. La prueba destapó dos defectos que se corrigieron: sin tiempo límite una subida colgada bloqueaba la cola, y el aviso solo se pintaba al terminar la cola. Pruebas que subían bytes falsos pasaron a JPEG reales a propósito.

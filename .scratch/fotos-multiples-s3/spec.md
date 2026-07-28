# Spec — Fotos múltiples (hasta 3) + S3FotoStorage (Grupo 15, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 15.

## Qué cambia

1. **Multi-foto**: el dominio ya soportaba varias fotos por paquete (tabla
   `paquete_fotos` ya era 1:N, Grupo 2 de la Ronda 1). Lo que faltaba:
   - `paquete_foto_service.agregar_foto` ahora rechaza (`ValueError`) una
     4ª foto para el mismo paquete (`_MAX_FOTOS_POR_PAQUETE = 3`).
   - El modal "Recibir" (`packages/list.html`) cambia `<input type="file"
     name="foto">` por `<input type="file" name="fotos" multiple>`.
   - La ruta `POST /paquetes/{id}/recibir` acepta `fotos: list[UploadFile]`
     en vez de un solo `foto`; guarda hasta 3 y **silenciosamente ignora**
     el resto si alguien manda más (nunca hace fallar todo el recibo por
     esto).
2. **S3FotoStorage** (`app/domain/s3_foto_storage.py`, nuevo): implementa
   el mismo `Protocol FotoStorage` que `LocalFotoStorage` — mismo patrón
   que `LiwaNotificationSender` frente a `ConsoleNotificationSender`.
   `app/web/fotos.py::get_foto_storage()` elige S3 si `AWS_S3_BUCKET_NAME`
   está en el entorno, si no `LocalFotoStorage` (dev/tests, sin cambios).

## Decisión de diseño importante (AgentX)

Investigado el legacy (`app/services/s3_service.py`): sube con
`ACL='private'` y sirve por URL firmada con expiración (~1h por defecto) —
correcto ahí porque son facturas sensibles. **Ese patrón NO sirve para
fotos de paquete**: `/consultar` es una pantalla pública sin sesión que
debe seguir mostrando la foto indefinidamente, y no hay ningún flujo para
"refrescar" una URL firmada vencida. `S3FotoStorage.guardar` sube
deliberadamente con `ACL='public-read'` y devuelve la URL directa y
permanente del objeto — una desviación intencional del patrón legacy,
justificada por la diferencia de sensibilidad del contenido (foto de un
paquete en portería vs. una factura).

## Bloqueo real (misma categoría que LIWA, Grupo 8 de la Ronda 1)

El código y los tests quedan 100% listos con `LocalFotoStorage` como
implementación activa (igual que hoy) — falta que el usuario confirme:

1. ¿Bucket **nuevo y dedicado** a PaqueteXv.2, o el mismo bucket que ya usa
   el sistema legacy en producción (con un prefijo distinto,
   `paquetes-recibidos-imagenes/` por defecto, configurable vía
   `AWS_S3_PREFIX_FOTOS`)?
2. Credenciales (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) y región,
   cuando estén listas — mismo mecanismo que `STAGING_SSH_KEY`/
   `LIWA_API_KEY`: se configuran en el servidor, no en el repo.

Sin esto, `S3FotoStorage()` nunca se instancia en el servidor real (la
variable `AWS_S3_BUCKET_NAME` sigue sin definir), así que el código no
tiene ningún efecto hasta que se confirme.

## Fuera de alcance

- No se migran las fotos ya guardadas localmente (si las hay) a S3 — eso
  sería un ticket de migración de datos aparte, no pedido.

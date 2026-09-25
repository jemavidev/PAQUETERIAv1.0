# 01 — Primer respaldo local de la base de datos

**What to build:** un comando dentro del contenedor de la app que saca un respaldo de la base de datos al disco del
servidor: una carpeta con fecha que contiene `base_datos.dump` (formato nativo de Postgres) y `manifiesto.txt` (fecha y
hora, dominio y conjunto, commit desplegado, versión Alembic, motivo del respaldo, conteos de las tablas principales,
tamaños y huellas de cada archivo). Es el esqueleto del módulo de respaldos que usarán el cron, el deploy y la pantalla.
Incluye preparar la imagen y los montajes que lo hacen posible, y corregir la línea de D/R del glosario.

**Blocked by:** None — can start immediately

**Status:** done

- [x] La imagen de la app tiene el cliente de Postgres de la misma versión mayor que la BD; el contenedor monta el
      checkout y el `.env` en solo lectura y una carpeta de respaldos del host en lectura/escritura.
- [x] Correr el comando produce una carpeta con `base_datos.dump` y `manifiesto.txt` con todos los campos del spec.
- [x] La carpeta se arma aparte y solo aparece completa al final: una corrida que falla a mitad de camino no deja una
      carpeta con apariencia de buena.
- [x] Dos corridas simultáneas no se pisan: la segunda espera o se salta con un mensaje claro.
- [x] En el disco quedan solo las últimas 3 carpetas de respaldo.
- [x] El `.env` real nunca queda dentro del respaldo.
- [x] CONTEXT.md: la línea de D/R ("`pg_dump` horario → S3 cifrado/versionado, RPO ~1 h") se reemplaza por lo decidido
      (diario + puntuales, sin cifrado propio, bucket privado).
- [x] Pruebas contra el Postgres efímero: carpeta y manifiesto correctos, huellas que coinciden, conteos reales,
      corrida fallida sin carpeta publicada, retención de 3.
- [x] Verificado a mano en test.papyrus.com.co (este deploy reconstruye la imagen: vigilar memoria en el servidor de
      1 GB).

## Comments

**2026-09-25 (implementado, `d196690` en PaqueteX / `e95a9b4` en PaqueteXv.2):** respaldo real en test.papyrus.com.co:
`/respaldos/2026-09-25_104949_diario`, `base_datos.dump` de 1,0 MB + manifiesto (EL CLUB, commit `d196690`, versión
`0064_paquete_fotos_origen_v1`, 2.593 paquetes, 617 personas, 7.516 fotos). Imagen con `pg_dump` 16.15 (repo oficial:
el de Debian 13 es 17 y sus volcados no restauran en 16). El rebuild en el servidor de 1 GB pasó sin problemas.

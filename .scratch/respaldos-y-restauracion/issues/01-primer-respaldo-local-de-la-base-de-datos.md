# 01 — Primer respaldo local de la base de datos

**What to build:** un comando dentro del contenedor de la app que saca un respaldo de la base de datos al disco del
servidor: una carpeta con fecha que contiene `base_datos.dump` (formato nativo de Postgres) y `manifiesto.txt` (fecha y
hora, dominio y conjunto, commit desplegado, versión Alembic, motivo del respaldo, conteos de las tablas principales,
tamaños y huellas de cada archivo). Es el esqueleto del módulo de respaldos que usarán el cron, el deploy y la pantalla.
Incluye preparar la imagen y los montajes que lo hacen posible, y corregir la línea de D/R del glosario.

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] La imagen de la app tiene el cliente de Postgres de la misma versión mayor que la BD; el contenedor monta el
      checkout y el `.env` en solo lectura y una carpeta de respaldos del host en lectura/escritura.
- [ ] Correr el comando produce una carpeta con `base_datos.dump` y `manifiesto.txt` con todos los campos del spec.
- [ ] La carpeta se arma aparte y solo aparece completa al final: una corrida que falla a mitad de camino no deja una
      carpeta con apariencia de buena.
- [ ] Dos corridas simultáneas no se pisan: la segunda espera o se salta con un mensaje claro.
- [ ] En el disco quedan solo las últimas 3 carpetas de respaldo.
- [ ] El `.env` real nunca queda dentro del respaldo.
- [ ] CONTEXT.md: la línea de D/R ("`pg_dump` horario → S3 cifrado/versionado, RPO ~1 h") se reemplaza por lo decidido
      (diario + puntuales, sin cifrado propio, bucket privado).
- [ ] Pruebas contra el Postgres efímero: carpeta y manifiesto correctos, huellas que coinciden, conteos reales,
      corrida fallida sin carpeta publicada, retención de 3.
- [ ] Verificado a mano en test.papyrus.com.co (este deploy reconstruye la imagen: vigilar memoria en el servidor de
      1 GB).

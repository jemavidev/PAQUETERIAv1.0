# 11 — Infraestructura y puesta en marcha

**What to build:** el espejo corre solo en el servidor v2 cada 15 minutos, con credenciales de solo lectura hacia la v1. Deja una guía paso a paso para activarlo y para el día del corte (ver `../spec.md`, Infraestructura e historias 10 y 45).

**Blocked by:** 08 — Modo `--final`, 09 — Pantallas sin apartamento, 10 — Script de limpieza previa del staging

**Status:** implementado — código, SQL, cron y guía listos; la ejecución en servidores espera autorización

- [x] Script de SQL que crea el rol `paquetex_importador` en la base de la v1, con solo `CONNECT` y `SELECT` sobre las tablas que se leen.
- [ ] Variables de la v1 (URL de la base con el rol de solo lectura y credenciales S3 de lectura) declaradas de forma explícita en el `docker-compose.yml` del repo de despliegue `jemavidev/PaqueteX`, que no usa `env_file`.
- [x] Entrada de cron en el servidor v2: cada 15 minutos corre el script dentro del contenedor, con lock para que no se solapen dos pasadas y el reporte en un log con rotación.
- [x] Guía de puesta en marcha: dump del staging → limpieza (ticket 10) → `--simular` contra la v1 real → revisar el reporte → primera pasada real → verificar conteos contra la v1 → activar el cron.
- [x] Guía del corte: v1 en solo lectura → `--final` → quitar el cron → retirar el rol y el script cuando se apague la base de la v1.
- [ ] Cambios sincronizados al repo de despliegue copiando archivos puntuales (sin `subtree push`), y `pytest` sin rutas en verde antes del push.
- [ ] **Crear el rol en producción, hacer deploy, limpiar el staging y activar el cron solo con autorización explícita de Jesús**, paso por paso.

## Comments

**2026-09-23 — implementación.**
- SQL del rol: `CODE/scripts/importador_v1/rol_solo_lectura.sql`. Validado contra una base local con
  la forma de la v1: el lector funciona con el rol y un `DELETE` falla por solo lectura.
- Cron: `CODE/scripts/importador_v1/importar_v1_cron.sh`, con `flock`, log rotado a los 5 MB y
  argumentos extra que pasa tal cual.
- Los CLI viven en `src/app/importador_v1_cli.py` y `src/app/limpieza_staging_cli.py`, porque la
  imagen de despliegue no incluye `scripts/`. Se corren con `python -m` desde `/app/src`.
- Guía completa: `../puesta-en-marcha.md`, que incluye el bloque de variables para
  `docker-compose.yml`. Ese archivo solo existe en el repo de despliegue, así que el cambio se aplica
  al sincronizar (paso 1).
- **Bloqueo nuevo (§0 de la guía):** la v2 corre con `WEB_ENV=production` y los SMS llegan a
  residentes reales. Hay que decidir cómo se maneja antes de activar el espejo.
- Pendiente, con autorización: push al repo de despliegue, crear el rol, variables en `.env`, dump y
  limpieza, primera pasada y cron.

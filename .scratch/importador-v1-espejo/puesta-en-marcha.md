# Importador espejo v1 → v2 — guía de puesta en marcha y de corte

Ticket 11 de `.scratch/importador-v1-espejo`. Cada paso marcado **[autorización]** toca producción
(`ssh paquetex`) o el servidor v2 (`ssh paquetex-v2`, `test.papyrus.com.co`), y se ejecuta **solo
con autorización explícita de Jesús, paso por paso**.

## 0. SMS durante la transición — decidido 2026-09-24: opción A

`test.papyrus.com.co` corre con `WEB_ENV=production`: los SMS de la v2 llegan a destinatarios reales
(el override de staging se retiró el 2026-08-10). Para que una prueba en la v2 sobre un paquete
importado nunca le escriba a un residente real de la v1, **`IMPORTADOR_V1_ESPEJO_ACTIVO=1`** apaga
los avisos de los paquetes importados (`src/app/domain/espejo_v1.py`, en
`notificacion_service.preparar_notificacion`). Los paquetes nativos, el OTP y las pruebas con
clientes reales no cambian. Complemento operativo: avisarle al staff que en la v2 no se opera sobre
paquetes importados hasta el corte.

**La variable debe estar puesta ANTES de la primera pasada (paso 5)** y se quita en el corte (paso 7).

## 1. Sincronizar el código al repo de despliegue (`jemavidev/PaqueteX`) **[autorización: push]**

Procedimiento habitual: copiar a mano los archivos puntuales (sin `CODE/`) a una rama nueva sobre
`paquetex-live/main`, verificar que el diff sea exactamente esta lista y hacer fast-forward.

- `alembic/versions/0061_personas_origen_v1.py` … `0064_paquete_fotos_origen_v1.py`
- `src/app/domain/importador_v1_service.py`, `importador_v1_lector.py`, `s3_copiador_fotos_v1.py`,
  `limpieza_staging_service.py`, `espejo_v1.py`
- `src/app/domain/notificacion_service.py` (silencio de avisos de paquetes importados)
- `src/app/domain/persona.py`, `paquete.py`, `usuario.py`, `paquete_foto.py`, `cobro.py` (columnas
  `origen_v1_id` y nota del Cobro)
- `src/app/importador_v1_cli.py`, `src/app/limpieza_staging_cli.py`
- `scripts/importar_v1.py`, `scripts/limpiar_staging_residentes.py`, `scripts/importador_v1/`
- `tests/data_model/test_importador_v1_*.py`, `test_s3_copiador_fotos_v1.py`,
  `test_limpieza_staging_residentes.py`, `test_importador_v1_silencio_sms.py`, `tests/web/test_datos_importados_sin_apartamento.py`
- `docker-compose.yml`: agregar al `environment:` de `app` (el compose lista las variables
  explícitamente y **no** usa `env_file`):

  ```yaml
      # Importador espejo v1 → v2 (.scratch/importador-v1-espejo). Solo lectura
      # sobre la base y el bucket de la v1. Definidas en .env, NO versionadas.
      V1_DATABASE_URL: ${V1_DATABASE_URL}
      V1_AWS_ACCESS_KEY_ID: ${V1_AWS_ACCESS_KEY_ID}
      V1_AWS_SECRET_ACCESS_KEY: ${V1_AWS_SECRET_ACCESS_KEY}
      V1_AWS_S3_BUCKET: ${V1_AWS_S3_BUCKET}
      V1_AWS_REGION: ${V1_AWS_REGION}
      # Silencia los avisos de los paquetes importados mientras dure el
      # espejo (espejo_v1.py). Se quita del .env en el corte.
      IMPORTADOR_V1_ESPEJO_ACTIVO: ${IMPORTADOR_V1_ESPEJO_ACTIVO}
  ```

  Como cambia el `docker-compose.yml`, CI hace `up -d --build`, y el arranque corre
  `alembic upgrade head` (migraciones 0061-0064).

Antes del push: `pytest` sin rutas en verde (CI recolecta todo junto).

## 2. Rol de solo lectura en la v1 **[autorización: producción]**

En `ssh paquetex`, con el usuario administrador de la base:

```
psql "<url-admin-de-paqueteria_v4>" -v clave="'<contraseña-nueva>'" -f rol_solo_lectura.sql
```

(`CODE/scripts/importador_v1/rol_solo_lectura.sql`, validado localmente: el rol lee las 7 tablas y
un `DELETE` falla con `cannot execute DELETE in a read-only transaction`.)

## 3. Variables en el `.env` de la v2 **[autorización: servidor v2]**

`ssh paquetex-v2`, en `~/app/.env`:

```
V1_DATABASE_URL=postgresql://paquetex_importador:<contraseña>@<POSTGRES_HOST de ~/paqueteria/.env en ssh paquetex>:5432/paqueteria_v4
V1_AWS_ACCESS_KEY_ID=<lectura de elclub-paqueteria>
V1_AWS_SECRET_ACCESS_KEY=<…>
V1_AWS_S3_BUCKET=elclub-paqueteria
V1_AWS_REGION=us-east-1
IMPORTADOR_V1_ESPEJO_ACTIVO=1
```

Tras editar el `.env`: `sudo docker compose --env-file .env up -d app` (recrea el contenedor con las
variables nuevas) y comprobar con `sudo docker compose exec app sh -c 'echo $IMPORTADOR_V1_ESPEJO_ACTIVO'`.

Las credenciales S3 de lectura de la v1 son hoy las de la app v1 (`AWS_ACCESS_KEY_ID` en su `.env`).
Lo ideal es un usuario IAM propio con solo `s3:GetObject` sobre `elclub-paqueteria`.

## 4. Dump y limpieza del staging **[autorización: servidor v2]**

```
cd ~/app
sudo docker compose exec -T db pg_dump -U paquetex -Fc paquetex > ~/paquetex_backup_pre_importador_v1_$(date +%Y%m%d_%H%M%S).dump
sudo docker compose --env-file .env exec -T -w /app/src app python -m app.limpieza_staging_cli --simular
# revisar conteos: se borran residentes/paquetes; se conservan usuarios, apartamentos (804), contactos externos (1041)
sudo docker compose --env-file .env exec -T -w /app/src app python -m app.limpieza_staging_cli --confirmar
```

## 5. Primera pasada **[autorización: servidor v2]** — requiere `IMPORTADOR_V1_ESPEJO_ACTIVO=1` (§0)

```
scripts/importador_v1/importar_v1_cron.sh --simular    # revisar ~/importador_v1/importador.log
```

Revisar el reporte: ~609 personas, ~2.555 + 18 paquetes, ~2.537 cobros, fotos
(en simular se cuentan sin copiar), 0 choques. Luego:

1. **Validación de fotos con una tanda chica** (ticket 06): en vez de la primera pasada completa,
   conviene confirmar primero con `curl -I` que un par de URLs copiadas responden `HTTP 200`
   públicamente. La primera pasada real copia las ~7.475 fotos (509 MB) y puede tardar; el `flock`
   evita que el cron la solape.
2. Pasada real: `scripts/importador_v1/importar_v1_cron.sh`
3. Verificar conteos contra la v1 (personas, paquetes por estado, suma de cobros = 3.857.500 COP
   al 2026-09-23 más lo nuevo) y abrir en la v2 un paquete conocido.
4. Segunda pasada: debe reportar todo `sin_cambios`.

## 6. Activar el cron **[autorización: servidor v2]**

```
crontab -e   # usuario ubuntu
*/15 * * * * /home/ubuntu/app/scripts/importador_v1/importar_v1_cron.sh
```

Una pasada con alerta del tope del 5 % no escribe nada y deja el código de salida 1 en el log.

## 7. Día del corte **[autorización: todo]**

1. Poner la v1 en solo lectura (fuera del alcance de este importador).
2. `scripts/importador_v1/importar_v1_cron.sh --final`: debe terminar `RESULTADO: exitosa`. Si falla,
   no escribió nada; resolver los choques o errores del log y repetir.
3. Quitar la línea del cron (`crontab -e`). Después del corte, "la v1 gana siempre" pisaría
   operaciones reales hechas en la v2.
4. Quitar `IMPORTADOR_V1_ESPEJO_ACTIVO` del `.env` y recrear el contenedor: desde ahí los paquetes
   importados que sigan pendientes vuelven a notificarse.
5. Apuntar el dominio (fuera del alcance).
6. Cuando se apague la base de la v1: retirar el rol (`REVOKE`/`DROP ROLE`, al pie de
   `rol_solo_lectura.sql`) y las variables `V1_*`.

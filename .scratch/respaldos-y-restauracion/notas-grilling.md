# Respaldos diarios y restauración — notas de `grilling` (2026-09-25)

Fuente: sesión de `grilling` con Jesús (esta conversación). Insumo para `/to-spec` → `/to-tickets`. Todo lo de abajo
son decisiones de Jesús, salvo lo marcado como "por defecto" (propuesto por Claude, sin objeción).

## Pedido original

"una forma en que se pueda hacer un backup diario de los datos de la base de datos que es lo primero y en algún punto
poder hacer un recovery de esos datos, siempre y cuando sea el mismo sistema que se quiere recuperar ... copias
automáticas del sistema (db, código, archivos yml o similar para montar los contenedores, con relación a las
configuraciones locales de cada servidor yo lo haré manualmente antes de restaurar), adicional una forma de recuperar
esos datos respaldados, sería bueno que esos datos puedan ser descargados para poder hacer restauraciones en lugares
diferentes a AWS".

## Hechos verificados (2026-09-25)

- test.papyrus.com.co: Lightsail 2 vCPU / 1 GB RAM / sin swap / 38 GB disco (20 %). Postgres 16 en contenedor, volumen
  con nombre `paquetex_pgdata`. BD 22 MB (2.592 paquetes, 617 personas, 7.511 fotos). ~330 paquetes/mes en El Club.
- Fotos solo en S3 (`paquetex-staging-fotos` en test), ~1,5–2,5 GB estimados (2048 px, JPEG 85), crecen ~200–300 MB/mes.
  La llave del servidor (`paquetex-staging-fotos-uploader`) hoy SOLO sube: sin `s3:ListBucket` ni lectura.
- Cuenta de AWS de Jesús: `172460160630`. La AWS CLI de la PC de desarrollo está autenticada en ella (usuario
  `Antigravity`); el bucket de fotos de test y su usuario viven ahí.
- SMTP configurado en test (`SMTP_HOST`/`SMTP_USER`/`SMTP_FROM_EMAIL`).
- Código en GitHub `jemavidev/PaqueteX` (PÚBLICO). Deploy: push a `main` → tests → SSH + `docker compose up -d --build`.
  Checkout en el servidor: `/home/ubuntu/app/PaqueteX`. Cron del importador v1 cada 15 min.
- Hoy solo hay `pg_dump` manuales sueltos en `~` del servidor (5, antes de operaciones riesgosas).

## Decisiones

1. **Fotos fuera del respaldo diario.** Aparte, opción a pedido para descargarlas con su estructura de carpetas,
   incremental a partir de la primera sincronización (ver 9–10).
2. **Dónde:** bucket S3 dedicado a respaldos en la cuenta de Jesús, separado del de fotos; el servidor solo puede
   SUBIR (no leer, borrar ni sobrescribir). Además, las últimas 3 copias en el disco del servidor.
3. **Conservación:** `diario/` 30 días; `mensual/` (copia del día 1) 12 meses; `anual/` (1 de enero) sin fecha de
   borrado. Reglas de ciclo de vida de S3 por carpeta.
4. **Sin cifrado propio.** Bucket privado con cifrado por defecto de S3; las copias nunca a los repos (públicos).
5. **Contenido de cada respaldo** (una carpeta con fecha): `base_datos.dump` (`pg_dump -Fc`), `sistema.tar.gz` (copia
   exacta del código desplegado: compose, Caddyfile, Dockerfile, requirements, `src/`, `alembic/`, `scripts/`),
   `manifiesto.txt` (fecha/hora, dominio y conjunto, commit, versión Alembic, conteos de tablas principales, tamaños y
   checksums, nombres de variables de entorno requeridas) y `env.plantilla`.
6. **`env.plantilla`:** generado del `.env` real al respaldar, todas las variables agrupadas con un comentario cada
   una; lo no secreto con su valor completo; los secretos ofuscados `ABC****XYZ` (3 + 3); secretos de menos de 12
   caracteres solo `****` (por defecto). Nunca se incluye el `.env` real.
7. **Horario y avisos:** diario 3:00 a. m. hora de Colombia. Correo inmediato si falla (qué paso falló) + resumen
   semanal los lunes (aunque todo esté bien) + una línea por corrida en un log del servidor. Destinatarios:
   `jveyes@gmail.com`, `info@papyrus.com.co` (variable `RESPALDO_CORREO_AVISOS`, por servidor). Envío por el SMTP del
   sistema.
8. **Restauración con 6 protecciones** (`restaurar.sh <carpeta>`): (1) verifica checksums del manifiesto; (2) mismo
   sistema: dominio/conjunto del manifiesto = destino, salvo `--otro-destino`; (3) versión compatible: BD más nueva que
   el código → se niega y pide desplegar el `sistema.tar.gz` de ese respaldo; más vieja → restaura y aplica migraciones;
   (4) respaldo automático de la BD actual antes (`antes_de_restaurar_<fecha>`); (5) confirmación escribiendo el
   dominio; (6) detiene app e importador, restaura, reinicia y verifica `/health`. "La idea es que correspondan".
9. **Pantalla "Respaldos" en `/administracion`** (solo ADMIN): descargar el respaldo de la fecha elegida o el último
   como `.zip`; botón para copiar las fotos de S3 al disco del servidor (incremental: la primera vez todas, después
   solo las nuevas), en segundo plano con avance visible; luego descargarlas. La llave de fotos gana permiso de leer y
   listar SOLO ese bucket.
10. **Descarga de fotos:** "Solo las nuevas" (desde la última descarga, registrada POR SISTEMA) y "Todas"; la pantalla
    muestra fecha de la última descarga y cuántas nuevas hay (≈ tamaño). Misma estructura de carpetas que S3.
11. **Restaurar SOLO por SSH** con `restaurar.sh`; la pantalla explica los pasos y muestra el comando exacto listo para
    copiar para el respaldo elegido. Nada de botón "Restaurar" en la web.
12. **Prueba de restauración automática semanal** (domingos de madrugada): Postgres temporal aparte en el mismo
    servidor, restaura el último respaldo, verifica `pg_restore` sin errores + versión Alembic = manifiesto + conteos
    = manifiesto, lo borra; resultado en el resumen del lunes, correo inmediato si falla.
13. **Varios servidores:** un solo bucket (`paquetex-respaldos`) con una carpeta por dominio
    (`test.papyrus.com.co/`, `elclub.papyrus.com.co/`, ...), cada una con `diario/ mensual/ anual/ puntual/`. Una llave
    por servidor limitada a su carpeta. test también se respalda.
14. **Respaldos puntuales** en `puntual/` (30 días): automático antes de cada deploy (paso en GitHub Actions, antes de
    migrar) + botón "Respaldar ahora". Aclarado con Jesús: es por la BASE DE DATOS (las migraciones la cambian y
    GitHub no la guarda); el código del momento va emparejado en el mismo respaldo.
15. **AWS:** Claude prepara políticas, reglas y scripts como archivos en el repo (sin secretos) y crea los recursos en
    la cuenta `172460160630` con la AWS CLI de la PC; instala las llaves nuevas directo en el `.env` del servidor por
    SSH, sin mostrarlas ni guardarlas en el repo. El resto del `.env` es de Jesús.
16. **Destinatarios de avisos:** `jveyes@gmail.com` e `info@papyrus.com.co`.

## Por defecto (sin objeción de Jesús)

- Copia local de fotos fuera del checkout: `/home/ubuntu/paquetex-fotos-copia`.
- Aviso por correo si el disco del servidor pasa del 80 %.
- Se implementa y prueba primero en test.papyrus.com.co; luego se replica en producción.

## Fuera de alcance

- Cifrado propio de las copias (decisión 4).
- Botón de restauración en la web (decisión 11).
- Fotos dentro del respaldo diario (decisión 1).
- Un tercer destino fuera de AWS (Drive, Backblaze...): mencionado como posible a futuro, no pedido.

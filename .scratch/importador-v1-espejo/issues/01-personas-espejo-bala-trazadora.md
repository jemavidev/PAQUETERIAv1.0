# 01 — Bala trazadora: Personas espejo de punta a punta

**What to build:** el primer recorrido completo del importador espejo v1 → v2 (ver `../spec.md`), solo para residentes. Al correr el script contra una base v1, cada `customers` aparece como **Persona** en la v2, sin apartamento, con el mismo teléfono (`+57…`), nombre (`full_name`) y email. Correrlo otra vez no cambia nada. Si alguien renombra en la v2 una Persona importada, la siguiente pasada la devuelve a lo que diga la v1. Si ya existía una Persona nativa con ese teléfono, se adopta. Incluye el esqueleto que usan todos los tickets siguientes: el servicio de dominio `sincronizar_desde_v1(session, instantanea_v1, copiador_fotos, modo) → ReporteSincronizacion`, la instantánea de filas planas de la v1, el lector SQL de solo lectura, el script con `--simular` y el reporte por entidad.

**Blocked by:** None — can start immediately

**Status:** done

- [x] Migración Alembic: columna nullable `origen_v1_id` en `personas`, con índice único parcial (donde no es nula). La prueba de paridad ORM/esquema sigue en verde.
- [x] El servicio vive en el paquete de dominio aislado y no importa nada del mundo viejo (ADR-0004).
- [x] Crea una Persona por cliente de la v1, incluidos los que no tienen paquetes. `apartamento_actual_id` y `terminos_aceptados_en` quedan en `NULL`.
- [x] Idempotencia: una segunda pasada con la misma instantánea reporta 0 creados, 0 actualizados y 0 errores.
- [x] La v1 gana: los campos importados que se editaron en la v2 se sobresciben en la siguiente pasada.
- [x] Adopción: una Persona nativa con el mismo teléfono recibe el `origen_v1_id` y los datos de la v1, sin duplicarse.
- [x] Las Personas sin `origen_v1_id` y sin teléfono coincidente no se tocan.
- [x] `--simular`: calcula y reporta igual que una pasada real, pero la base de la v2 queda sin cambios.
- [x] No se envía ningún aviso (se verifica con los senders falsos existentes).
- [x] El lector de la v1 abre la conexión en solo lectura y normaliza las fechas a UTC. El script lee las credenciales del entorno e imprime el reporte.
- [x] Pruebas en `tests/data_model` con instantáneas armadas en memoria, siguiendo el patrón de `test_importar_contactos_externos.py`.

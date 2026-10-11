# 430 — `PUBLIC_BASE_URL` fijo en test dentro de `docker-compose.yml`

**Origen:** análisis de enlaces, hallazgo 3. Jesús: "corrige los 3 problemas que encontraste".

**Status:** verificado — cerrado por Jesús 2026-10-11 (en producción). Antes: desplegado en test (`a3bda27`, 2026-09-27), pendiente confirmar en vivo

## Contexto

`PUBLIC_BASE_URL` es la base de los enlaces que salen de la app (SMS/WhatsApp `/consultar?q=`, pie del correo,
restablecer contraseña). En el repo de despliegue estaba escrita a mano (`PUBLIC_BASE_URL: https://test.papyrus.com.co`
en `docker-compose.yml`): el día del paso a producción, con el mismo archivo, los residentes recibirían enlaces a test.
Además, el mensaje de WhatsApp de Acciones caía a un enlace relativo (inservible fuera de la app) si la variable faltaba.

## Decisiones

- `docker-compose.yml` la lee del `.env` del servidor (`${PUBLIC_BASE_URL}`), como el resto de las variables propias
  del despliegue; el `.env` de test lleva `https://test.papyrus.com.co`. Va con el próximo deploy (repo
  `jemavidev/PaqueteX`), y el `.env` se ajusta ANTES de ese push.
- La app se niega a arrancar en `staging`/`production` sin `PUBLIC_BASE_URL` (falla al iniciar, no al primer SMS): así
  ningún enlace relativo puede salir en una notificación.

## Pendiente para el próximo deploy (repo `jemavidev/PaqueteX`)

1. ANTES del push: agregar `PUBLIC_BASE_URL=https://test.papyrus.com.co` al `.env` del servidor de test (hoy no está:
   viene fija del compose).
2. En `docker-compose.yml`, cambiar `PUBLIC_BASE_URL: https://test.papyrus.com.co` por
   `PUBLIC_BASE_URL: ${PUBLIC_BASE_URL:?falta PUBLIC_BASE_URL en el .env}` y actualizar el comentario (ya no es
   "literal, inherente a este despliegue").
3. Documentada en `CODE/.env.staging.example`.

## Verificación

- `tests/web/test_arranque_produccion.py::test_fuera_de_desarrollo_no_arranca_sin_public_base_url` (production y
  staging; fallaban antes). La parte del `docker-compose.yml` queda para el deploy (arriba).

## Deploy (2026-09-27, `a3bda27`)

- `.env` del servidor de test: `PUBLIC_BASE_URL=https://test.papyrus.com.co` agregado ANTES del push (respaldo previo en
  `.env.bak-2026-09-27b`). `docker-compose.yml` ahora usa `${PUBLIC_BASE_URL:?...}` (validado con `docker compose config`
  contra ese `.env` antes del push). En vivo: el contenedor la tiene y `/health` responde.
- **En producción**, el `.env` de ese servidor tiene que llevar su propio dominio: sin la variable, el contenedor no arranca.

# 09 — Salida a producción y glosario

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** El despliegue deja a todos los Usuarios en el flujo nuevo. Se cierran todas las sesiones de staff abiertas, y en su siguiente ingreso cada uno entra con contraseña y crea su PIN. La llave HMAC del PIN existe en el entorno de despliegue. El glosario recoge los términos nuevos.

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08.

**Status:** implementado localmente · pendiente: deploy a test (solo cuando se pida)

- [x] Invalidación de las sesiones de staff al desplegar: subir la versión de sesión de todos (migración o comando operativo), sin tocar las sesiones de cliente.
- [ ] La llave HMAC del PIN se agrega a la configuración del repo de despliegue (`jemavidev/PaqueteX`) y al entorno de test, generada al azar y nunca commiteada.
- [x] Se reconstruye `tailwind.css` si hubo clases nuevas en las plantillas (el Dockerfile de despliegue no lo hace).
- [x] Glosario de `CONTEXT.md`: PIN, Dispositivo registrado, Operador activo y Bloqueo.
- [x] La suite completa corre verde con el comando del CI (`pytest` sin rutas) y con `-m browser`.
- [ ] Verificación en `test.papyrus.com.co`, en celular y escritorio: primer ingreso y creación del PIN, cambio entre dos Usuarios con PIN, bloqueo por inactividad, y fotos subiendo con el equipo bloqueado.

## Comments

- **Invalidación de sesiones: automática, sin migración ni comando.** Una sesión de staff abierta antes del despliegue no trae la cookie del equipo (`paquetex_dispositivo`), así que `current_staff` la rechaza y manda a `/ingresar`. Al entrar, cada Usuario crea su PIN. Lo cubre `test_sin_la_cookie_del_equipo_la_sesion_no_vale`.
- **`tailwind.css`:** no hace falta reconstruirlo. Se verificó que todas las clases usadas en las plantillas nuevas ya existen en el CSS compilado. El teclado y la capa usan estilos propios (`.teclado-pin`, `.capa-bloqueo`).
- **Glosario:** se agregaron PIN, Dispositivo registrado, Operador activo y Bloqueo (este distinto de "Bloqueado", el estado del residente).
- **Suites:** web + data_model + infra en verde (2409 tras el ticket 08) y `-m browser` en verde (94).
- **Ambiente local:** migraciones 0068 y 0069 aplicadas a la BD de desarrollo, y uvicorn de `:8010` reiniciado. Un login real lleva a "Crea tu PIN".
- **PENDIENTE, solo cuando se pida el deploy:**
  1. Generar `PIN_SECRET_KEY` al azar y agregarla al `.env` del servidor **y** al bloque `environment:` de `docker-compose.yml` en el repo de despliegue (`jemavidev/PaqueteX`). Con `WEB_ENV=production` es obligatoria: sin ella, entrar falla con RuntimeError. Documentada en `.env.staging.example`.
  2. Llevar los archivos al repo de despliegue (diff por archivo, sin `git subtree`).
  3. Verificar en `test.papyrus.com.co`, en celular y escritorio: crear el PIN al primer ingreso, cambio entre dos Usuarios con PIN, bloqueo por inactividad y fotos subiendo con el equipo bloqueado.

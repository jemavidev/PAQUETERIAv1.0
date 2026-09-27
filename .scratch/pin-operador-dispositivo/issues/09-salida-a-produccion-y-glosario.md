# 09 — Salida a producción y glosario

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** El despliegue deja a todos los Usuarios en el flujo nuevo. Se cierran todas las sesiones de staff abiertas, y en su siguiente ingreso cada uno entra con contraseña y crea su PIN. La llave HMAC del PIN existe en el entorno de despliegue. El glosario recoge los términos nuevos.

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08.

**Status:** ready-for-agent

- [ ] Invalidación de las sesiones de staff al desplegar: subir la versión de sesión de todos (migración o comando operativo), sin tocar las sesiones de cliente.
- [ ] La llave HMAC del PIN se agrega a la configuración del repo de despliegue (`jemavidev/PaqueteX`) y al entorno de test, generada al azar y nunca commiteada.
- [ ] Se reconstruye `tailwind.css` si hubo clases nuevas en las plantillas (el Dockerfile de despliegue no lo hace).
- [ ] Glosario de `CONTEXT.md`: PIN, Dispositivo registrado, Operador activo y Bloqueo.
- [ ] La suite completa corre verde con el comando del CI (`pytest` sin rutas) y con `-m browser`.
- [ ] Verificación en `test.papyrus.com.co`, en celular y escritorio: primer ingreso y creación del PIN, cambio entre dos Usuarios con PIN, bloqueo por inactividad, y fotos subiendo con el equipo bloqueado.

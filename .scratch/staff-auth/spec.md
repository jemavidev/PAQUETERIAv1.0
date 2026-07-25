# Spec — Autenticación de staff (login usuario/contraseña + actor de sesión)

Status: ready-for-agent
Feature: staff-auth
Branch: PaqueteXv.2
Depende de: `data-model` (entidad `Usuario`, roles ADMIN/OPERADOR), `package-lifecycle` (transiciones que exigen un `actor`), `announce-web` (capa web clean-room).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §9/§14 · `CONTEXT.md` (Usuario, "el actor sale de la sesión real") · ADR-0004

---

## Problem Statement

El staff no puede **entrar al sistema**. La entidad `Usuario` (ADMIN/OPERADOR) existe como esqueleto pero **no tiene credenciales** (ni email ni contraseña), no hay login, ni sesión, ni forma de saber **quién** es el operador que ejecuta una acción. Y la máquina de estados (`recibir/entregar/cancelar`) ya **exige un `actor: Usuario`** que "sale de la sesión real, nunca hardcodeado" — pero no hay sesión que lo produzca. Sin esto, ninguna vista con privilegios (`/packages` y sus modales) puede construirse.

Desde la perspectiva del staff: llega a operar y no hay dónde iniciar sesión; desde la del administrador: no hay forma de dar de alta a un operador; desde la de auditoría: las acciones no pueden atribuirse a una persona real.

## Solution

Autenticación de staff con **usuario/email + contraseña fuerte** (brief §9), **entidad separada** de los clientes, que produce una **sesión** de la que sale el `actor` de cada acción:

- El staff inicia sesión en `/auth/login` con **email + contraseña**; el sistema verifica el hash y abre una **sesión** (cookie firmada).
- Una **dependencia `current_staff`** lee la sesión y entrega el `Usuario` actual — el **actor** para la máquina de estados y la **puerta** de las rutas con privilegios (sin sesión → a login).
- **Solo un ADMIN crea cuentas de staff** (`create_staff`); el **primer** ADMIN se siembra por un bootstrap operativo (no expuesto por HTTP).
- La contraseña se guarda **hasheada** (nunca en claro); se exige una política de contraseña fuerte al crearla.
- El staff cierra sesión en `/auth/logout`.

No depende del proveedor SMS para entrar (elegido sobre OTP-para-staff porque las cuentas de staff tienen poder destructivo; brief §9).

## User Stories

1. Como **staff**, quiero iniciar sesión con mi **email y contraseña** en `/auth/login`, para entrar a operar.
2. Como **staff**, quiero que una contraseña **incorrecta** (o un email inexistente) se **rechace** con un mensaje genérico, para no filtrar qué email existe.
3. Como **staff**, quiero que al iniciar sesión se abra una **sesión persistente** (cookie), para no re-autenticarme en cada acción.
4. Como **staff**, quiero **cerrar sesión** en `/auth/logout`, para dejar el equipo seguro.
5. Como **staff**, quiero que las **rutas con privilegios** me manden a `/auth/login` si no tengo sesión, para que nada operativo quede expuesto.
6. Como **operador**, quiero que cuando **reciba/entregue/cancele** un paquete quede registrado que **fui yo** (mi `Usuario` de sesión es el actor), para trazabilidad.
7. Como **administrador**, quiero **crear cuentas de staff** (email, nombre, rol, contraseña), para dar de alta operadores.
8. Como **administrador**, quiero que **solo un ADMIN** pueda crear cuentas de staff, para que un operador no escale privilegios.
9. Como **operador**, quiero que si intento crear una cuenta se me **rechace** (no soy admin), para respetar la regla.
10. Como **dueño**, quiero **sembrar el primer ADMIN** por un bootstrap operativo (no por HTTP), para resolver el arranque sin un admin previo.
11. Como **administrador**, quiero que no se puedan crear **dos cuentas con el mismo email**, para que el email sea una llave de acceso única.
12. Como **administrador**, quiero que las contraseñas se guarden **hasheadas** (nunca en claro), para que una filtración de la BD no exponga credenciales.
13. Como **administrador**, quiero que se exija una **contraseña fuerte** (longitud mínima, no trivial) al crear/cambiar, para reducir el riesgo de cuentas débiles.
14. Como **staff**, quiero que mi rol (`ADMIN`/`OPERADOR`) viaje en mi identidad de sesión, para que las rutas sepan qué puedo hacer.
15. Como **auditor**, quiero que la identidad del actor siempre venga de la sesión verificada y **nunca** de un id enviado por el cliente, para que la atribución sea confiable.
16. Como **QA**, quiero poder probar login/logout y una ruta protegida de punta a punta (con y sin sesión), para confiar en la puerta.
17. Como **operador**, quiero un mensaje claro si mi sesión **expiró**, para volver a entrar sin confusión.
18. Como **dueño**, quiero que la app **no dependa del proveedor SMS** para que el staff entre, para poder operar aunque el SMS falle (brief §9).

## Implementation Decisions

### Credenciales en `Usuario` (migración `0005`, descendiente de `0004`)

- Añadir a `usuarios`: `email` (**único**, nullable a nivel de columna) y `password_hash` (nullable). Constraints con **nombre explícito** en ORM y migración (paridad esquema↔ORM). Nullable porque un `Usuario` puede existir como **actor sin credenciales** (así no se rompen los tests de lifecycle que crean actores mínimos); en producción todo staff real tiene ambos. Login exige que estén presentes.
- Árbol Alembic de **raíz única** (ADR-0002): `0001→0002→0003→0004→0005`, `heads` = 1.

### Hashing y política de contraseña

- Hash con un algoritmo fuerte y lento (bcrypt vía `passlib`, nueva dep del arnés). El hash nunca se registra ni se devuelve.
- Política de contraseña fuerte (longitud mínima razonable, no vacía/ni trivial) validada al **crear/cambiar**; `ValueError` si no cumple.

### Servicios de dominio (costura existente — Seam A)

- `create_staff(session, actor, email, nombre, password, rol)` → crea un `Usuario` con credenciales. **Exige `actor.rol == ADMIN`** (si no, `PermissionError`); email único (`ValueError`/conflicto si repetido); hashea la contraseña; valida su fortaleza.
- `create_initial_admin(session, email, nombre, password)` → **bootstrap**: crea el primer ADMIN **sin** actor. Solo cuando no existe ningún ADMIN (idempotencia/guardia). No se expone por HTTP; lo usa una tarea/CLI operativa.
- `verify_credentials(session, email, password) -> Usuario | None` → busca por email y verifica el hash; `None` si no coincide (sin distinguir email-inexistente de contraseña-mala, para no filtrar).

### Sesión y dependencias (capa web — ADR-0004)

- **Sesión por cookie firmada** (middleware de sesión de Starlette) que guarda el `usuario_id`. Requiere `SECRET_KEY` — se añade al settings mínimo del web (`SECRET_KEY` desde el entorno; en dev un default explícito de desarrollo, en prod obligatorio).
- **`current_staff`**: dependencia que lee `usuario_id` de la sesión, carga el `Usuario` y lo entrega; sin sesión (o Usuario inexistente) → redirige a `/auth/login` (o 401 según el consumidor). Es la fuente del **actor** para las transiciones y la puerta de las rutas privilegiadas.
- **`require_admin`**: variante que además exige `rol == ADMIN` para rutas de administración.

### Rutas (capa web)

- `GET /auth/login` (formulario email+contraseña), `POST /auth/login` (verifica → abre sesión → redirige), `POST /auth/logout` (cierra sesión). Server-rendered, mobile-first, patrón del `/announce` (JS con `finally`, validación server-side, mensajes genéricos).
- La creación de cuentas de staff por un admin vive en `/admin` (rebanada aparte); esta rebanada entrega `create_staff` + `require_admin` que esa vista usará.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable** — que un login válido abre sesión y uno inválido no; que una ruta protegida rechaza sin sesión y admite con ella; que `create_staff` respeta la regla de admin y la unicidad de email; que la contraseña se guarda hasheada (no en claro) — sin inspeccionar el algoritmo ni el HTML exacto.

**Costuras (ambas EXISTENTES, ninguna nueva):**
- **Dominio (Seam A):** `create_staff`, `create_initial_admin`, `verify_credentials`, política de contraseña — contra el Postgres efímero (`tests/` shared harness). Casos: admin crea staff; operador NO puede (`PermissionError`); email duplicado rechazado; bootstrap crea el primer admin; `verify_credentials` acepta la correcta y rechaza la mala/el email inexistente por igual; el `password_hash` guardado **no** es la contraseña en claro.
- **HTTP (Seam web):** `TestClient` (arnés `tests/web`). Casos: `GET /auth/login` → 200; `POST` con credenciales válidas → abre sesión + redirige; con inválidas → re-render con error genérico, sin sesión; una **ruta protegida de prueba** con `current_staff` → sin sesión redirige/401, con sesión responde y expone el `Usuario` correcto como actor; `logout` cierra la sesión.

**Prior art:** los tests de dominio (`tests/data_model`) y de web (`tests/web/test_announce.py`). Construir **test-first** con `/tdd`.

## Out of Scope

- **OTP de clientes por teléfono** (el otro mecanismo de auth, brief §9) — rebanada aparte.
- **`/packages`** y sus modales — consumen `current_staff`, pero son otra rebanada.
- **`/admin`** (UI de alta de staff, plantillas, residencias) — usa `create_staff`/`require_admin`, rebanada aparte.
- **Recuperación de contraseña** (`/auth/forgot-password`, reset por email) y **MFA** — futuros; brief los deja como opcionales.
- **`/customer/verify`** y vistas de cliente.
- **Rate-limiting / lockout** de intentos de login — endurecimiento posterior (existe `rate_limiting.py` viejo, se integrará luego).

## Further Notes

- **Bootstrap del primer admin**: es el clásico huevo-gallina de "solo un admin crea staff". Se resuelve con `create_initial_admin` operativo (CLI/tarea), fuera de HTTP y guardado para no crear un segundo admin por esa vía. No es un ADR (es un patrón conocido), pero conviene documentarlo en la guía de operación.
- **Mensajes genéricos**: login fallido no revela si el email existe (historia 2) — decisión de seguridad, no de UX.
- **`SECRET_KEY`** entra al settings del web (hasta ahora solo tenía `DATABASE_URL`); en prod es obligatorio, en dev un default explícito de desarrollo.
- **Consumo aguas abajo:** `current_staff` es la pieza que `/packages` usará como **actor** de `recibir/entregar/cancelar`; cierra el invariante "el actor sale de la sesión real".
- **Decisión abierta menor (elijo default):** sesión por **cookie firmada** (stateless, liviano) en vez de sesión server-side en Redis; si se quiere revocación inmediata a futuro, se migra sin cambiar el modelo.

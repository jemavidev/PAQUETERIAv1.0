# 02 — Login de staff + sesión + `current_staff` (web)

**Spec:** `.scratch/staff-auth/spec.md` · **Glosario:** Usuario, "el actor sale de la sesión real" · **ADR:** 0004 (capa web clean-room)

**What to build:** El staff **inicia sesión** en `/auth/login` con email + contraseña, obtiene una **sesión**, y las **rutas con privilegios se abren solo con esa sesión** (dependencia `current_staff`, que además es el **actor** de la máquina de estados). Cierra sesión en `/auth/logout`.

**Blocked by:** 01 — Credenciales de staff + creación (dominio). Necesita `verify_credentials` y una cuenta de staff con la que entrar.

**Status:** ready-for-agent

- [ ] `SECRET_KEY` en el settings del web (obligatorio en prod, default explícito de desarrollo) + **middleware de sesión** (cookie firmada) montado en el app.
- [ ] `GET /auth/login` → 200: formulario email + contraseña (mobile-first, patrón del `/announce`: validación server-side, JS con `finally`).
- [ ] `POST /auth/login`: credenciales válidas (`verify_credentials`) → **abre sesión** (guarda `usuario_id`) + redirige; inválidas → re-render con **mensaje genérico** (no revela si el email existe), **sin** sesión.
- [ ] `POST /auth/logout` → **cierra** la sesión.
- [ ] Dependencia **`current_staff`**: lee la sesión → carga el `Usuario` → lo entrega (el **actor**); sin sesión (o Usuario inexistente) → redirige a `/auth/login` (o 401 según el consumidor). **`require_admin`** exige `rol == ADMIN`.
- [ ] Una **ruta protegida de prueba** con `current_staff`: **sin** sesión rechaza; **con** sesión responde y expone el `Usuario` correcto como actor.
- [ ] Tests (web `TestClient`): `GET /auth/login` → 200; `POST` válido abre sesión + redirige; `POST` inválido → mensaje genérico + sin sesión; ruta protegida **sin** sesión rechaza y **con** sesión responde; `logout` cierra la sesión.

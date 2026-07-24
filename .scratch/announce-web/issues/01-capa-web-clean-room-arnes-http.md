# 01 — Capa web clean-room + arnés HTTP

**Spec:** `.scratch/announce-web/spec.md` · **ADR:** 0004 (rebuild aislado / strangler fig)

**What to build:** El rebuild tiene su **propia puerta de entrada HTTP**: una app FastAPI nueva que **arranca sin credenciales AWS**, con su dependencia de sesión de BD, su setup de templates/estáticos, y un arnés de test HTTP. Se verifica sola con una ruta trivial `GET /health` que responde 200 desde un `TestClient`.

**Blocked by:** None — el dominio (`app/domain/`, servicio `announce`) y el arnés de Postgres efímero ya están.

**Status:** ready-for-agent

- [ ] App factory FastAPI **nuevo** (paquete web propio del rebuild) que **arranca sin credenciales AWS/S3** y **sin importar** `app/config.py` / `app/main.py` / rutas legacy (ADR-0004). Lee la conexión desde `DATABASE_URL` (o un settings mínimo del rebuild).
- [ ] **Dependencia de sesión de BD propia**: entrega una `Session` por request con **commit al éxito / rollback al error**, sobre un engine desde `DATABASE_URL`. NO reutiliza el `get_db` viejo (atado al config con AWS).
- [ ] Setup de **templates server-rendered** (Jinja2) + estáticos, listo para Tailwind + Alpine/HTMX (cero Node en runtime).
- [ ] Ruta trivial `GET /health` → 200 (smoke de que el app monta y responde).
- [ ] **Arnés de test HTTP**: `TestClient` de FastAPI sobre el app nuevo, con la BD = Postgres efímero construido con `alembic upgrade head` (reutiliza `tests/data_model`/conftest). Tests: `GET /health` → 200; el app **importa y arranca sin** variables AWS en el entorno.

---
status: accepted
---

# El rebuild vive en paquetes nuevos aislados y reemplaza la app vieja incrementalmente (strangler fig)

El código del rebuild (PaqueteXv.2) se construye en **paquetes nuevos y aislados** — `app/domain/` (modelo + servicios) y `app/web/` (capa HTTP) — que **no importan el mundo viejo** (`app/config.py`, `app/models/*`, `app/main.py`, rutas legacy) y que **reemplazan la app anterior rebanada por rebanada** (patrón *strangler fig*). Elegido porque el `config.py` viejo **lanza al arrancar sin credenciales AWS S3** (`_validate_required_settings`) y su app factory importa todo el subsistema fuera de alcance (facturas/CUFE): construir "en su lugar" acoplaría el rebuild a un grafo de imports roto y fuera de alcance.

## Considered Options

- **Extender la app vieja in situ** (hacer AWS opcional en `config.py`, añadir las rutas nuevas al app factory existente, reutilizar su `get_db`). Rechazado: acopla el rebuild al import-graph legacy roto/fuera de alcance; un cambio en el mundo viejo puede romper el nuevo; arrastra facturas/CUFE/S3 que no se tocan.
- **Rebuild aislado (elegido):** paquetes nuevos que arrancan solos (sin AWS), con su propio bootstrap web y su propia dependencia de sesión; la app vieja se estrangula ruta por ruta.

## Consequences

- Durante la migración **coexisten dos apps FastAPI** (vieja `src/main.py` + nueva `app/web`) y dos dependencias de sesión de BD — deuda temporal aceptada a cambio de aislamiento y tests limpios.
- Los tests del rebuild corren contra el esquema nuevo (`alembic upgrade head`) sin tocar el `config`/credenciales viejos (ver el arnés `tests/data_model`).
- Cada rebanada HTTP nueva monta su ruta en el app nuevo; `src/main.py` se retira cuando no quede ruta legacy en uso.
- Coherente con [ADR-0002](0002-arbol-alembic-raiz-unica.md) (árbol Alembic de raíz única): el rebuild parte de cero también en persistencia.

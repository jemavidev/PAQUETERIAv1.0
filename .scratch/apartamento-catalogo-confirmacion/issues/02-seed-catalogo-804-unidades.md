# 02 — Seed del catálogo de 804 unidades

**What to build:** migración Alembic que siembra exactamente 804 filas en `apartamentos` — la terna `(conjunto, torre, apartamento)` de cada una de las unidades reales del conjunto (10 torres), tal como quedó verificada y corregida con el cliente (Torre 3, Piso 3 corregido a `301-308`; catálogo completo en `.scratch/apartamento-catalogo-confirmacion/spec.md`). El valor de `conjunto` para las 804 filas es el nombre vigente en el registro singleton del ticket 01 ("El Club"). No cambia ningún comportamiento todavía — `get_or_create_apartamento` sigue creando bajo demanda hasta el ticket 03; esta migración es puramente aditiva.

**Blocked by:** 01 (necesita el nombre de Conjunto ya sembrado).

**Status:** done

- [x] Migración Alembic siembra las 804 filas, una por unidad del catálogo. Generadas por código a partir de `{piso: cantidad}` por torre (cada piso son las unidades `piso*100+1..+cantidad`, patrón que las 10 torres cumplen sin excepción) — no 804 tuplas tipeadas a mano, para no reintroducir un error de transcripción como el que tenía el listado original.
- [x] Las 804 ternas son exactamente las del catálogo corregido — ninguna de más, ninguna de menos, sin el duplicado `303` que traía el listado original de Torre 3 (test dedicado que verifica cero ternas repetidas).
- [x] `conjunto` de las 804 filas coincide con el nombre vigente al momento de correr la migración — leído con SQL directo a `configuracion_conjunto` (fila si ya existe, si no `"EL CLUB"`, mismo fallback que `configuracion_conjunto_service`, pero sin importar código de la app dentro de la migración).
- [x] `alembic upgrade head` sobre Postgres vacío deja exactamente 804 filas en `apartamentos`; `downgrade` revierte limpio (round-trip, Seam B) — borra por `(torre, apartamento)`, no por `conjunto` (que pudo haberse renombrado después del seed).
- [x] Test que cuenta filas por torre coincide con lo documentado en el spec (38/56/100/104×4/100/56/38).
- [x] `get_or_create_apartamento` con una terna real del catálogo reutiliza la fila sembrada (no crea una nueva) — confirma que seed y dedup por terna conviven bien, antes de que el ticket 03 cambie su semántica.

## Implementación

- **Migración:** `alembic/versions/0021_seed_catalogo_apartamentos.py` (`down_revision = 0020_configuracion_conjunto`). El catálogo vive como `{piso: cantidad}` por cada una de las 10 torres (4 formas distintas, reutilizadas entre torres gemelas: Torres 1/10, 2/9, 3/8 idénticas entre sí; 4/5/6/7 idénticas entre sí) — generado en tiempo de migración, no una lista literal de 804 filas.
- **Regresión detectada y corregida:** 4 tests preexistentes (`test_apartamento_service.py` ×3, `test_paquete_correccion_service.py` ×1) asumían la tabla `apartamentos` vacía al arrancar (`db_session` corre sobre una BD migrada UNA vez por sesión de test) — con el seed ya sembrado, esos conteos absolutos (`== 1`, `== 2`, `== 0`) rompieron. Corregidos a medir contra una línea base capturada al inicio de cada test (`total_antes = ...count()`), no contra cero — sin tocar el comportamiento que esos tests realmente verifican.
- **Tests nuevos:** `tests/data_model/test_apartamento_seed.py` (6, Seam B + una de dominio) — total de filas, conteo por torre, `conjunto` uniforme, sin ternas duplicadas, round-trip de migración, reutilización vía `get_or_create_apartamento`.
- **Suite completa:** 579 passed (6 deselected — los mismos fallos preexistentes de `tests/web/test_layout.py` del ticket 01, no relacionados).

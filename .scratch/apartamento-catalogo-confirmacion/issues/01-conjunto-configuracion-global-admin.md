# 01 — Conjunto: configuración global editable solo por ADMIN

**What to build:** entidad nueva y liviana que guarda el nombre vigente del Conjunto residencial — un único registro en todo momento (singleton, no una lista). Valor inicial sembrado: "El Club". Función de dominio para leer el nombre vigente y otra para renombrarlo, esta última exigiendo un actor `ADMIN` (reusa `require_admin`, el mismo guard que ya protege `/administracion/personal` — `OPERADOR` queda rechazado). Pantalla nueva bajo `/administracion` con un campo de texto + guardar, sin lista ni CRUD de varios Conjuntos. Renombrar es una operación transaccional que, además de actualizar el registro singleton, deja lista la sincronización hacia `apartamentos.conjunto` para cuando existan filas ahí (ver ticket 02) — un `UPDATE` en bloque, nunca desincronizado.

**Blocked by:** Ninguno — puede empezar de inmediato.

**Status:** done

- [x] Migración Alembic crea la tabla singleton. Ajuste sobre el plan original: **no siembra una fila** — sigue el patrón ya establecido de `PlantillaNotificacion` (tabla de override): sin fila, el dominio devuelve el default hardcodeado `"El Club"`; la fila solo aparece cuando un ADMIN renombra por primera vez. Mismo comportamiento observable ("El Club" hasta que alguien lo cambie), menos una migración de datos y sin el problema de truncado-sin-reseed entre tests web.
- [x] Función de dominio para leer el nombre vigente del Conjunto (`obtener_nombre_conjunto`).
- [x] Función de dominio para renombrarlo (`renombrar_conjunto`), actualiza el singleton y hace `UPDATE` en bloque de `apartamentos.conjunto` (no falla si `apartamentos` está vacía todavía — el ticket 02 la puebla después).
- [x] Renombrar exige actor `ADMIN`; `OPERADOR` o ausencia de sesión de staff es rechazado.
- [x] Pantalla nueva en `/administracion/conjunto` (mismo árbol que `/administracion/personal`) con el nombre actual y un formulario de renombrar, protegida por `require_admin`.
- [x] Tests de dominio: valor por defecto sin fila; `ADMIN` renombra y la lectura posterior refleja el cambio; `OPERADOR` rechazado (con aserción de que no tocó nada); renombrar con un Apartamento ya existente sincroniza su `conjunto` y no deja ninguno con el nombre anterior.

## Implementación

- **Dominio:** `app/domain/configuracion_conjunto.py` (modelo `ConfiguracionConjunto`, tabla `configuracion_conjunto`) + `app/domain/configuracion_conjunto_service.py` (`obtener_nombre_conjunto`, `renombrar_conjunto`). Nombre normalizado con `texto.normalizar_nombre` (MAYÚSCULAS), igual que `Apartamento.conjunto` — necesario para que la sincronización compare/actualice correctamente (un test lo atrapó: comparar `"El Club"` sin normalizar contra `"EL CLUB"` ya persistido no encontraba nada que actualizar).
- **Migración:** `alembic/versions/0020_configuracion_conjunto.py` (`down_revision = 0019_persona_auto_recepcion`), solo crea la tabla — sin seed de datos (ver nota arriba).
- **Web:** dos rutas nuevas en `app/web/routes/admin.py` (`GET`/`POST /administracion/conjunto`), protegidas por `require_admin`, mismo patrón que `/administracion/notificaciones`. Template `admin/conjunto.html` (reusa `formulario_flujo`/`input_texto`/`toast` del design system). Ícono `conjunto` nuevo en `icons.py` (Heroicons solid "office-building") + enlace nuevo en el menú de administración de `base.html`.
- **Tests:** `tests/data_model/test_configuracion_conjunto_service.py` (4, Seam A) + `tests/web/test_admin_conjunto.py` (6, gate `require_admin` + persistencia). `configuracion_conjunto` agregada a `test_parity_esquema_orm.py` y a `_TABLAS` en `tests/web/conftest.py` (trunca entre tests web; al no tener fila, `obtener_nombre_conjunto` vuelve sola al default — mismo patrón que `plantillas_notificacion`, sin necesidad de reseed).
- **Suite completa:** 573 passed (6 deselected — `tests/web/test_layout.py`, fallos **preexistentes en la rama**, confirmados reproduciendo sin mis cambios vía `git stash`; no relacionados con este ticket).

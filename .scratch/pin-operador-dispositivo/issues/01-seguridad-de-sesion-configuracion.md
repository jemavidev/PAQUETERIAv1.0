# 01 — Sección "Seguridad de sesión" en /administracion/conjunto

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** El ADMIN ve en `/administracion/conjunto` una sección "Seguridad de sesión" con dos campos: **segundos de inactividad antes del bloqueo** (60–3600, 300 por defecto) y **días de vigencia del registro de un dispositivo** (1–90, 15 por defecto). Guarda los valores y el sistema los lee en cada petición, así que un cambio aplica de inmediato. Por ahora nadie los consume; los usan los tickets 02 y 04.

**Blocked by:** None — can start immediately.

**Status:** done · 6 tests nuevos verdes

- [x] La configuración del conjunto suma los dos campos, con sus valores por defecto para la fila ya existente (migración descendiente de la cabeza actual, `alembic heads` = 1, guard de paridad esquema↔ORM verde).
- [x] La sección solo la ve y guarda un ADMIN; para un OPERADOR, la ruta de guardado responde 403.
- [x] Un valor fuera de rango, vacío o no numérico se rechaza con un mensaje claro y no se guarda nada.
- [x] Una función de dominio devuelve los dos valores vigentes (el ticket 02 la consume).
- [x] Pruebas en la costura web: se ven los valores por defecto, un guardado válido se refleja en la siguiente petición, se rechazan los valores fuera de rango, y el OPERADOR recibe 403.

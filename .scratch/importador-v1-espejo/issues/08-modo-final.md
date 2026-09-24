# 08 — Modo `--final`

**What to build:** el día del corte, una pasada que solo termina bien si el espejo quedó completo y limpio, para apuntar el dominio con confianza (ver `../spec.md`, historia 44).

**Blocked by:** 07 — Borrado reflejado con tope del 5 %

**Status:** done

- [x] En modo final, cualquier choque de `access_code`, error de entidad, `changed_by` desconocido, foto fallida o alerta del 5 % hace fallar la pasada y revierte la escritura en la base.
- [x] El script termina con un código distinto de cero ante una alerta (en cualquier modo) y ante cualquier falla en modo final.
- [x] Una pasada final limpia reporta cero pendientes.

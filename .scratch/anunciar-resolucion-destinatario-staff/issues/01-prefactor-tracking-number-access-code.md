# 01 — Prefactor: quitar `tracking_number`, `access_code` de 4 caracteres sin ambigüedad

**Qué construir:** El Paquete deja de tener `tracking_number` en el esquema y en todo el código (migración Alembic que elimina la columna y su `UniqueConstraint`, quitar el generador y toda referencia en dominio/web/plantillas). El generador de `access_code` produce 4 caracteres de un alfabeto reducido (dígitos `2-9`, letras mayúsculas sin `O`/`I`/`L`), nunca con la subcadena `"666"`.

**Bloqueado por:** Ninguno — puede empezar de inmediato.

**Estado:** ready-for-agent

- [ ] Nueva migración Alembic elimina la columna `tracking_number` y su `UniqueConstraint` de `paquetes`.
- [ ] `_generar_tracking_number` y toda referencia a `tracking_number` se eliminan de `paquete_service.py`, `paquete.py`, `announce.py`, `search.py`, `announce/confirmacion.html`, `search/form.html`.
- [ ] `_generar_access_code` produce exactamente 4 caracteres del alfabeto `23456789` + letras mayúsculas excluyendo `O`, `I`, `L`.
- [ ] `_generar_access_code` nunca devuelve un código que contenga `"666"` como subcadena (regenera si ocurre).
- [ ] `test_parity_esquema_orm` y `test_migration_graph` (ya existentes) siguen pasando sin cambios — confirman que el esquema y el ORM no divergieron.
- [ ] Suite completa (`pytest`) pasa.

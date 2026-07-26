# 02 — Filtros combinables + paginación en `/paquetes`

**Qué construir:** `GET /paquetes` acepta `estado`, `q` (código de acceso, guía, nombre parcial o teléfono), `torre`, `apartamento` y `pagina` — todos opcionales y combinables. 20 resultados por página, controles de paginación arriba y abajo de la lista.

**Bloqueado por:** 01 (comparte plantilla, aunque la lógica es independiente).

**Estado:** ready-for-agent

- [ ] Filtro por `estado` (exacto).
- [ ] Filtro por `q`: coincide si es igual a `access_code`, o a `guide_number`, o `recipient_name` contiene el texto (parcial, insensible a mayúsculas), o el texto normaliza como teléfono y coincide con `announced_by_phone`/`recipient_phone`.
- [ ] Filtro por `torre` y `apartamento` (parcial o exacto sobre `snapshot_torre`/`snapshot_apartamento`).
- [ ] Los filtros se combinan con AND cuando vienen varios a la vez.
- [ ] Paginación: 20 por página, parámetro `pagina`, controles (Anterior/números/Siguiente) arriba y abajo de la lista, conservando los filtros activos en los enlaces de paginación.
- [ ] `tests/web/test_packages.py` extendido: cada filtro por separado, combinación de filtros, paginación con más de 20 paquetes.
- [ ] Suite completa (`pytest`) pasa.

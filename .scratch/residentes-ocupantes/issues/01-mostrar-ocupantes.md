# 01 — Mostrar Ocupantes del apartamento en la ficha de residente

**Qué construir:** `/residentes/{id}` muestra, de solo lectura, los Ocupantes del apartamento actual de la Persona (nombre, teléfono si tiene, cuál es el principal).

**Bloqueado por:** Ninguno — la entidad Ocupante ya existe.

**Estado:** ready-for-agent

- [ ] Si la Persona tiene `apartamento_actual_id`, la ficha muestra la lista de Ocupantes de ese Apartamento (`listar_ocupantes`).
- [ ] Se indica visualmente cuál Ocupante es el principal.
- [ ] Si la Persona no tiene apartamento, no se muestra esta sección.
- [ ] `tests/web/test_customers_manage.py` extendido con ambos casos.
- [ ] Suite completa (`pytest`) pasa.

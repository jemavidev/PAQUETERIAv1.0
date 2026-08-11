# 07 — WhatsApp para residentes secundarios: `/mis-datos`

**What to build:** mismo alcance que el ticket 06 (input único autoclasificado para "agregar Ocupante", Asociar/Editar/Desvincular WhatsApp, ocultar "Confirmar" ya confirmado), aplicado al autoservicio del cliente principal en `/mis-datos`.

**Blocked by:** 01 (clasificador compartido), 06 (reusa las funciones de dominio de WhatsApp que introduce ese ticket).

**Status:** ready-for-agent

- [ ] El formulario "agregar Ocupante" de `/mis-datos` usa el input único autoclasificado.
- [ ] `/mis-datos` muestra botones "Asociar/Editar/Desvincular WhatsApp" por cada Ocupante gestionable (mismo guard de `_ocupante_gestionable_por` que ya existe).
- [ ] La acción "Confirmar" deja de mostrarse sobre un Ocupante que ya tiene `confirmado_en`.
- [ ] Tests en `test_customer_verify.py` cubriendo los mismos casos que el ticket 06, desde la perspectiva del cliente principal.

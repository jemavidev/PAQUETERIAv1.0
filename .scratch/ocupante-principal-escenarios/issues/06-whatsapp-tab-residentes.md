# 06 — WhatsApp para residentes secundarios: tab Residentes

**What to build:** en tab "Residentes" de `/residentes/{id}`, "agregar Ocupante" pasa de un campo "Teléfono" a un input único "Teléfono o WhatsApp" autoclasificado; se agregan las acciones "Asociar/Editar/Desvincular WhatsApp" (mismo patrón que ya existen para Teléfono); se oculta la acción "Confirmar" cuando el Ocupante ya está confirmado.

**Blocked by:** 01 (clasificador compartido).

**Status:** ready-for-agent

- [ ] `ocupante_service` gana `asociar_whatsapp_a_ocupante`/`editar_whatsapp_ocupante`/`desvincular_whatsapp_ocupante`, mismo contrato y restricciones que sus contrapartes de Teléfono (el principal no se edita/desvincula por acá).
- [ ] El formulario "agregar Ocupante" de tab Residentes usa el input único autoclasificado del ticket 01 en vez del campo "Teléfono" actual — puede crear un Ocupante identificado por Teléfono o por WhatsApp.
- [ ] Tab Residentes muestra botones "Asociar/Editar/Desvincular WhatsApp" por cada Ocupante, junto a los que ya existen de Teléfono.
- [ ] La acción "Confirmar" deja de mostrarse (en vez de mostrarse y fallar) sobre un Ocupante que ya tiene `confirmado_en`.
- [ ] Tests en `test_customers_manage.py` cubriendo: agregar con WhatsApp, asociar/editar/desvincular WhatsApp, "Confirmar" ausente en un Ocupante ya confirmado.

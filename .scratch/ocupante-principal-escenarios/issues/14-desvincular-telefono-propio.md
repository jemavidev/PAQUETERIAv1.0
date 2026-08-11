# 14 — Desvincular el propio Teléfono (tab Datos)

**What to build:** nueva acción en tab "Datos": la Persona logueada puede quitarse su propio Teléfono, solo si ya tiene WhatsApp asociado. Exige una confirmación explícita advirtiendo que se pierde el acceso a `/mis-datos` (el login sigue siendo estrictamente por Teléfono), y cierra la sesión de ese dispositivo de inmediato al confirmar.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Nueva función en `persona_service.py` (junto a `cambiar_telefono_propio`): quita `telefono`, exige `whatsapp_usuario` ya presente (rechaza con mensaje claro si no).
- [ ] La UI de tab Datos exige confirmación explícita (ej. checkbox u paso adicional) que menciona la pérdida de acceso, antes de ejecutar.
- [ ] Al confirmar con éxito, la sesión de ese dispositivo se cierra de inmediato (mismo criterio que `cambiar_telefono_propio` al cambiar a un número nuevo).
- [ ] Tests en `test_customer_verify.py`: éxito con advertencia + cierre de sesión, rechazo sin WhatsApp de respaldo.

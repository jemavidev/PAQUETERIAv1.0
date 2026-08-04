# 01 — Auto-declarar apartamento en `/mis-datos` también crea el Ocupante principal

**What to build:** cuando el cliente declara Torre/Apartamento por primera vez desde `/mis-datos`, además de seguir actualizando `Persona.apartamento_actual_id` (como hace hoy), el sistema debe crear/asegurar su propio `Ocupante` marcado como principal para ese Apartamento — reusando `ocupante_service.agregar_ocupante`, que ya exige teléfono para el primer Ocupante de un Apartamento y lo marca `es_principal` automáticamente. Esto alimenta el mismo roster que hoy solo alimentaba el flujo de staff (`/announce`), y es la base de todos los tickets siguientes de este spec.

**Blocked by:** Ninguno — puede empezar de inmediato.

**Status:** done

- [x] Al declarar Torre/Apartamento por primera vez desde `/mis-datos`, se crea un `Ocupante` con `es_principal=True` para esa Persona en ese Apartamento.
- [x] Reenviar el mismo formulario sin cambiar Torre/Apartamento no crea un segundo `Ocupante` duplicado (idempotente).
- [x] `Persona.apartamento_actual_id` sigue actualizándose igual que hoy — sin regresión del comportamiento actual.
- [x] Tests cubren: primera declaración crea el Ocupante principal; reenvío sin cambios no duplica.

## Implementación

- `ocupante_service.ocupante_de_persona(session, apartamento, persona_id)` (nuevo) — guardia de idempotencia.
- `customer_verify.py`: tras `declare_unit`, si `ocupante_de_persona(...) is None`, llama `agregar_ocupante`.
- Tests nuevos en `tests/web/test_customer_verify.py`: `test_declarar_apartamento_por_primera_vez_crea_ocupante_principal`, `test_reenviar_el_mismo_apartamento_no_duplica_el_ocupante`.
- Suite completa: 456 passed (454 + 2 nuevos).

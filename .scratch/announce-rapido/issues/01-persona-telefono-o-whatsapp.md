# 01 — Persona acepta Teléfono o WhatsApp como identidad

**What to build:** hoy `Persona.telefono` es obligatorio sin excepción (ADR-0003, "la llave universal"). Esta ficha lo relaja: `telefono` pasa a nullable, con una constraint nueva que exige que Teléfono o `whatsapp_usuario` estén presentes (nunca los dos vacíos a la vez) y un índice único parcial sobre `whatsapp_usuario` (mismo criterio de unicidad que ya tiene el Teléfono, mismo estilo que `uq_ocupantes_principal_por_apartamento`). Nueva función de dominio `get_or_create_persona_por_whatsapp`, simétrica a `get_or_create_persona` mismo pero resolviendo/creando por `whatsapp_usuario` (reutiliza la normalización que ya existe en `update_datos_personales` — recorta `@` inicial, valida formato).

Esta ficha también deja el rastro arquitectónico en orden: un ADR nuevo (`docs/adr/0007-*.md`) que documenta la relajación de ADR-0003 — dejando explícito que sigue exigiéndose Teléfono O WhatsApp (nunca "ninguno de los dos", que es la opción que ADR-0003 rechazaba, y que ADR-0006 había reafirmado) — y la actualización de `CONTEXT.md` (sección Persona, sección Teléfono, e invariante 1 "El Teléfono es la llave universal... nunca falta") para reflejar que la identidad real ahora es "Teléfono o WhatsApp". La línea de Ocupante/Principal en `CONTEXT.md` ("Teléfono obligatorio") queda para el ticket 02 — recién ahí el código deja de exigir Teléfono específicamente, así que actualizarla acá describiría un comportamiento que el código todavía no tiene.

Sin superficie de UI todavía — se verifica enteramente por dominio/migración.

**Blocked by:** Ninguno — puede empezar de inmediato.

**Status:** done

- [x] `personas.telefono` es nullable; migración `upgrade head` → `downgrade base` limpia sobre Postgres vacío.
- [x] Constraint de base de datos: insertar una Persona con `telefono=NULL` y `whatsapp_usuario` presente funciona; insertar con ambos `NULL` falla.
- [x] Índice único parcial sobre `whatsapp_usuario` (`WHERE whatsapp_usuario IS NOT NULL`): dos Personas no pueden compartir el mismo valor.
- [x] `get_or_create_persona_por_whatsapp` crea una Persona nueva solo-WhatsApp la primera vez, y reutiliza la misma Persona en llamadas repetidas con el mismo usuario (con o sin `@` inicial).
- [x] `docs/adr/0007-*.md` escrito, referenciando y actualizando ADR-0003 (y ADR-0006, que había reafirmado esa misma exigencia).
- [x] `CONTEXT.md` actualizado: Persona, Teléfono (+ WhatsApp como identidad alterna), invariante 1.

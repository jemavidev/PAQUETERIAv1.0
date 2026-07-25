# 03 — Eliminar cliente (web, solo ADMIN)

**Spec:** `.scratch/customers-manage/spec.md` · **ADR:** 0005 (eliminar = anonimización)

**What to build:** Un **ADMIN** elimina (anonimiza) un cliente desde su ficha, con **confirmación explícita** antes de enviar — reutilizando `anonimizar_persona` **sin cambios**. Un operador no-admin es rechazado.

**Blocked by:** 01 — Anonimizar Persona (dominio); 02 — Buscar + ver/editar cliente (la ficha donde vive el botón "Eliminar").

**Status:** ready-for-agent

- [ ] En la ficha (`GET /customers/manage/{persona_id}`), botón **"Eliminar"** visible solo si el `staff` actual es ADMIN, con **paso de confirmación explícita** en la UI (mismo espíritu que el aviso de irreversibilidad de Cancelar en `/packages`) antes de enviar.
- [ ] `POST /customers/manage/{persona_id}/delete` **gated por `require_admin`**: llama `anonimizar_persona(db, persona)`; éxito → redirige a `/customers/manage` con confirmación. Operador (no admin) → **403** (la ruta se protege server-side; la UI no es la única barrera).
- [ ] `persona_id` inexistente → 404.
- [ ] Tests HTTP: ADMIN elimina → Persona queda anonimizada (verificado en `client.db`: nombre/email/documento/teléfono cambiados, `eliminado_en` seteado); OPERADOR intentando eliminar → 403, Persona **sin cambios**; sin sesión → redirige; id inexistente → 404.

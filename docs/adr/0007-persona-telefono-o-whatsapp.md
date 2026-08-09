---
status: accepted
---

# Persona: Teléfono o usuario de WhatsApp, nunca ninguno de los dos

[ADR-0003](0003-telefono-llave-universal.md) ancla la identidad de una Persona en su Teléfono, sin excepción — y [ADR-0006](0006-ocupante-residentes-sin-persona-propia.md) reafirma esa decisión explícitamente al rechazar "volver nullable el Teléfono de Persona" por reintroducir "personas sin llave" en *todo* el sistema (auth, notificaciones, unicidad). Esta ADR reabre esa decisión de forma **acotada**, a pedido del cliente (`.scratch/announce-rapido`, sesión de `/grilling`): el conjunto tiene residentes que se identifican por su usuario de WhatsApp antes que por su número de celular, y el staff necesita poder anunciarles/registrarles un paquete sin forzarlos a dar un Teléfono que no quieren compartir.

Se decide que **Persona.telefono pasa a nullable**, pero con una constraint nueva que exige que **Teléfono o `whatsapp_usuario` estén presentes, nunca los dos vacíos a la vez**. `whatsapp_usuario` gana la misma garantía de unicidad que ya tenía el Teléfono. Esto **no** es la opción que ADR-0006 rechazó ("id opaco sin ninguna llave real") — sigue existiendo exactamente UNA llave de identidad por Persona en todo momento, solo que ahora puede ser cualquiera de dos campos en vez de uno solo.

## Considered Options

- **Mantener el Teléfono como única llave posible (statu quo de ADR-0003/0006).** Rechazada por el cliente: bloquea el caso real de un residente que se identifica solo por WhatsApp, forzando a inventar un Teléfono falso o a excluirlo del padrón.
- **Ruta paralela solo para Ocupante** (una columna `whatsapp_usuario` propia de `Ocupante`, sin tocar `Persona`). Considerada durante el `/grilling` y descartada por el cliente: dispersa la resolución de "quién anunció/quién recibe" en dos mecanismos distintos (Persona vía Teléfono, Ocupante vía WhatsApp) en vez de uno solo — cada lugar que hoy resuelve identidad vía `Persona` (login, `Paquete.announced_by_persona_id`, notificaciones futuras) tendría que aprender a mirar también esta ruta paralela.
- **Persona acepta Teléfono O WhatsApp (elegida).** Una Persona solo-WhatsApp es una Persona real, con su propia fila — todo lo que ya cuelga de `Persona` (FKs, `get_or_create_*`, unicidad) sigue funcionando sin duplicar mecanismos. El costo es que el Teléfono deja de ser una garantía incondicional en el esquema; se compensa con la constraint "uno de los dos, siempre".

## Consequences

- `Persona.telefono` es nullable; nueva constraint `ck_personas_telefono_o_whatsapp` (`telefono IS NOT NULL OR whatsapp_usuario IS NOT NULL`) y nuevo índice único parcial `uq_personas_whatsapp_usuario` (mismo criterio de unicidad que el Teléfono).
- El Teléfono sigue siendo la **única** llave que habilita login/OTP y el envío de notificaciones automáticas (SMS/email) — una Persona solo-WhatsApp no puede loguearse ni recibir avisos automáticos todavía. Esto es una limitación conocida y aceptada, no un defecto: depende de un canal de envío por WhatsApp que este rebuild no construye en esta rebanada.
- Un Ocupante (ADR-0006) puede ser Principal con una Persona solo-WhatsApp — el guard "sin Teléfono no puede ser Principal" pasa a "sin Teléfono NI WhatsApp no puede ser Principal".
- `Paquete.announced_by_phone` (ADR-0001, columna denormalizada del snapshot) pasa a nullable — queda `NULL` cuando el Anunciante no tiene Teléfono. `Paquete.announced_by_persona_id` **no cambia**: sigue `NOT NULL`, toda Persona real (con Teléfono o WhatsApp) sigue siendo referenciable por FK.
- ADR-0006 **no se reabre** en lo demás: Ocupante sigue siendo la entidad correcta para "residente sin identidad propia todavía" (nombre suelto, `persona_id IS NULL`) — esta ADR solo amplía qué puede ser una identidad propia (Persona), no toca ese caso distinto.

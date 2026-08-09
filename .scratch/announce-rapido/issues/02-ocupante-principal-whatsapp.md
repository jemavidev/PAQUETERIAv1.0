# 02 — Ocupante y Principal aceptan WhatsApp como contacto propio

**What to build:** `ocupante_service.promover_a_principal` y `confirmar_ocupante` hoy exigen específicamente que la Persona del Ocupante tenga Teléfono para poder ser Principal ("sin Teléfono no puede promoverse"). Pasan a exigir que tenga Teléfono **o** `whatsapp_usuario` — cualquier Persona real (ticket 01) basta. Mismo ajuste en `agregar_ocupante`: la exigencia de que el primer Ocupante de una unidad vacía tenga Teléfono pasa a "Teléfono o WhatsApp".

Login/OTP y notificaciones automáticas para un Principal solo-WhatsApp siguen sin funcionar (dependen de un canal de envío por WhatsApp que no existe todavía) — es una limitación conocida, no algo que esta ficha deba resolver.

Esta ficha además actualiza la línea de `CONTEXT.md` sobre Ocupante/Principal ("Teléfono obligatorio") que el ticket 01 dejó pendiente a propósito — recién acá ese comportamiento pasa a ser cierto en el código.

**Blocked by:** 01 (necesita que Persona pueda existir solo-WhatsApp).

**Status:** done

- [x] Un Ocupante cuya Persona tiene solo `whatsapp_usuario` (sin Teléfono) puede promoverse a Principal vía `promover_a_principal`.
- [x] `confirmar_ocupante` sobre el primer Ocupante de una unidad vacía, con una Persona solo-WhatsApp, lo promueve a Principal en la misma operación (igual que ya hace hoy para una Persona con Teléfono).
- [x] `agregar_ocupante` acepta el primer Ocupante de una unidad vacía con solo `whatsapp_usuario` (sin Teléfono) sin lanzar `ValueError`.
- [x] Un Ocupante sin Teléfono NI WhatsApp (ninguno de los dos) sigue rechazado por los tres guards, sin cambios en ese caso.
- [x] `CONTEXT.md` (sección Ocupante) actualizado: "Teléfono obligatorio" del Principal pasa a "Teléfono o WhatsApp".

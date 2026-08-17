# 104 — Ícono de WhatsApp: fallback por nombre cuando no hay teléfono en el snapshot

**Pedido original (cliente):**
"let me point to a example 'CAMILA OSPINA' in the /paquetes view, is not
letting me click on the whatsapp icon in this view" -- reportado como
ejemplo concreto tras la pregunta general de issue 103 sobre la prioridad
username > teléfono.

**Status:** implementado

## Diagnóstico

Confirmado contra la base de datos real: el paquete de "CAMILA OSPINA"
(código `ZWX8`) tiene `recipient_phone = None`. Su Persona SÍ existe y
SÍ tiene `whatsapp_usuario = "camila.ospina"`, pero NO tiene `telefono`
-- es una Persona solo-WhatsApp (ADR-0007). El fix de issue 103 resolvía
la Persona real del destinatario buscando por `recipient_phone` --
cuando ese campo está vacío (a propósito: `telefono_notificacion_ocupante`
nunca mete un username de WhatsApp ahí, esa columna la leen SMS/OTP como
Teléfono real), la búsqueda nunca la encontraba, y el ícono caía al
estado apagado en vez de usar su `whatsapp_usuario`.

## Implementación

- `packages.py`, nueva `_personas_por_nombre` (batch, mismo criterio que
  `_personas_por_telefono`): fallback SOLO para paquetes sin ningún
  teléfono en el snapshot -- busca la Persona por `recipient_name` exacto.
  Confiable en este dominio específico: `agregar_ocupante` (issue 97)
  fuerza que el nombre de cualquier Ocupante coincida con su Persona real
  cuando el contacto ya existe, y "Corregir destinatario" copia el
  nombre EXACTO del candidato elegido -- `recipient_name == Persona.
  nombre` es el caso normal acá, no la excepción. Riesgo documentado y
  aceptado: dos Personas con el mismo nombre completo registrado podrían
  resolver a la equivocada (caso borde, no la norma -- nombres completos,
  no apodos).
- `_listar`: el fallback por nombre solo se intenta cuando
  `recipient_phone` está vacío -- si hay teléfono pero no resuelve a
  ninguna Persona, se mantiene el comportamiento de siempre (cae al
  teléfono crudo, sin adivinar por nombre).

## Verificación

- `tests/web/test_packages.py`: nuevo test reproduce el escenario exacto
  (Persona solo-WhatsApp, `Destinatario.solo_nombre` con su nombre exacto,
  `recipient_phone` confirmado `None`) y verifica que el ícono resuelve
  su `whatsapp_usuario` -- 123 tests, todos pasan.
- Playwright contra el servidor local real, sobre el paquete REAL
  reportado (`ZWX8`, "CAMILA OSPINA"): el ícono de WhatsApp ahora es
  clickeable y apunta a `https://wa.me/camila.ospina`.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

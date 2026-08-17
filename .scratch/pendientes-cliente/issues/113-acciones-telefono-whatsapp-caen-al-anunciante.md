# 113 — Bug: íconos de Teléfono/WhatsApp apagados en Acciones sin fallback al anunciante

**Pedido original (cliente):**
"despues que apliques esta, dime porque este paquete '6Y5U' no le
aparece ningun boton de Accion activo, no entiendo, deberia poder tener
por lo menos el del telefono ya que cuenta con uno valido."

**Status:** implementado

## Diagnóstico (skill `diagnosing-bugs`)

Confirmado contra la BD real de dev: paquete 6Y5U (`REVERT TEST
ENTREGADX`) tiene `recipient_phone` vacío y ningún apartamento --
`Destinatario.solo_nombre` sin contacto propio (ADR-0007). Su Anunciante
(`persona_anunciante`) SÍ tiene teléfono (`+573005551212`), sin
`whatsapp_usuario`.

Causa raíz, dos lugares:
- `_acciones.html`, ícono Teléfono: `{% if p.recipient_phone %}` sin
  ningún fallback -- a diferencia del modal "Ver" (que sí cae al teléfono
  del Anunciante en su línea de contacto) y del ícono de Email de esta
  MISMA columna (que siempre usa `persona_anunciante.email`, nunca un
  campo del destinatario).
- `packages.py`, `_whatsapp_url_destinatario`: devolvía `None` cuando no
  había Persona resuelta NI `recipient_phone` -- nunca miraba al
  Anunciante.

Loop rojo/verde: test que reproduce exactamente el patrón de 6Y5U
(`Destinatario.solo_nombre` sin contacto + Anunciante con teléfono) --
falló primero (confirmando el bug), pasó después del fix.

## Implementación

- `packages.py`, `_whatsapp_url_destinatario`: nuevo último fallback --
  si no hay Persona resuelta NI `recipient_phone`, usa
  `url_whatsapp(persona_anunciante)` (mismo criterio que ya usa Email).
  `persona_anunciante` es un atributo transitorio (`_listar`, no una
  relación real), leído con `getattr(..., None)` por seguridad.
- `_acciones.html`, ícono Teléfono: nueva rama `elif
  p.persona_anunciante and p.persona_anunciante.telefono` -- título
  explícito "Teléfono del anunciante: ..." (mismo criterio que Email:
  puede no ser el teléfono del destinatario real).

## Verificación

- `tests/web/test_packages.py`: 2 tests nuevos (Teléfono y WhatsApp caen
  al Anunciante cuando no hay nada del destinatario) -- confirmados en
  rojo antes del fix, verde después.
- Playwright contra el servidor local real, sobre el paquete 6Y5U real de
  la BD de dev: WhatsApp y Teléfono pasan de apagados (gris) a activos
  (verde/azul), Email se queda apagado (correcto -- el Anunciante tampoco
  tiene email).
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

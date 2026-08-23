# 163 — `recipient_phone` siempre intenta caer al Principal de la unidad

**Pedido original:** aclaración del cliente mientras se investigaba issue 164: "eso ya había
quedado claro que cada paquete debería tener siempre un número de teléfono, del destinatario o en
su defecto si no tiene [contacto propio] usaría el del principal del apartamento, siempre debe
haber un número o usuario de WhatsApp responsable, siempre."

**Status:** verificado

## Diagnóstico

`Paquete.announced_by_persona_id` es una FK real (siempre a quien ANUNCIA), pero el
**destinatario** es puro snapshot de texto (ADR-0001) -- `recipient_phone` se resolvía de forma
INCONSISTENTE según el camino de `announce()`:

- Un solo camino (`DECLARADO_POR_CLIENTE` con match de co-residente) ya usaba
  `telefono_notificacion_ocupante` (propio, o si no el del Principal).
- Los otros 4 caminos (`YO_MISMO`, `PERSONA_REGISTRADA`, `OCUPANTE`, `DECLARADO_POR_CLIENTE`
  default) usaban el Teléfono crudo de la Persona/Anunciante SIN ningún fallback -- si esa Persona
  solo tenía WhatsApp, `recipient_phone` quedaba en `None` sin intentar el Principal.
- Peor aún: el camino `OCUPANTE` (staff eligiendo un residente de una unidad) caía explícitamente
  al Anunciante (quien LLAMÓ) en vez del Principal -- comportamiento documentado como deliberado en
  su momento (`.scratch/ocupante-principal-escenarios`, ticket 10), pero contrario a lo que el
  cliente confirmó que quiere ahora.

## Cambio

- `telefono_notificacion_ocupante` (`ocupante_service.py`) profundizado: antes solo caía al
  Principal si el Ocupante NO tenía Persona propia en absoluto; ahora también cae al Principal si
  la Persona propia del Ocupante SÍ existe pero solo tiene WhatsApp (sin Teléfono). Sigue
  estrictamente Teléfono (nunca WhatsApp) en el resultado -- mismo motivo de siempre
  (`recipient_phone` es una columna que SMS/OTP leen como Teléfono real).
- Nueva función `telefono_notificacion_de_persona` (misma lógica, partiendo de una Persona en vez
  de un Ocupante ya resuelto) -- usada por los caminos `YO_MISMO`/`PERSONA_REGISTRADA`/
  `DECLARADO_POR_CLIENTE` default.
- Camino `OCUPANTE`: usa `telefono_notificacion_ocupante` directo, con `or anunciante.telefono`
  como último recurso si ni el Ocupante ni su unidad tienen a nadie alcanzable por Teléfono
  todavía (unidad recién declarada, sin Principal).
- `SOLO_NOMBRE` queda sin cambios a propósito -- no hay Persona ni unidad detrás, nada de dónde
  sacar un Principal.

## Verificación

- 2 tests nuevos en `test_announce_paquete.py` que distinguen explícitamente el caso "cae al
  Anunciante por último recurso" del caso "cae al Principal confirmado" (para no confundirlos).
- 2 tests reescritos que asumían el comportamiento viejo (uno de ellos, en `test_announce_new.py`,
  llevaba el nombre `..._cae_a_quien_llamo_no_al_principal` -- renombrado a
  `..._cae_al_principal_no_a_quien_llamo`, revierte el criterio del ticket 10 citado arriba).
- Suite completa: 1048/1048 (antes de sumar [[164]]).

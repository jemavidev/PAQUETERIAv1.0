# 217 — `/mis-datos` tab Residentes: sugerir agregar el canal que falta (Teléfono/WhatsApp)

**Pedido original (cliente):** "En caso que en la vista /mis-datos y el Tab
de residentes sería bueno así como corregiste '⭐ Principal, ✕ WhatsApp, ✕
Teléfono, ...' en caso que no tenga teléfono/whatsapp sería bueno poder
sugerir de la misma forma agregar teléfono/whatsapp, solo en caso que no lo
tenga." (seguimiento de [[216-mis-datos-residentes-acciones-mas-claras]] y
[[213-ocupante-telefono-y-whatsapp-simultaneos]]).

**Status:** implementado

## Implementación

Resuelve de fondo el hallazgo de [[213-ocupante-telefono-y-whatsapp-simultaneos]]:

- `ocupante_service.py`: dos funciones nuevas,
  `agregar_telefono_a_persona_de_ocupante`/`agregar_whatsapp_a_persona_de_ocupante`
  -- agregan el canal que falta sobre la Persona YA vinculada al Ocupante
  (sin re-resolver `persona_id` como hacían `editar_telefono_ocupante`/
  `editar_whatsapp_ocupante`, que movían el Ocupante a una Persona
  DISTINTA). También se corrigieron `desvincular_telefono_ocupante`/
  `desvincular_whatsapp_ocupante`: con canal doble, ahora solo limpian su
  propio campo (antes desvinculaban el Ocupante por completo, perdiendo
  también el otro canal).
- `customer_verify.py`: los handlers `/telefono` y `/whatsapp` ganan una
  tercera rama (agregar canal faltante vs. editar canal existente vs.
  asociar el primer contacto).
- `verify.html`: chips "+ Teléfono"/"+ WhatsApp" (mismo estilo que
  ⭐/✕), visibles SOLO si ese canal falta -- despliegan un campo pequeño
  (`<details>`) para agregarlo.


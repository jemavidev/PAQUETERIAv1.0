# 213 — Ocupante: permitir teléfono Y WhatsApp simultáneos (cliente + staff)

**Pedido original (cliente):** "Por ahora solo veo que se asocia el
teléfono o el whatsapp, debería ser posible agregar ninguno, uno o ambos,
tanto para esta vista [`/mis-datos`] como para las vistas de staff, ya que
prácticamente es la misma funcionalidad. Recuerda que en la vista de
usuarios principales es que será posible realizar los cambios [el
staff/Principal] — los residentes simples no podrán modificar la
información de otros, solo la de ellos."

**Status:** implementado

Nota: el dominio (ADR-0007) ya permite que una Persona tenga Teléfono,
WhatsApp o ambos — falta confirmar si la restricción "uno u otro" descrita
es de la UI (`/mis-datos`, `/residentes`) o de la lógica de asociación.

## Investigación

Confirmado: es una restricción real de la lógica de dominio, no solo de la
plantilla (`ocupante_service.py`):

- `asociar_telefono_a_ocupante`/`asociar_whatsapp_a_ocupante` rechazan de
  entrada (`ValueError`) si `ocupante.persona_id is not None` -- o sea, en
  cuanto un Ocupante tiene CUALQUIER contacto propio (uno u otro), ninguna
  de las dos vuelve a poder usarse.
- `editar_telefono_ocupante`/`editar_whatsapp_ocupante` (las que sí corren
  una vez `persona_id` existe) resuelven `get_or_create_persona(...)` por
  el NUEVO valor y re-ligan `ocupante.persona_id` a esa Persona -- si el
  Ocupante ya tenía WhatsApp y se le agrega Teléfono, esto NO agrega el
  Teléfono a la Persona existente: crea/busca una Persona DISTINTA (por
  Teléfono) y mueve el `persona_id` del Ocupante hacia ella, dejando a la
  Persona de WhatsApp huérfana (sin Ocupante, con su historial de paquetes
  intacto pero desconectado de este Ocupante).
- La plantilla de `/mis-datos` solo agrava el síntoma (por eso se sentía
  como "uno u otro"): el campo de "Actualizar" de cada canal solo se
  renderiza si ESE canal ya tiene valor -- no hay ningún campo para
  agregar el canal que falta una vez que existe el otro.

Arreglarlo bien requiere una función de dominio nueva (agregar un canal a
la Persona YA vinculada al Ocupante, sin re-resolver `persona_id`) --
tocaría `ocupante_service.py`, las plantillas de `/mis-datos` (cliente) y
`/residentes/{id}` (staff, mismo patrón hoy). Alcance mayor que el resto de
este lote -- se deja pendiente para una pasada aparte, no se improvisa acá
por el riesgo de dejar Personas huérfanas o historial de paquetes
desconectado.

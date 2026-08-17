# 116 — "¿A nombre de quién es?" solo se ofrece con apartamento ya resuelto

**Pedido original (cliente):**
"Te pregunto para este modal al momento de recibir, si selecciono un
apartamento diferente este quedara para asignar el destinatario a este
nuevo apartamento que no tiene apartamento asociado o este destinatario
no deberia ver los residentes '¿A nombre de quién es? (confirmá o
corregí, opcional)' ya que es el solo y no tiene a nadie, no se esta
seccion aqui en caso que no tenga residente lo veo como si no
pertenece, a menos que ya este tenga un apartamento asignado. no se tu
que opinas" -- confirmado "si", con pedido adicional de seguir
compactando texto hacia placeholder cuando sea posible.

**Status:** implementado

## Diagnóstico

Confirmado en código antes de opinar: `candidatos_correccion` siempre
incluye al Anunciante como candidato mínimo, así que "¿A nombre de
quién es?" NUNCA aparecía vacía, ni siquiera para un paquete sin
apartamento -- de ahí la sensación de "pertenece a algo que no existe"
que describió el cliente. Peor: el `candidato_idx` viaja como ÍNDICE, y
`_resolver_desde_candidato` recalcula `candidatos_correccion` server-side
DESPUÉS de que el picker de Apartamento (issue 114/115, mismo form)
pudo haber declarado una unidad nueva -- un índice pensado para la
lista vieja podía terminar apuntando a otra persona de la unidad recién
declarada. Riesgo real de datos, no solo de UX.

## Implementación

- `_recibir_paquete.html`: la sección completa (`{% if candidatos %}`)
  gana `and not sin_apartamento` -- solo se ofrece si el paquete YA
  tenía un apartamento resuelto ANTES de abrir el modal. Elimina el
  riesgo de raíz: cuando no hay apartamento previo, el picker de
  Apartamento es la única forma de declarar unidad en ese envío, sin
  competir con esta sección.
- Texto compactado de paso (pedido explícito, mismo mensaje): "¿A
  nombre de quién es? (confirmá o corregí, opcional)" -> "¿A nombre de
  quién es? (opcional)" -- se revisó el resto del modal por más
  oportunidades de mover etiquetas a placeholder, pero `input_texto` ya
  lo hacía (sin `<label>` separado) y los grupos de chips (Tipo/
  Condición) no tienen equivalente de placeholder al ser botones, no
  inputs de texto -- no se tocaron.

## Verificación

- `tests/web/test_packages.py`: confirma ausencia de la sección sin
  apartamento y presencia cuando sí lo hay (dos tests, uno por caso).
- Playwright contra el servidor local real: paquete sin apartamento ya
  no muestra "¿A nombre de quién es?" -- el modal va directo de
  Apartamento a Guía.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

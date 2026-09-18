# 343 — `/paquetes`: quitar "Asignar apartamento" y "Fecha" de la fila; limitar íconos de Acciones en mobile

## Ronda 1

**Pedido original (cliente):**
"en la vista /paquetes remueve el icono 'Asignar apartamento' y 'fecha
hora', veo que estos datos los podremos consultar en el modal"

**Status:** implementado, pendiente confirmar visualmente

### Contexto

Tras issue 342 (Modificar + Asignar apartamento agregados al modal "Ver",
junto a Recibir/Entregar), el cliente pidió retirar esas mismas
afordancias de la FILA -- ya son redundantes ahí.

### Implementación

- `<th>Fecha</th>` y su `<td>` (+ la píldora equivalente en mobile,
  issue 341) se eliminan por completo -- columna retirada, no solo oculta.
  `Residente/Torre y Apartamento/Acciones`, 3 columnas (antes 4).
- `fecha_corta` deja de importarse en `packages/_resultados.html` (sigue
  existiendo en `packages/_acciones.html`, usado por otras plantillas).
- Columna/píldora "Torre y Apartamento": el botón activo "Asignar
  apartamento" (🏠, ANUNCIADO/RECIBIDO sin unidad) se retira -- ahora
  siempre muestra el mismo indicador apagado cuando no hay unidad,
  sin importar el estado. La acción sigue viva SOLO en el modal "Ver"
  (issue 342).

## Ronda 2 (mismo mensaje del cliente, pedido siguiente)

**Pedido:** "en la vista mobil los unicos iconos que deben aparecer en la
columna de Accion son 'Whatsapp, Telefono, Recibir/Entregar'"

**Status:** implementado, pendiente confirmar visualmente

### Implementación

`packages/_acciones.html`: Email, Modificar, Cancelar y Eliminar (activos
y apagados) llevan `hidden sm:inline-flex` -- mismo truco `replace` que ya
usa WhatsApp para su propio split mobile/desktop. Modificar sigue
alcanzable en mobile desde el modal "Ver" (issue 342); Email/Cancelar/
Eliminar quedan solo en desktop, sin equivalente en el modal -- alcance
explícito del pedido.

## Tests

- `test_encabezados_de_columna_nuevos`: tupla de encabezados sin "Fecha" +
  assert `>Fecha< not in r.text`.
- `test_fecha_columna_refleja_el_ultimo_cambio_de_estado`: eliminado --
  probaba la columna retirada.
- `test_icono_asignar_apartamento_en_anunciado_y_recibido_sin_unidad`:
  conteo de "🏠</button>" baja de 6 a 2 (ahora solo vive en el modal Ver).
- Suite completa `test_packages.py`: 229 passed.

## Verificación

Pendiente confirmación visual del cliente. Nota: tras esta implementación
el cliente reportó "los iconos de asignar apartamento aparecen
desactivados en todas las vistas, pero menos en el modal de la vista
Residentes" -- en investigación, ver conversación.

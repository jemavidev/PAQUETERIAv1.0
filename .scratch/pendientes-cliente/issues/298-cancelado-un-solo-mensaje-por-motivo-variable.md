# 298 — CANCELADO pasa a un solo mensaje; el motivo se resuelve vía `{motivo}`

**Pedido original (cliente):** "la idea es poder crear y gestionar los
motivos de cancelacion, solo eso, despues esta impisito que cada cliente al
momento que se le cancela un paquete, se selecciona un motivo de
cancelacion, dentro de la lista que ya hayamos creado previamente y es
invocado por {motivo} desde la plantilla, despues de esto dicho es claro
que solo se necesita un solo mensaje o plantilla de cancelacion y la
etiqueta {motivo} es quien controla lo que se establecio" — tras [[296]]
(unificación del CRUD dentro del modal por-motivo) y [[297]] (reducción a
un solo motivo genérico), el cliente señaló que el diseño de fondo (una
plantilla de notificación distinta POR CADA motivo) nunca hizo falta: el
catálogo de motivos es solo la lista de opciones para el picker de
`/paquetes`, y el mensaje de CANCELADO ya tenía la variable `{motivo}` para
resolver cuál se eligió -- exactamente como `{recipient_name}`/
`{access_code}`. Esto predataba incluso esta rebanada (venía de Grupo 8 /
`.scratch/plantillas-notificacion-multicanal`).

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

- CANCELADO pasa a tener un solo mensaje por canal (SMS/Email/WhatsApp),
  igual que ANUNCIADO/RECIBIDO/ENTREGADO -- ya no una plantilla por motivo.
- El catálogo de motivos (crear/editar/borrar) sigue existiendo intacto,
  pero su ÚNICO propósito ahora es alimentar el picker de "Cancelar
  paquete" en `/paquetes` -- sin relación con cuántas plantillas de
  notificación existen.
- En `/administracion/notificaciones`, `/administracion/notificaciones`
  vuelve a mostrar exactamente 4 filas (una por evento) -- el modal de
  CANCELADO incluye, además de sus 3 pestañas de canal, la lista "Motivos
  seleccionables" (crear/editar/borrar) embebida arriba.

## Implementación

- `notificacion_service.construir_mensaje`: deja de buscar la plantilla por
  `paquete.cancel_reason` para CANCELADO -- busca por `motivo=None`, igual
  que los demás eventos. `{motivo}` se sigue resolviendo desde
  `paquete.cancel_reason` (`_variables`, sin cambios ahí).
- `notificacion_service.mensaje_de_prueba`: `motivo` deja de seleccionar
  plantilla -- solo aporta el valor de ejemplo para `{motivo}` en la vista
  previa. El caller (`admin_notificaciones_probar`) le pasa una etiqueta
  real del catálogo cuando el evento es CANCELADO.
- `admin.py::_filas_plantillas`: simplificado a una lista fija de 4 filas
  (una por evento que notifica), sin el loop por motivo.
- `admin/notificaciones.html`: retirada la generación de una fila/modal por
  motivo. El modal de CANCELADO gana la sección "Motivos seleccionables"
  (lista + Editar/Borrar por fila + "+ Agregar"), con sus modales
  (`motivo-crear`, `motivo-editar-{id}`, `motivo-eliminar-{id}`)
  declarados como HERMANOS del modal de CANCELADO (nunca anidados: un
  `hidden` en el ancestro oculta todo su subárbol vía CSS, así que un
  modal anidado no se podría abrir con el padre cerrado).
- Migración `0041_cancelado_una_plantilla`: por cada canal, promueve UNA
  fila ya guardada (la de motivo "Otro" si existe, si no cualquiera) a
  `motivo = NULL` -- sin borrar las demás (evita violar la FK de
  `plantillas_notificacion_historial.plantilla_id`, que no tiene `ON
  DELETE CASCADE`); quedan huérfanas e intactas, mismo criterio ya
  aceptado para el catálogo. Aplicada y verificada contra el Postgres de
  desarrollo real, no solo el efímero de tests.
- Tests de `tests/web/test_admin_notificaciones.py` que verificaban el
  título compuesto "CANCELADO · <motivo>" reescritos para verificar la
  lista "Motivos seleccionables" dentro del modal (nuevo helper
  `_segmento_modal`, portado de `tests/web/test_packages.py`).

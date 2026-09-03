# 296 — CRUD de motivos de cancelación se unifica dentro del modal CANCELADO

**Pedido original (cliente):** "necesito que unifiques y permitas trabajar las
funcionalidades del acordeón relacionadas al estado CANCELADO que acabas de
crear, para que sea un solo modulo que trabaje de la mano" — tras terminar
`.scratch/motivos-cancelacion-catalogo` (tickets 01-04), la pantalla
`/administracion/notificaciones` tenía dos secciones desconectadas para lo
mismo: una arriba para renombrar/borrar el motivo (la etiqueta), otra abajo
(la fila `CANCELADO · <motivo>`) para editar sus 3 plantillas de canal.

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

- El modal grande de cada fila CANCELADO (el que ya tenía las 3 pestañas
  SMS/Email/WhatsApp) gana, arriba de esas pestañas, un formulario para
  renombrar el motivo + un botón "Borrar este motivo" (abre la misma
  confirmación ya existente) -- todo sobre ESE motivo vive en ESE modal.
- La sección separada "Motivos de cancelación" (lista con íconos
  editar/borrar) se elimina por completo de la pantalla.
- "+ Agregar motivo de cancelación" pasa a ser la última fila del listado
  compacto de CANCELADO -- crea el motivo y, si se guarda con éxito, abre
  directo su modal (ya listo para personalizar las 3 plantillas).
- El botón "Borrar este motivo" se omite (no aparece) cuando solo queda un
  motivo en el catálogo -- mismo criterio ya existente, movido de lugar.

## Implementación

- `_filas_plantillas` (`admin.py`) agrega `motivo_id` a cada fila CANCELADO
  -- identifica la fila del catálogo sin depender de comparar texto.
  `admin_motivos_crear`/`editar`/`eliminar` ganan `motivo_creado_id` /
  `motivo_editado_id` / `motivo_eliminar_error_id` para reabrir el modal
  grande correcto tras cada acción.
- `admin/notificaciones.html`: retirada la sección/card "Motivos de
  cancelación" y sus modales `motivo-editar-{id}` (uno por fila, ya no
  existen); el formulario de renombrar y el disparador de "Borrar" ahora
  viven dentro de `modal-notif-{fila_id}`, condicionados a
  `fila.motivo_id`. El modal `motivo-crear` y la confirmación
  `motivo-eliminar-{id}` se mantienen, solo cambian de ubicación/disparador.
- Tests de `tests/web/test_admin_notificaciones.py` (44, ya existentes del
  ticket 02) siguen verdes sin cambios -- verificaban comportamiento
  (status, texto, catálogo), no la estructura exacta de modales, así que
  la reubicación no los rompió.

Ver también [[297]] (reducción del catálogo a un solo motivo genérico,
pedido inmediatamente después de ver esta unificación).

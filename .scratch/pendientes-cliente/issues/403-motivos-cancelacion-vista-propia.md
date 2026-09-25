# 403 — Motivos de cancelación con vista propia (`/administracion/motivos-cancelacion`)

**Pedido original (Jesús):** "lo relacionado a 'Motivos seleccionables' ... en la vista de /administracion/notificaciones,
la idea es que estas opciones se comporten como se manejan los motivos de bloqueo y anulación
(/administracion/motivos-bloqueo y /administracion/motivos-anulacion-cobro), con su propia vista y que aplique a los
motivos de cancelación". Confirmado: "sí, continúa con todo".

**Status:** desplegado en test (`f65dfc7`), pendiente confirmar en vivo

## Decisiones (acordadas)

- Vista nueva `/administracion/motivos-cancelacion`, mismo diseño que motivos de bloqueo/anulación: formulario
  "Nuevo motivo de cancelación" arriba, lista con Eliminar + confirmación abajo, toasts de creado/eliminado.
- Se conserva "Editar" (hoy existe para cancelación, no en las otras dos).
- Se conserva la regla de mínimo 1 motivo: sin Eliminar cuando queda uno solo.
- Menú de cuenta (Datos): "Motivos de cancelación" junto a bloqueo y anulación.
- `/administracion/notificaciones`: se quita "Motivos seleccionables" del modal CANCELADO; `{motivo}` sigue igual.
- Cancelar en `/paquetes` no cambia; los motivos existentes se conservan.

## Verificación

- `tests/web/test_admin_motivos_cancelacion.py` (10, nuevas, vistas fallar antes de implementar): gate admin, lista,
  crear/editar/eliminar con sus toasts, duplicados/vacíos rechazados, modal Editar reabierto con error, sin Eliminar y
  400 con un solo motivo, enlace en el menú.
- `test_admin_notificaciones.py`: se quitaron las 9 pruebas del catálogo embebido (movidas a la vista nueva) y se
  agregó una que confirma que el modal CANCELADO ya no administra motivos, conserva `{motivo}` y las rutas viejas no
  existen. 49 en verde entre ambos archivos.
- Tailwind reconstruido, `?v=108`.

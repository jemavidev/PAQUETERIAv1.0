# 192 — "Agregar usuario" en /administracion/personal pasa a modal

**Pedido original (cliente):**
"como puedes hacer que el agregar un usuario en la vista
/administracion/personal sea por medio de un boton de agregar usuario que
abra un modal con el formulario que ya se esta manejando."

**Status:** implementado

## Implementación

- `admin/staff.html`: la sección "Dar de alta staff" (antes un
  `formulario_flujo` siempre visible al fondo de la página) se reemplaza
  por un botón "Agregar usuario" (junto al título, mismo patrón que los
  íconos "Editar"/"Resetear" ya usan) que abre el modal `agregar-usuario`
  (`components/_modales.html`, mismo componente que ya usan los modales de
  Editar/Resetear contraseña de esta misma pantalla) — mismos campos
  (Email, Nombre, Contraseña, Rol), sin cambios de ruta ni de dominio.
- `abierto=(email is defined)`: si la creación falla (email duplicado,
  contraseña débil, campos vacíos), el modal se reabre automáticamente con
  los campos marcados en rojo visibles, en vez de quedar cerrado con el
  error solo en el toast — `email` únicamente llega al contexto de la
  plantilla desde el `_error()` de esta ruta específica (POST
  `/administracion/personal`, sin id), así que es un discriminador limpio
  sin necesitar una bandera nueva.

## Verificación

- 3 tests nuevos en `tests/web/test_admin_staff.py`: el botón existe y el
  modal arranca cerrado; un error de alta lo reabre con los campos
  conservados; un alta exitosa lo deja cerrado.
- Suite `tests/web/test_admin_staff.py` completa: 19 tests, todos pasan
  (incluye los ya existentes de alta/edición/reset/activar-desactivar, sin
  tocarlos).
- Pendiente: deploy a test.papyrus.com.co.

# 193 — Quitar la palabra "staff" de los textos visibles

**Pedido original (cliente):**
"Puedes remover la palabra staff del aplicativo, por lo general podrias
remplasarla por algo como 'Personal' o simplemente removersla, por ejemplo
'Nueva cuenta de staff' --> 'Nuevo usuario'"

**Status:** implementado

## Alcance

Auditoría completa de "staff" en `src/app/web/templates/**/*.html` y
`src/app/domain/*.py`/`src/app/web/routes/*.py`: 9 apariciones eran texto
realmente visible para un usuario (título de modal, mensajes de error,
etiqueta de menú). El resto (identificadores internos como `tiene_staff`/
`staff_list`/`badge_estado_staff`, rutas como `/staff/olvide-password`,
comentarios/docstrings) se dejó intacto a propósito — cambiar eso es un
alcance distinto (renombrar rutas rompe bookmarks/enlaces existentes,
renombrar variables no cambia nada que el usuario vea) y el ejemplo del
pedido ("Nueva cuenta de staff" → "Nuevo usuario") es puntualmente sobre
copy, no sobre identificadores ni URLs.

## Cambios

- `admin/staff.html`: título del modal "Nueva cuenta de staff" → "Nuevo usuario".
- `auth/me.html`: encabezado "Sesión de staff" → "Mi sesión".
- `customer/verify.html`: "...si el staff te asigna..." → "...si el personal te asigna...".
- `base.html`: etiqueta del menú de cuenta "Staff" → "Personal".
- `staff_service.py` (4 mensajes de error, `PermissionError`): "cuentas de staff"/"contraseñas de staff"/"activar/desactivar staff" → "...de personal".
- `persona_service.py`: "pídele al staff que te lo agregue" → "pídele al personal que te lo agregue".

## Verificación

- `tests/data_model/test_staff_service.py`, `test_persona_service.py`,
  `tests/web/test_admin_staff.py`, `test_layout.py`, `test_customer_verify.py`
  — 161 tests, todos pasan (ninguno hardcodeaba el texto exacto de estos
  mensajes).
- Pendiente: deploy a test.papyrus.com.co.

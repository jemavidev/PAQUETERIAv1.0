# 198 — Autoservicio: editar nombre propio (sin poder tocar el rol)

**Pedido original (cliente):**
"tambien permite que se cambien datos de los usuarios 'Operadores' por
ellos mismos con formularios y demas, pero no permitas que se modifique el
rol por ellos mismos" -- seguimiento a issue 196 (autoservicio de
contraseña) y al pedido de mejorar el look de `/mi-sesion`.

**Status:** implementado

## Alcance

El único otro dato editable de `Usuario` (fuera de la contraseña, ya
cubierta en [[196]]) es `nombre` -- no hay teléfono/avatar/otros campos de
perfil en el dominio hoy. "Datos... y demás" se resolvió a eso.

## Implementación

- `staff_service._set_nombre(usuario, nombre)`: lógica de validación
  extraída de `editar_staff` (antes inline), compartida.
- `staff_service.editar_mi_perfil(session, usuario, nombre)`: función
  nueva, autoservicio -- SIN parámetro `rol` (ni existe la posibilidad de
  pasarlo, a diferencia de `editar_staff`) y sin chequeo de actor ADMIN
  (mismo split que `set_password`/`resetear_password`: acá no hace falta,
  self-edit de nombre es igual para cualquier rol). Esto hace que "no se
  puede cambiar el rol propio" sea una garantía a nivel de firma de
  función, no solo de que el form no traiga el campo.
- `POST /mi-sesion/editar` (`auth.py`): el actor sale de `current_staff`
  (la sesión), nunca de un campo del form.
- `auth/me.html`: nueva sección "Editar mi perfil" (solo Nombre,
  pre-llenado) usando `formulario_flujo`, junto a la de "Cambiar mi
  contraseña" ([[196]]).

## Verificación

- Domain: `editar_mi_perfil` cambia el nombre sin tocar el rol; su firma
  no acepta `rol` en absoluto (`inspect.signature`); nombre vacío rechaza.
- Web: OPERADOR edita su propio nombre y lo ve reflejado; el form NO trae
  ningún `name="rol"`; nombre vacío → 400; sin sesión → redirige a login.
- `test_staff_service.py` + `test_auth.py`: 42 tests, todos pasan.
- Verificado en vivo contra el servidor de dev local con un OPERADOR real.
- Pendiente: deploy a test.papyrus.com.co.

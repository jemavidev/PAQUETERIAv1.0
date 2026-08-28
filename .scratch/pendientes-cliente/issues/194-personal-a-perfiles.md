# 194 — "Personal" → "Perfiles" (la página, no el rol de dropdown)

**Pedido original (cliente):**
"En el header cambia la palabra 'Personal' --> 'Perfiles' o en su defecto
'Perfil'" / "Esto ya que en realidad no son Personal, son usuarios del
sistema"

**Status:** implementado

## Alcance

"Personal" aparecía en 4 lugares — 3 se renombraron a "Perfiles", uno se
dejó igual a propósito:

- `admin/staff.html` `<title>` y `<h1>` (la página que lista cuentas
  ADMIN/OPERADOR) — **renombrado a "Perfiles"**.
- `base.html`, enlace del menú de cuenta hacia `/administracion/personal`
  (`bloque_staff`) — **renombrado a "Perfiles"**, mismo texto que el H1 de
  la página a la que apunta.
- `base.html`, `account-menu-block-label` que agrupa "Mi sesión" +
  "Perfiles" + "Notificaciones" + "Conjunto" en el dropdown de cuenta
  cuando coexisten sesión de cliente y de staff — **se dejó como
  "Personal"**: ahí el sentido es "esto es lo que puedes hacer como
  personal/staff de la empresa" (rol de quien está logueado), no "lista de
  cuentas" — es un uso correcto y distinto del que motivó el pedido. Si
  también lo quieres cambiar, avisa.

No se tocó la ruta `/administracion/personal` (URL) -- mismo criterio que
issue 193, el pedido es sobre texto visible, no sobre URLs.

## Verificación

- `tests/web/test_layout.py` + `test_admin_staff.py`: 47 tests, todos
  pasan (ninguno hardcodeaba el texto "Personal", solo el atributo
  `href="/administracion/personal"`, que no cambió).
- Pendiente: deploy a test.papyrus.com.co.

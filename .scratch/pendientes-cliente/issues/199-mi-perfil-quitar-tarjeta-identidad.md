# 199 — Quitar la tarjeta de identidad de "Mi perfil"

**Pedido original (cliente):**
"En la vista de /mi-sesion, remieve esta seccion A ADMIN info@papyrus.com.co
ADMIN Cerrar sesión 'bg-white border border-gray-200 rounded-2xl shadow-lg
p-6' creo que no es necesario" — la tarjeta de avatar+nombre+email+rol+
Cerrar sesión agregada en issue 197.

**Status:** implementado

## Implementación

- `auth/me.html`: se quita por completo la tarjeta de identidad. Queda
  solo el `<h1>Mi perfil</h1>` + los dos formularios de autoservicio
  ("Editar mi perfil", "Cambiar mi contraseña").
- "Cerrar sesión" **no desaparece de la app** -- sigue disponible siempre
  desde el dropdown de cuenta del header (`formulario_salir()`,
  `base.html`), que ya tenía su propia instancia independiente de este
  botón. Solo se quitó la copia redundante que vivía en esta página.
- Import de `_botones.html` (`boton`) removido del template -- quedó sin
  uso tras quitar el botón de logout de esta página (los otros 2
  formularios usan `formulario_flujo`, que trae su propio botón).

## Verificación

- `test_login_valido_abre_sesion_y_me_muestra_al_staff` (`test_auth.py`)
  confirmaba identidad vía el email visible en la página -- ya no aparece
  ahí, así que se actualizó para confirmar vía el nombre precargado en
  "Editar mi perfil" (`value="ADMIN"`) en su lugar. Ningún otro test
  dependía del contenido de esa tarjeta.
- `test_auth.py` + `test_layout.py` + `test_password_reset.py` +
  `test_customer_auth.py` + `test_rate_limit.py` + `test_staff_service.py`:
  97 tests, todos pasan.
- Verificado en vivo contra el servidor de dev local: la tarjeta ya no
  aparece; "Cerrar sesión" sigue disponible 2 veces en la página (dropdown
  de escritorio + móvil del header), ninguna en el cuerpo de "Mi perfil".
- Pendiente: deploy a test.papyrus.com.co.

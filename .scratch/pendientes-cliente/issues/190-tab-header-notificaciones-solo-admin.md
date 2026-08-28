# 190 — Tab de "Notificaciones" en el header, visible solo para ADMIN

**Pedido original (cliente):**
"como puedo ver que se creo en esta vista? que posibilidad existe en que
agregues un tab al header donde solo se muestre para el rol de admin"

(Sobre `/administracion/notificaciones` — las plantillas multicanal
SMS/Email/WhatsApp recién construidas, `.scratch/plantillas-notificacion-
multicanal`, tickets 01-04.)

**Status:** implementado

## Hallazgo antes de implementar

La pantalla YA es alcanzable hoy — `base.html`, `bloque_staff(es_admin)` —
pero solo dentro del menú desplegable de cuenta (ícono de avatar arriba a
la derecha → bloque "Staff" → "Notificaciones"), no como un tab visible en
la barra de navegación principal (`.site-nav`). El pedido es promoverlo a
esa barra visible, sin quitarlo del menú de cuenta.

## Implementación planeada

`base.html`, línea ~330-337 — el bloque `.site-nav` de staff ya calcula
`es_admin` ahí mismo (lo usa después para el menú de cuenta) pero no lo usa
en este `<nav>`. Se agrega un `{% if es_admin %}` con
`enlace_nav('/administracion/notificaciones', 'Notificaciones', iconos_nav.notificaciones)`
dentro de ese bloque, mismo patrón que los demás enlaces ahí (`Paquetes`,
`Residentes`, `Consultar`).

## Verificación

- `tests/web/test_layout.py`: 2 tests nuevos — ADMIN ve el tab dentro de
  `.site-nav`, OPERADOR no. Los 2 tests existentes de esta misma sección
  (`test_staff_operador_ve_su_conjunto_de_enlaces_sin_administracion`,
  `test_staff_admin_ve_ademas_los_enlaces_de_administracion`) siguen
  pasando sin tocarlos.
- Suite `tests/web` completa: 661 tests, todos pasan.
- Verificado en vivo contra el servidor de dev local: el tab aparece en el
  header para el admin logueado, con el email actualizado (ver issue 191).
- Pendiente: deploy a test.papyrus.com.co.

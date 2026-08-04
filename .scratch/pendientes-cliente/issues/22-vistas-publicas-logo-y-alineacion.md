# 22 — Logo + alineación en el resto de vistas públicas sin sesión

**Pedido original (cliente):** "aplica esto también a
https://test.papyrus.com.co/ingresar y todas las vistas en la zona para
usuarios sin autenticar y que manejen un formulario como has notado, analiza
y dime cuales aplican" + "incluyendo esta vista también
https://test.papyrus.com.co/anunciar [confirmación] que no tiene formulario,
pero también aplica" + confirmaciones puntuales de `/otp/solicitar` (misma
plantilla que `/otp`), `/otp/verificar` y `/staff/olvide-password` (ya
cubiertas por el ticket 21 y por este mismo ticket).

**Vistas:** análisis completo de rutas públicas (sin `current_staff`/
`current_customer`/`require_admin`) hecho por `grep` sobre todos los
`routes/*.py`. Resultado:

| Ruta | Plantilla | Aplica | Motivo |
|---|---|---|---|
| `/anunciar` | `announce/form.html` | ya correcto | Referencia original |
| `/consultar` | `search/form.html` | ya correcto | Referencia original (ancho distinto a propósito, muestra timeline/fotos) |
| `/anunciar` (POST, confirmación) | `announce/confirmacion.html` | **sí** | Resultado directo del formulario de /anunciar, aunque no tiene form propio |
| `/entrar` | `auth/entrar.html` | ya correcto | Tickets 13-20 |
| `/ingresar` | `auth/login.html` | **sí** | Login de staff |
| `/otp`, `/otp/solicitar` (error) | `auth/customer_login.html` | **sí** | Pedir OTP de cliente -- misma plantilla en ambas rutas |
| `/otp/verificar` | `auth/customer_verify.html` | **sí** | Confirmar OTP |
| `/staff/olvide-password` | `auth/olvide_password.html` | **sí** | Ticket 21 |
| `/staff/olvide-password` (confirmación) | `auth/olvide_password_enviado.html` | **sí** | Ticket 21 |
| `/staff/restablecer-password` | `auth/restablecer_password.html` | **sí** | Ticket 21 |
| `/ayuda`, `/terms` | `ayuda/form.html`, `terms/form.html` | **no** | Páginas estáticas de contenido (FAQ/T&C), no forman parte de este flujo de acción -- criterio del cliente fue "vistas... que manejen un formulario" |
| `/mi-sesion`, `/otp/perfil`, `/mis-datos`, `/mis-paquetes`, `/paquetes`, `/residentes*`, `/administracion/*`, `/announce` (alterno) | varias | **no** | Todas exigen sesión (`current_staff`/`current_customer`/`require_admin`) -- fuera del alcance "zona sin autenticar" |

**Status:** verificado

## Qué se hizo

Mismo patrón que tickets 17/20/21 en cada plantilla aplicable: logo de
Papyrus (`<img src="/static/branding/papyrus-logo.png">`, `max-w-xs`,
`max-height:120px;min-height:80px`) arriba del contenido + wrapper externo
`max-w-md mx-auto px-4 py-8` (antes `py-12`, o `px-4 py-10` sin `max-w-md`
en el caso de `announce/confirmacion.html`). Ningún cambio de clases nuevas
para Tailwind (todas ya estaban compiladas) -- sin recompilar.

## Verificación

- [x] Suite de tests relevante sin regresiones (86 passed:
      test_customer_auth, test_customer_verify, test_layout,
      test_password_reset, test_auth, test_announce, test_announce_new).
- [x] Capturas confirman logo + alineación en las 6 vistas nuevas --
      posiciones de logo medidas con Playwright, coinciden exacto
      (`top:93 left:35`) entre `/ingresar`, `/otp` y `/anunciar`.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo, incluyendo
      un anuncio real de punta a punta para ver la confirmación con logo.

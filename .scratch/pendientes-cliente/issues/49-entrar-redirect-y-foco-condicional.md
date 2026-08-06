# 49 — `/entrar`: redirigir si ya hay sesión; foco condicional en TODO el app

**Pedido original (cliente):** "Para esta vista de /entrar, se ve esteticamente
bien, pero seria bueno que la misma vista analice a ver si el usuario esta
logueado (otp/staff), en caso positivo seria bueno que sea redirigido al area
de usuarios logueados por default (otp=mis datos / staff=mis paquetes).
Adicional a esto seria bueno controlar el focus en caso que exista un error
en CUALQUIER vista del app, el focus hoy trabaja para iniciar en el primer
campo de input de una vista, pero si se presenta un error en cualquier campo
seria bueno que el focus no se active en ningun campo del formulario, esto no
activaria el teclado automatico que aparece en un dispositivo movil y de esta
manera se podra visualizar el mensaje de error que aparece en la parte
inferior de la vista desde el mobile."

**Status:** verificado

## Contexto

Primer pedido de la ronda de "versión móvil" (el cliente pidió recorrer,
vista por vista, todas las pantallas que ve un cliente -- público y
autenticado con OTP -- empezando por `/entrar`).

## Implementación

**1. Redirect si ya hay sesión (`entrar.py`):**
`GET /entrar` ahora chequea sesión ANTES de renderizar el selector
Cliente/Staff -- mismo chequeo LIVIANO (presencia en `request.session`, sin
verificar contra la BD) y mismo destino que ya usaba `destino_marca` en
`base.html` para el link de marca del header: staff → `/paquetes`, cliente →
`/mis-datos`. Si coexisten ambas sesiones, staff gana (mismo criterio de
prioridad que `destino_marca`).

**2. Foco condicional (autofocus solo sin error) -- aplicado a TODO el app,
no solo `/entrar`, porque el cliente lo pidió explícitamente para "CUALQUIER
vista":**

Encontrados 13 lugares con `autofocus` incondicional (11 vía el macro
`input_texto`/`input_select`, más 2 casos con `autofocus` crudo fuera del
macro: las casillas de dígito de `/otp/verificar`, y el `<textarea>` dentro
del loop de `/administracion/notificaciones`). Cambiados todos a
`autofocus=(not error)` (o su equivalente `{% if not error %}` para los 2
casos fuera del macro) -- `error` es la variable general que TODAS las rutas
de este proyecto ya seteaban de forma consistente en cada re-render con
fallo (confirmado repasando cada ruta antes de tocar su plantilla), así que
es la señal correcta incluso cuando el error no es específico de un campo
(ej. rate-limit, "credenciales incorrectas" sin decir cuál).

Se dejaron SIN tocar 3 cuadros de búsqueda (`/consultar`, y 2 buscadores de
staff en `/paquetes` y `/residentes`) porque son formularios GET sin ningún
estado de error posible -- gatear ahí no tendría efecto real.

Archivos tocados: `entrar.py` (ruta), y 13 templates
(`admin/conjunto.html`, `admin/staff.html`, `admin/notificaciones.html`,
`announce/form.html`, `announce_new/form.html`, `auth/customer_login.html`,
`auth/entrar.html`, `auth/login.html`, `auth/olvide_password.html`,
`auth/restablecer_password.html`, `auth/customer_verify.html`,
`customers_manage/detail.html`, `customer/verify.html`).

Sin cambios de CSS/layout en ningún archivo -- ambos fixes son puramente de
comportamiento (routing + atributo HTML condicional), así que no hay ningún
riesgo para la vista desktop (instrucción explícita del cliente para toda
esta ronda).

## Verificación

620 tests pasan (607 + 13 nuevos: 3 para el redirect de `/entrar`
-- cliente, staff, y prioridad cuando coexisten ambas sesiones -- y 10 para
el foco condicional, cubriendo `/otp`, `/otp/verificar`, `/anunciar`,
`/mis-datos` e `/ingresar` como muestra representativa de ambas audiencias
y de los 3 patrones de campo distintos -- input_texto, casillas de dígito
crudas, y el textarea en loop).

Confirmado en vivo por el cliente en `test.papyrus.com.co` (2026-08-05):
"/otp" y "/otp/verificar" ok, "no veo nada raro".

# 284 — Desactivar `autofocus` en vistas exclusivas de staff

**Pedido original (cliente):** "para la opcion de staff veo que los
autofocus que habiamos configurado son algo molestos, posibilidades de
desactivarlos en caso de ser staff o estar autenticado"

Se preguntó alcance (`AskUserQuestion`): solo los buscadores, o todos
los `autofocus` de vistas de staff. Respuesta: **todos**.

**Status:** implementado

## Alcance

Se auditaron TODOS los usos de `autofocus` en el repo (`grep -rn
autofocus CODE/src/app/web/templates/`) y se clasificó cada template
por si su ruta exige sesión de staff (`Depends(current_staff)` /
`require_admin`) o no:

**Staff-only -- `autofocus` retirado (7 archivos, 9 usos):**
- `packages/list.html` (buscador de `/paquetes`)
- `customers_manage/search.html` (buscador de `/residentes`)
- `customers_manage/detail.html` (campo Nombre, editar residente)
- `admin/staff.html` (campo Email, nuevo usuario staff)
- `admin/conjunto.html` (campo Nombre del Conjunto)
- `admin/notificaciones.html` (3 usos: Asunto, Mensaje/textarea, Enviar
  prueba)
- `announce_new/form.html` (campo Teléfono/WhatsApp -- gated por
  `current_staff`, confirmado en el docstring de `announce_new.py`)

Como estas rutas SOLO se pueden alcanzar autenticado como staff, no
hace falta una condición dinámica (`if staff...`) -- directamente se
retira el argumento `autofocus=...` (el default del macro ya es
`False`).

**NO tocado (confirmado que NO son staff-only, a pesar del nombre o de
estar cerca de vistas de staff):**
- `announce/form.html` -- **`/anunciar` es vista PÚBLICA**, sin
  privilegios (docstring explícito de `announce.py`: "vista pública,
  sin privilegios") -- el cliente la usa para anunciar su propio
  paquete, nada que ver con `announce_new` (que sí es de staff).
- `search/form.html` -- `/buscar` tampoco exige `current_staff`
  (comentario explícito en `search.py`: "esta vista sigue sin
  Depends(current_staff)") -- es la búsqueda pública de paquetes,
  aunque staff también la usa para las acciones Entregar/Recibir.
- `auth/login.html`, `auth/olvide_password.html`,
  `auth/restablecer_password.html` -- login/reset de staff, pero se
  visitan UNA vez por sesión, no en el flujo repetido del día a día
  que motivó la queja -- ahí el autofocus sigue ayudando.
- Todo lo de `/mis-datos`, `/otp`, `/entrar` (customer, no staff).

## Verificación

Un test dependía del `autofocus` retirado
(`test_anunciar_deja_el_formulario_listo_para_el_siguiente`, esperaba
que SÍ estuviera presente) -- actualizado a lo contrario, con comentario
explicando el cambio de comportamiento. Otro test relacionado
(`test_recibir_sin_autofocus_en_el_campo_principal`) seguía pasando tal
cual (su aserción ya era "sin autofocus"), se actualizó igual su
comentario para no atribuirlo solo al modal abierto.

Suite completa de los 6 archivos de test afectados
(`test_admin_conjunto`, `test_admin_notificaciones`, `test_admin_staff`,
`test_announce_new`, `test_customers_manage`, `test_packages`): 478
passed, sin regresiones.

Verificado en vivo (dev local, `document.activeElement`): en `/paquetes`
y `/residentes`, al cargar la página el foco queda en `<body>`, no en el
buscador -- confirmado también que no queda ningún
`input[autofocus]` en el DOM de ninguna de las dos.

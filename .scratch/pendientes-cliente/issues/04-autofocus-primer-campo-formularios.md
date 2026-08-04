# 04 — Autofocus en el primer campo de cada formulario al cargar la vista

**Pedido original (cliente):** "para las diferentes vista que tengo, existen
algunas con formularios, quiero que las vistas que incluyan formularios al
carcar cada una de esas vistas, el focus se situe en el primer campo de
input del formulario."

**Vistas:** todas las que tienen un formulario real al cargar la página (no
dentro de un modal). Ver lista abajo.

**Status:** verificado

## Decisiones (resueltas por Claude, "procede como más recomiendes")

1. **`auth/entrar.html`** (pestañas Cliente/Staff, ambos `<form>` presentes
   en el DOM, ocultos por CSS): autofocus solo en el primer campo de la
   pestaña visible por defecto (Cliente). Cambiar de pestaña sin recargar no
   reasigna el foco — eso requeriría JS y es un pedido distinto ("foco al
   cambiar de pestaña"), no lo que se pidió ("al cargar la vista").
2. **Modales de Recibir/Entregar/Cancelar** (`packages/list.html` /
   `components/_modales.html`): FUERA de alcance de este ticket — se abren
   con clic, no al cargar la página, así que "al cargar cada una de esas
   vistas" no aplica ahí tal cual. Mecanismo distinto (foco al abrir el
   modal) si se quiere más adelante.

## Qué hacer

- `input_texto()` (`components/_inputs.html`) gana un parámetro opcional
  `autofocus=False` (mismo patrón que `destacado`/`icono` en tickets
  anteriores) — renderiza el atributo HTML nativo `autofocus` en el
  `<input>`, sin JS.
- Pasar `autofocus=True` en el primer campo real de:
  - `auth/login.html`
  - `auth/customer_login.html`
  - `auth/entrar.html` (solo tab Cliente, por defecto visible)
  - `announce/form.html`
  - `announce_new/form.html`
  - `admin/staff.html`
  - `admin/notificaciones.html`
  - `customers_manage/detail.html`
  - `customer/verify.html`
- Precedente ya existente en el código: `auth/customer_verify.html` (input
  del código OTP) ya tiene `autofocus` puesto a mano — no se toca, ya
  funciona.

### Reapertura — inventario incompleto

El inventario original solo trazó callers de `input_texto`/`formulario_flujo`.
Se pasó por alto un componente compartido DISTINTO con su propio `<form>`:
`busqueda_filtros()` (`components/_busqueda_filtros.html`), con su propio
campo de texto (`q`). Tres vistas usan este componente y también necesitan
autofocus:

- `search/form.html` → `/consultar` (público) — la que el cliente reportó.
- `packages/list.html` → `/paquetes` (staff)
- `customers_manage/search.html` → `/residentes` (staff)

`busqueda_filtros()` gana el mismo parámetro opcional `autofocus=False`,
aplicado al campo `q` (el primer campo real de la barra en los 3 casos —
Estado es un grupo de radios/chips, no un campo de texto de entrada).

## Verificación

- [x] Render local (`client.get`) confirma exactamente 1 `autofocus` por
      página en `/ingresar`, `/entrar`, `/anunciar` — sin duplicados.
- [x] 229/229 `tests/web/` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `f5e2e50`) y confirmado en
      vivo vía `curl` en las 3 vistas públicas: `/ingresar` → campo Email,
      `/entrar` → campo Teléfono (tab Cliente), `/anunciar` → campo Nombre.
      Las 6 vistas restantes (staff/admin/cliente autenticado) llevan el
      mismo parámetro `autofocus=True` verificado en tests, no re-probadas
      en vivo una por una porque requieren sesión.
- [x] Reapertura: `/consultar`, `/paquetes`, `/residentes` (componente
      `busqueda_filtros()`) desplegados (commit `35cfba6`) y `/consultar`
      confirmado en vivo — exactamente 1 `autofocus`, en `name="q"`.
      `/paquetes` y `/residentes` requieren sesión de staff, verificados vía
      test dedicado en vez de curl en vivo. Con esto quedan cubiertas las
      12 vistas con formulario real al cargar la página.

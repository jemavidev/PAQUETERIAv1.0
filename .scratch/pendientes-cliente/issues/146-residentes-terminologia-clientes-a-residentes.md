# 146 — Terminología: "Clientes" → "Residentes" en la vista `/residentes`

**Pedido original:** "Analiza nuevamente y confírmame que esta vista de residentes se alinea con
todo lo comentado en las otras 2 vistas de paquetes y anuncios, adicional necesito que se cambie
el término de clientes a residentes, ya que eso es lo que son, residentes."

**Status:** implementado (alcance explicado abajo -- ver "Fuera de alcance")

## Contexto importante: esto revierte una decisión anterior

`Residentes -> Clientes` fue un rename **explícito y deliberado** del propio Grupo 10/Ronda 2
(commit `7fb0876`, 2026-07-28): `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`
línea 256 dice textualmente *"`Residentes` se renombra a `Clientes` solo como etiqueta del
link -- la ruta sigue siendo `/residentes`"*. No encontré documentado el motivo original de ese
cambio. Este ticket revierte esa decisión puntual por instrucción explícita y directa en esta
sesión -- quedó documentado acá para que una sesión futura no la revierta de nuevo sin saber que
ya se decidió dos veces.

## Auditoría de alineación con /paquetes y /announce (pedido explícito)

- **Confirmado**: `/announce` (staff, `announce_new.py`) ya usa "residente(s)" en todo su copy
  visible -- nunca "cliente". El propio link desde `/announce` hacia esta vista ya decía
  "¿Solo registrar **residentes**?" (`announce_new/form.html`), antes de este cambio -- evidencia
  de que la vista `/residentes` (etiquetada "Clientes") ya era la excepción, no la norma.
- **Confirmado**: modales de confirmación, ya alineados con `/paquetes` -- ver [[145]].
- **Confirmado**: ancho de contenido alineado con el header en las 3 vistas de lista/tabla
  (`/paquetes`, `/residentes`, `/administracion/personal`) -- ver [[143]], sin cambios acá.
- **Divergencia real, NO tocada en este ticket**: `/paquetes` y `/announce` usan la fuente Nunito
  Sans (`packages/list.html`, `announce_new/form.html` -- ver [[132]]), `/residentes` no. El
  scope original de [[132]] fue explícitamente "SOLO /paquetes y /announce, no base.html" -- no
  asumí que debía extenderse a `/residentes` sin que se pida.

## Qué se renombró (alcance: copy visible de `/residentes` + sus puntos de entrada)

- Nav de staff (desktop y footer móvil, `base.html`): "Clientes" → "Residentes" (el link sigue
  siendo `/residentes`, sin tocar la ruta).
- `customers_manage/search.html`: título de pestaña, `<h1>`, "Buscar clientes" → "Buscar
  residentes", tooltip/modal "Eliminar cliente" → "Eliminar residente", estados vacíos ("Sin
  clientes todavía" → "Sin residentes todavía", mensaje de sin-resultados).
- `customers_manage/detail.html`: título de pestaña, "Ficha de cliente"/"Volver a Clientes" →
  "Ficha de residente"/"Volver a Residentes", "Datos del cliente" → "Datos del residente", los 3
  párrafos de ayuda que decían "este cliente"/"el cliente".
- `customers_manage.py` (ruta): mensaje 404 "Cliente no encontrado" → "Residente no encontrado",
  los 2 avisos de `_aviso_reasignacion_bloqueada` (tab Dirección), el aviso de dato huérfano, el
  error de "falta apartamento/nombre" al agregar Ocupante -- todos user-facing. Varios docstrings
  internos también, por consistencia (no user-facing pero describen la misma entidad).
- `components/_breadcrumbs.html` y `components/_tablas.html`: ejemplos de uso en los comentarios
  del componente (no afectan render, pero quedaban con el texto viejo como referencia).
- `tests/web/test_customers_manage.py` / `test_layout.py`: 2 aserciones que dependían del texto
  literal viejo ("sin clientes todavía", ">Clientes<" en el nav) -- actualizadas para no quedar
  rotas, y un test renombrado (`test_residentes_sin_clientes_registrados...` →
  `...sin_residentes_registrados...`).

## Fuera de alcance (deliberado, no tocado)

- **Columna "Cliente" de `/paquetes`** (`packages/_resultados.html`, encabezado de tabla +
  bastante documentación de issues previas alrededor de ese nombre exacto). Es la misma
  inconsistencia de fondo, pero es una vista distinta, activamente iterada, con su propia
  historia de decisiones sobre ese nombre de columna -- no se tocó sin que se pida
  explícitamente.
- **Concepto amplio de "Customer"/autoservicio** (`customer_verify.py`, `customer_portal.py`,
  `CUSTOMER_SESSION_KEY`, "Portal de Clientes" en `/ayuda`, el bloque "Cliente" del menú de
  cuenta en `base.html` cuando un staff también es residente). Es la misma palabra pero un
  concepto de producto distinto (el rol/sesión de autoservicio del residente logueado por OTP,
  no la gestión de fichas por staff) -- cambiar esos nombres es un rename de módulos/rutas/
  constantes de sesión mucho más grande, fuera de lo que pide este ticket.
- **`app/routes/customers.py` y el resto de `app/` (fuera de `app/web/`)**: es el backend legacy
  "PAQUETES EL CLUB v1.0", un sistema distinto que convive en el mismo repo -- no forma parte de
  PaqueteX v2 ni de esta vista.
- **`.scratch/pendientes-cliente/` y todo comentario "pedido del cliente"**: "cliente" ahí
  significa el cliente de negocio de Papyrus (quien pide features), no un residente -- palabra
  distinta, no se toca.

## Verificación

- Sintaxis Jinja (`Environment.parse()`) sobre las 5 plantillas tocadas -- OK.
- `tests/web/test_customers_manage.py` + `tests/web/test_layout.py`: 118/118 tras actualizar las
  2 aserciones con texto literal viejo.
- Suite completa del repo corriendo en background al momento de escribir este ticket -- pendiente
  de confirmar 0 regresiones fuera de las 2 ya corregidas.
- Pendiente: confirmación visual en navegador real (sin acceso a la extensión Chrome en esta
  sesión).

# 335 — Unificar look and feel de 7 vistas de Administración/Mi perfil

**Pedido original (cliente):**
"estas vistas /administracion/tarifas-cobro, /administracion/motivos-anulacion-cobro,
/administracion/motivos-bloqueo, /administracion/migrar-anio,
/administracion/contactos-externos, /administracion/conjunto, /mi-sesion todas estas
vistas no corresponden a lo que se supone que es el look and feel del aplicativo
(responsive, anchos unificados, uniformidad en lo que ve, en general tienen un look
and feel diferente al resto del aplicativo, analiza como maneja el aplicativo estas
cosas y dime si puedes corregirlas de la mejor manera)"

**Status:** implementado

## Análisis

Se comparó cada una de las 7 vistas contra el patrón ya establecido en el resto del
código (`admin/staff.html`, `packages/list.html`, `customers_manage/search.html`,
`announce/form.html`, componentes en `components/_*.html`).

Conclusión: **5 de las 7 ya siguen el patrón "tarjeta única" ya establecido** para
formularios cortos (`max-w-md mx-auto px-4 py-8`, macro `formulario_flujo` de
`_formularios.html` — el mismo contenedor exacto que usa `/anunciar`, la referencia
del design system para este tipo de pantalla). No son inconsistentes con el resto de
la app por ese lado — el ancho angosto es intencional para una tarjeta de 1-4 campos,
igual que login/registro/anunciar. Donde SÍ hay defectos reales, contra el propio
estándar del código:

1. **`admin/contactos_externos.html`** — única vista de las 7 que NO importa ningún
   componente del design system (`_inputs.html`, `_botones.html`, `_paginacion.html`).
   Input y botón de búsqueda son HTML crudo con clases ad-hoc; la paginación es
   "Anterior/Siguiente" hecho a mano en vez del macro compartido `paginacion()`
   (`components/_paginacion.html`, pensado explícitamente para "cualquier listado
   paginado, no solo `/paquetes`"); el `<h1>` usa `text-lg font-semibold` en vez del
   `text-xl font-bold` que usan `staff.html`/`packages/list.html`/`auth/me.html`. Es
   estructuralmente una vista de búsqueda+lista (como `/residentes`), no un formulario
   corto, así que el contenedor angosto (`max-w-2xl`) tampoco calza con ese rol.

2. **`admin/migrar_anio.html`** — único botón primario de las 7 vistas que NO usa el
   macro `boton()` de `_botones.html`: es un `<button>` crudo en `bg-slate-900`
   (negro/gris oscuro) en vez del azul de marca (`bg-blue-800`) que usa CUALQUIER
   otro CTA primario de la app. `<h1>` también en `text-lg font-semibold` en vez de
   `text-xl font-bold`.

3. **Pulido menor (las 5 de "tarjeta única")** — `tarifas_cobro.html` (4 campos) y
   `motivos_anulacion_cobro.html`/`motivos_bloqueo.html` (1 campo) son los únicos
   formularios de la app que usan `input_texto()` SIN `icono=` — se ven "pelados"
   frente a la referencia (`/anunciar`, `auth/me.html`, `conjunto.html`, que sí
   decoran cada campo). `base.html` ya asigna un ícono temático a cada uno de estos
   ítems en el menú de cuenta (`rayo` a Tarifas, `alerta` a los 2 catálogos de
   motivos) — mismo ícono, reusado en el campo, sin inventar nada nuevo.

## Implementación

- `admin/contactos_externos.html`: contenedor pasa a `max-w-7xl mx-auto px-4
  sm:px-6 lg:px-8 py-6` (mismo criterio documentado en `staff.html`: vista de
  lista, no formulario de una columna). **Superado en vivo por una sesión
  paralela de Claude Code sobre el mismo repo (`matt-28`)** que llevó esta
  vista más lejos de lo que este ticket proponía: en vez de un GET simple +
  `paginacion()`, ahora reusa `busqueda_filtros()` (mismo mecanismo de
  búsqueda en vivo con fetch+debounce de `/paquetes`/`/residentes`), con un
  fragmento nuevo (`admin/_contactos_externos_resultados.html`) que trae
  `<table>` de verdad (6 columnas: Nombre/Teléfono(s)/WhatsApp/Fuentes/
  Creado/Actualizado, mismo estilo de tabla que `staff.html`) y el
  componente compartido `_estado_vacio.html` para "sin resultados". Ruta
  (`admin.py`) actualizada para servir el fragmento en peticiones en vivo
  (`_peticion_en_vivo_contactos_externos`). Este archivo terminó con una
  implementación MÁS alineada al resto de la app (`/paquetes`, `/residentes`)
  que la propuesta original de este ticket -- no se revirtió, se adoptó tal
  cual quedó. Ver comentario al final.
- `admin/migrar_anio.html`: botón reemplazado por `boton('Confirmar migración',
  type='submit', full_width=True, disabled=(total==0), icono=iconos_nav.reloj)`;
  `<h1>` a `text-xl font-bold`.
- `admin/tarifas_cobro.html`: los 4 `input_texto()` reciben `icono=iconos_nav.rayo`.
- `admin/motivos_anulacion_cobro.html` / `admin/motivos_bloqueo.html`: el
  `input_texto('Etiqueta', ...)` recibe `icono=iconos_nav.alerta`.
- `admin/conjunto.html` / `auth/me.html` (`/mi-sesion`): sin cambios — ya siguen
  el patrón establecido (`formulario_flujo` + campos con ícono).

## Verificación

- Suite completa relevante corrida en local (`test_admin_conjunto.py`,
  `test_admin_contactos_externos.py`, `test_admin_migrar_anio.py`,
  `test_admin_motivos_anulacion_cobro.py`, `test_admin_motivos_bloqueo.py`,
  `test_admin_tarifas_cobro.py`, `test_auth.py`): 55 tests, todos pasan.
  Se verificó además que ninguna clase de Tailwind nueva quedó sin compilar
  (las 44 clases usadas en los 5 archivos editados por esta sesión ya
  existían en `tailwind.css` por venir de macros ya usados en otras
  vistas -- no hizo falta rebuild).
- Pendiente: revisar visualmente en `test.papyrus.com.co` (o `localhost:8010`)
  las 7 vistas en mobile y desktop -- no se pudo abrir un navegador real desde
  esta sesión (extensión Chrome no conectada).

## Nota fuera de alcance

`admin/estadisticas_cobro.html` y `admin/proveedores.html` (no listados por el
cliente) comparten el mismo `<h1 class="text-lg font-...">` en vez de `text-xl
font-bold` — mismo defecto menor que 2 de las vistas de acá. No se tocan en este
ticket (el cliente no las mencionó); quedan anotadas acá por si se quiere unificar
después.

## Comments

Mientras se implementaba este ticket se detectó (vía `git status`, el archivo
`admin/contactos_externos.html` cambió en disco sin que esta sesión lo tocara)
que otra sesión de Claude Code sobre el MISMO repo (`matt-28`, misma máquina,
mismo working tree) estaba trabajando en paralelo sobre esa misma vista —
aparentemente el mismo pedido del cliente, lanzado en dos terminales a la vez.
Se dejó su versión tal cual (quedó más completa que la de acá, ver
"Implementación" arriba) y no se volvió a tocar ese archivo desde esta sesión.
Vale la pena que el cliente confirme si eso fue intencional (comparar 2
enfoques) o un descuido (2 terminales abiertas sin querer) — si es lo segundo,
conviene cerrar una de las 2 sesiones para no seguir arriesgando choques sobre
los mismos archivos.

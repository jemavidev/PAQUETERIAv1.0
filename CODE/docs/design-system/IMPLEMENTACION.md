# PaqueteX — Guía de implementación del tema

Documento de cierre del design system. Si estás retomando este proyecto para el refactoring
real (migrar las plantillas del rebuild de su CSS ad-hoc a los componentes), **este es el punto
de partida** — te dice qué existe, dónde está, qué ya se corrigió contra producción, y qué falta
página por página.

No leas esto en vez de `tokens.md` — léelo antes: te dice qué sección de `tokens.md` te importa
para cada pantalla.

---

## 1. Qué es este tema, en una frase

El tema visual real de PaqueteX es el de **Papyrus SAS** (`paqueteex.papyrus.com.co`, sistema
"PAQUETES EL CLUB v4.0", agencia de desarrollo JEMAVI) — colibrí como ícono/favicon, azul
`#1e40af` como color principal, y una paleta de 20 colores con nombre ya definida en su propio
`variables.css`. Este design system (`docs/design-system/`) es la traducción de ese tema real a
15 componentes Jinja2 reutilizables para el rebuild (`src/app/web/`), verificados contra el
código fuente real de producción por SSH — no inventados desde cero ni aproximados a ojo.

## 2. Dónde está todo

| Qué | Dónde |
|---|---|
| Reglas de trabajo (cómo se diseñó cada componente) | `docs/design-system/README.md` |
| Fuente de verdad del vocabulario visual (colores, tipografía, espaciado, sombras) | `docs/design-system/tokens.md` — 20 secciones |
| Previews visuales, uno por componente, abrir en navegador | `docs/design-system/previews/*.html` |
| Comparación línea por línea con producción real | `docs/design-system/previews/comparacion-produccion-vs-nuevo.html` |
| **Macros Jinja2 finales, lo que se importa en las plantillas reales** | `src/app/web/templates/components/_*.html` |
| Assets de marca reales (bajados de producción por SSH, no reinventados) | `src/app/web/templates/static/branding/` — `colibri-icono.png` (favicon + logo del header), `papyrus-logo.png` (wordmark completo, sin usar todavía) |
| Layout compartido — header, footer, favicon — YA integrado | `src/app/web/templates/base.html` |

## 3. Los 15 componentes — todos cerrados

| # | Componente | Macro | Import |
|---|---|---|---|
| 1 | Botones | `boton(texto, variant, size, ...)` | `from 'components/_botones.html' import boton` |
| 2 | Badges de estado | `badge(estado)` | `from 'components/_badge.html' import badge` |
| 3 | Inputs de texto | `input_texto(label, name, ...)` | `from 'components/_inputs.html' import input_texto` |
| 4 | Tarjetas | `tarjeta_paquete(p)`, `tarjeta_cliente(cliente, ubicacion)` | `from 'components/_tarjetas.html' import tarjeta_paquete, tarjeta_cliente` |
| 5 | Formularios de flujo | `formulario_flujo(titulo, action, boton_texto, ...)` | `from 'components/_formularios.html' import formulario_flujo` |
| 6 | Tablas de datos | `accion_icono(icono, titulo, ...)` (el `<table>` se escribe directo) | `from 'components/_tablas.html' import accion_icono` |
| 7 | Timeline de seguimiento | `timeline_paquete()`, `paso_timeline(titulo, badge_texto, rol, ...)` | `from 'components/_timeline.html' import timeline_paquete, paso_timeline` |
| 8 | Alertas / toast | `toast(mensaje, variant, duracion_ms, id)` | `from 'components/_toast.html' import toast` |
| 9 | Modales / confirmación | `modal(id, titulo)`, `modal_confirmacion(...)`, `grupo_chips(...)` | `from 'components/_modales.html' import modal, modal_confirmacion, grupo_chips` |
| 10 | Carga de fotos (S3) | `carga_fotos(name, max_fotos, id, etiqueta)` | `from 'components/_carga_fotos.html' import carga_fotos` |
| 11 | Búsqueda y filtros | `busqueda_filtros(accion, ...)`, `filtro_estado(seleccionado)` | `from 'components/_busqueda_filtros.html' import busqueda_filtros` |
| 12 | Paginación | `paginacion(pagina_actual, total_paginas, base_url, params)` | `from 'components/_paginacion.html' import paginacion` |
| 13 | Breadcrumbs / volver | `encabezado_volver(titulo, href_volver, texto_volver, ...)` | `from 'components/_breadcrumbs.html' import encabezado_volver` |
| 14 | Empty states | `estado_vacio(titulo, mensaje, icono, boton_texto, boton_href)` | `from 'components/_estado_vacio.html' import estado_vacio` |
| 15 | Estados de carga | `estado_carga(texto, alto)` | `from 'components/_estado_carga.html' import estado_carga` |

Detalle de cada uno (colores exactos, por qué se diseñó así, casos borde) está en su sección
correspondiente de `tokens.md` (secciones 1-20, indexadas por nombre de componente).

## 4. Correcciones aplicadas contra producción (2026-07-29) — léelas antes de migrar nada

El diseño original de este sistema se hizo sin acceso al servidor. Al conectarse por SSH
(`ssh paquetex`, repo `PAQUETERIAv1.0`, mismo repo que este) se encontraron y corrigieron 3 cosas
que **cambian cómo se ve cualquier página que migres** — si estás portando una plantilla legacy,
no copies sus colores ad-hoc, usá los del design system corregido:

1. **El mapeo estado→color estaba invertido.** Real: `ANUNCIADO`=ámbar, `RECIBIDO`=azul,
   `ENTREGADO`=verde, `CANCELADO`=rojo, `DEVUELTO`=naranja (5º estado que no existe todavía en
   `EstadoPaquete` local). Ver `tokens.md` sección 6.
2. **Los 4 roles de acción (botones/toasts/íconos) tenían tonos inventados.** Reales:
   `primary`=`blue-800` (no `blue-600`), `success`=`emerald-600` (no `-700`),
   `warning`=**naranja** `orange-600` (no ámbar), `danger`=`red-600` (sin cambio). Ver sección 1.
3. **Favicon, logo del header y footer** ahora son los reales de producción (colibrí +
   Ayuda/WhatsApp/Teléfono con íconos + "Desarrollado por JEMAVI © PAPYRUS"). Ya integrados en
   `base.html` — no hace falta tocarlos de nuevo al migrar páginas.

Nota técnica que hay que respetar si el footer vuelve a cambiar de altura: el toast (`_toast.html`)
se ancla a `bottom-24` porque el footer mide 80px — estos dos números están acoplados a propósito
(comentario cruzado en `base.html`, `_toast.html` y `tokens.md` sección 13).

## 5. Checklist de migración — página por página

**Tandas 1, 2 y 3 completas (2026-07-30): `packages/list.html`, `customers_manage/detail.html` y
`search/form.html` ya usan los componentes.** El resto de plantillas todavía no importa nada de
`components/` y sigue con su propio `<style>` inline.

Leyenda de estado: ✅ migrada · 🔴 no iniciado · las columnas de componentes son la lista de qué
aplica, no un orden obligatorio.

| Plantilla | Qué tiene hoy (ad-hoc) | Componentes que aplican |
|---|---|---|
| `packages/list.html` ✅ | ~~Lista de paquetes + filtros + paginación + 4 modales (recibir/corregir/entregar/cancelar) + scanner de guía~~ Migrada a Tarjetas (`tarjeta_paquete`, con `mostrar_codigo=False` — ver nota en el macro), Búsqueda y filtros, Paginación, Modales (`modal`, `modal_confirmacion`, `grupo_chips` para tipo/condición/motivo), Carga de fotos, Badges, Empty states, Toast (error). El scanner ZXing y el doble-check de guía siguen siendo JS/CSS propios de la página (no son parte del design system) — ver el `<style>` de ganchos `.scan-*`/`.guia-check-*` en el `head` de la plantilla. |
| `packages/_modal.html` | Macro `modal()` ad-hoc, bottom-sheet | Ya no lo usa `packages/list.html` (reemplazado por `_modales.html` → `modal()`). **Todavía lo usa `admin/staff.html`** — no se elimina hasta que esa pantalla también migre. |
| `admin/staff.html` | Lista de personal (tarjetas), alta de staff, editar/resetear (modales) | Tablas (`accion_icono` para editar/resetear/activar/desactivar), Modales, Formularios (alta de staff), Botones, Toast |
| `admin/notificaciones.html` | Formulario + error/ok | Formularios, Inputs, Botones, Toast |
| `announce/form.html` | Nombre + Teléfono + checkbox T&C (el caso de referencia de Formularios) | Formularios (`formulario_flujo`), Inputs, Botones |
| `announce_new/form.html` | Variante del anterior, con error/ok | Formularios, Inputs, Botones, Toast |
| `announce/confirmacion.html` | Página de éxito simple | No hay un componente "confirmación de página completa" en la lista de 15 — evaluar si Empty states (`estado_vacio` con ícono de éxito) encaja o si amerita un componente nuevo |
| `auth/login.html`, `auth/entrar.html`, `auth/me.html` | Forms de login/sesión staff | Formularios, Inputs, Botones, Toast |
| `auth/customer_login.html`, `auth/customer_verify.html`, `auth/customer_me.html` | Forms de login/verificación cliente (OTP) | Formularios, Inputs, Botones, Toast |
| `ayuda/form.html` | Formulario de contacto/ayuda | Formularios, Inputs, Botones |
| `customer/paquetes.html` | Lista de paquetes del cliente + empty state | Tarjetas (`tarjeta_paquete`), Empty states, Timeline (si se agrega seguimiento por paquete) |
| `customer/verify.html` | Form + tabla + error/ok | Formularios, Tablas, Toast |
| `customers_manage/search.html` | Búsqueda simple de clientes (un campo) | Búsqueda y filtros (`busqueda_filtros(..., mostrar_estado=False, mostrar_torre_apartamento=False)` — ya diseñado para este caso exacto) |
| `customers_manage/detail.html` ✅ | ~~Ficha de cliente — sin forma de volver a la lista~~ Migrada a Breadcrumbs (`encabezado_volver`), Formularios (`formulario_flujo` para nombre/email/segundo contacto/SMS), Toast (error/guardado). "Zona de peligro" pasó del `confirm()` nativo del navegador a `modal_confirmacion` (variant danger) — mismo texto, mismo endpoint, ahora consistente con Cancelar en `packages/list.html`. Ocupantes de la unidad sigue siendo una tarjeta a mano (no hay componente de "fila de ocupante" entre los 15). |
| `search/form.html` ✅ | ~~Tracking público — usaba un `.timeline` ad-hoc que predataba al componente 7~~ Migrada a Timeline (`paso_timeline`, con `rol` solo en el hito que coincide con `paquete.estado` — el resto en gris, misma regla que Badges), Búsqueda y filtros (caso simple, sin estado/torre/apartamento), Badge (estado actual), Empty states (sin resultados). El timeline sigue mostrando solo los hitos OCURRIDOS (sin pasos "pendientes" — la ruta no arma esa info); las fotos quedan en una grilla con Tailwind (no se usó `tarjeta_paquete`, ese macro asume un paquete de lista, no una galería). |

### Orden sugerido (no obligatorio)

1. ~~`packages/list.html`~~ ✅ hecho (2026-07-30) — desplegado y verificado en vivo en
   `test.papyrus.com.co`.
2. ~~`customers_manage/detail.html`~~ ✅ hecho (2026-07-30).
3. ~~`search/form.html`~~ ✅ hecho (2026-07-30).
4. El resto de formularios (`announce/*`, `auth/*`, `admin/notificaciones.html`,
   `ayuda/form.html`) — son todos el mismo patrón (Formularios + Inputs + Botones + Toast),
   conviene hacerlos en lote una vez que el patrón esté probado en una pantalla real.
5. `admin/staff.html` — pendiente; sigue importando `packages/_modal.html` (ver sección 5), es el
   único motivo por el que ese archivo ad-hoc no se ha borrado todavía.

## 6. Reglas para cuando migres (no renegociables sin pedirlo)

Las mismas de siempre (`README.md` sección "Reglas de interacción"), la que más importa acá:

- **No reinventar colores/radios/sombras al migrar.** Si una plantilla legacy usa un azul o un
  verde que no es exactamente el de `tokens.md`, se cambia al de `tokens.md` — el objetivo de
  migrar es unificar, no preservar la variación ad-hoc que ya había.
- Mobile-first, un solo bloque con `sm:`/`md:`/`lg:` — nunca una plantilla por dispositivo.
- Si una pantalla necesita algo que ningún componente cubre (ej. la confirmación de
  `announce/confirmacion.html`), es una ronda de diseño nueva (3 opciones, elegir, cerrar) — no
  se improvisa CSS ad-hoc nuevo por fuera del sistema.

## 7. Lo que NO está hecho todavía

- Solo una plantilla real migrada hasta ahora: `packages/list.html` (sección 5). El resto de la
  lista sigue con su `<style>` ad-hoc.
- Componente para "página de confirmación/éxito" no existe como los 15 — evaluar si hace falta
  antes de migrar `announce/confirmacion.html`.
- Íconos de navegación en el **header** de escritorio (`.site-nav`) — el footer ya los tiene, el
  header todavía es solo texto. No se tocó en esta ronda por no haber sido pedido explícitamente.
- `_iconos.html` centralizado — hoy cada componente repite sus propios `<path>` SVG inline. Es una
  mejora de mantenibilidad identificada pero no construida (ver análisis del 2026-07-29 en el
  historial de esta conversación).
- `papyrus-logo.png` (el wordmark ancho) está descargado pero sin usar en ninguna pantalla
  todavía — candidato natural para una pantalla de login o splash si se necesita en algún punto.

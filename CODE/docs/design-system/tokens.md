# PaqueteX — Design Tokens

**Estado:** Fijado a partir del componente Botones (Variante A "Vívida"), aprobado por el usuario.
**Corregido el 2026-07-29** contra los valores REALES de producción
(`paqueteex.papyrus.com.co`, extraídos por SSH de `CODE/src/static/css/variables.css`,
`components/buttons.css` y `components/status.css` del repo `PAQUETERIAv1.0`) — ver nota al final
de la sección 1. Los primeros 5 componentes de este documento se diseñaron antes de tener acceso a
esos valores reales; donde había una diferencia, gana producción, porque es la marca real que el
staff ya usa a diario, no una paleta inventada.

Este documento es la **fuente de verdad** del vocabulario visual de PaqueteX. Todo componente
nuevo del design system (badges, tarjetas, alertas, modales, inputs, etc.) debe **heredar** estos
tokens — no reinventar radios, sombras, anillos de foco ni tonos de color por su cuenta.

Implementación de referencia: `src/app/web/templates/components/_botones.html`
Preview visual: `docs/design-system/previews/botones.html`

---

## 1. Roles semánticos de color

Cada rol tiene un significado fijo en todo el sistema. No reasignar un color a un rol distinto
del que aquí se define (ej. el azul siempre es "primario/informativo", nunca "peligro"). Valores
exactos = `.btn-primary`/`.btn-success`/`.btn-warning`/`.btn-danger` de producción.

| Rol | Uso | Fondo | Hover | Texto | Anillo de foco |
|---|---|---|---|---|---|
| **primary** | Acción principal, informativo neutro | `bg-blue-800` (`#1e40af`) | `hover:bg-blue-700` (`#1d4ed8` — sí, más CLARO al hover, es el comportamiento real de producción, no un error) | `text-white` | `focus-visible:ring-blue-300` |
| **success** | Confirmación, estado positivo/completado | `bg-emerald-600` (`#059669`) | `hover:bg-emerald-700` (`#047857`) | `text-white` | `focus-visible:ring-emerald-300` |
| **warning** | Advertencia, acción pendiente del staff (NO es el color de "Anunciado" — ver sección 6) | `bg-orange-600` (`#ea580c`) | `hover:bg-orange-700` (`#c2410c`) | `text-white` | `focus-visible:ring-orange-300` |
| **danger** | Peligro, eliminar, cancelar | `bg-red-600` (`#dc2626`) | `hover:bg-red-700` (`#b91c1c`) | `text-white` | `focus-visible:ring-red-300` |
| **disabled** | Estado inactivo (vía atributo `disabled`, no un rol de color aparte) | `disabled:bg-gray-200` | — | `disabled:text-gray-400` | sin anillo (no interactivo) |

### Corrección 2026-07-29 — de dónde salen estos valores

Antes de tener acceso al servidor de producción, este documento definía `primary=blue-600`,
`success=emerald-700`, `warning=amber-500/text-amber-950` — una paleta razonable pero inventada.
Al analizar `paqueteex.papyrus.com.co` por SSH apareció el sistema de diseño real
(`variables.css`, 224 líneas, ya con paleta/tipografía/espaciado/sombras/z-index documentados) y
sus 4 botones semánticos reales. La diferencia más notable: **`warning` es naranja (`orange-600`),
no ámbar** — con `orange-600` el texto blanco SÍ pasa AA sin necesitar el color oscuro que
usábamos antes (ver nota de accesibilidad abajo, ahora obsoleta para el rol `warning`).

### Nota de accesibilidad — texto oscuro solo sigue haciendo falta para el acento ANUNCIADO

Con `warning=orange-600` (confirmado en producción con `text-white`), la regla de "texto oscuro
en vez de blanco" YA NO aplica a los 4 roles genéricos — los 4 pasan AA con `text-white` sobre su
fondo sólido. Donde SÍ sigue haciendo falta texto/ícono oscuro es en el acento ámbar reservado
para el estado `ANUNCIADO` (sección 6) cuando se usa como relleno sólido (ej. el ícono de paso
"actual" en Timeline) — ese ámbar es un 5º color fuera de los 4 roles, y sí falla AA con blanco.

---

## 2. Forma base (botones)

Heredable por defecto en componentes sólidos futuros, pero cada componente nuevo confirma su
propia forma en su propia ronda de diseño — esto no es una imposición automática.

| Token | Valor | Clase Tailwind |
|---|---|---|
| Radio de borde | 8px | `rounded-lg` |
| Sombra en reposo | sutil | `shadow-sm` |
| Sombra en hover | elevación suave | `hover:shadow-md` |
| Transición | suave, sin brusquedad | `transition` |

## 3. Foco (accesibilidad — obligatorio en todo elemento interactivo)

```
focus-visible:ring-2 focus-visible:ring-{color}-300 focus-visible:ring-offset-2 focus-visible:outline-none
```

`{color}` = el color del rol semántico del elemento (`blue`, `emerald`, `orange`, `red` — o `amber`
específicamente para el acento ANUNCIADO de la sección 6, que no es uno de los 4 roles genéricos).

## 4. Tamaños

**Corregido el 2026-07-31** — el tamaño `base` original (`px-4 py-2 text-sm`, ≈36px de alto) quedaba
visiblemente más chico que el botón real de producción, medido en vivo en `paquetex.papyrus.com.co`:
50px de alto, texto 16px, `padding: 12px 32px`. Se subieron los tres tamaños de la escala para que
`base` iguale ese alto real y `sm`/`lg` mantengan la jerarquía relativa (antes `lg` quedaba más
chico que el nuevo `base`).

| Tamaño | Padding | Texto |
|---|---|---|
| `sm` | `px-4 py-2` | `text-sm` |
| `base` | `px-6 py-3` | `text-base` |
| `lg` | `px-7 py-3.5` | `text-base` |

## 5. Estado loading

Spinner SVG inline (`animate-spin`) + `opacity-70 cursor-wait` + el elemento se marca `disabled`
para impedir doble envío. Ver implementación en `_botones.html`.

### Forma de tarjeta genérica — corregida el 2026-07-31

No es un componente propio de la lista de 16 (es el contenedor `bg-white border border-gray-200
rounded-* shadow-*` que reaparece en Formularios, Empty states, Búsqueda y filtros, Confirmación,
y varias plantillas reales) pero se corrigió al mismo tiempo que Botones/Inputs por el mismo
motivo: comparado en vivo con producción, la sombra (`shadow-sm`) y el radio (`rounded-xl`, 12px)
quedaban más planos que el `shadow-lg`/`rounded-2xl` (16px) real. Regla aplicada en todo el
sistema:

| Contexto | Antes | Ahora |
|---|---|---|
| Tarjetas de página (Formularios, Empty states, Búsqueda y filtros, Confirmación, tarjetas sueltas en pantallas) | `rounded-xl shadow-sm` | `rounded-2xl shadow` |
| Tarjetas compactas de lista (`tarjeta_paquete`/`tarjeta_cliente`, pasos de Timeline, tarjeta de "Mis paquetes") | `rounded-lg shadow-sm` | sin cambio de radio — ver nota |
| Modales (`_modales.html`) | `rounded-2xl shadow-xl` | sin cambio — ya tenían más sombra que el resto |

Nota: las tarjetas compactas de lista (radio 8px) no subieron de radio a propósito — son ítems
densos dentro de una lista/grid, no contenedores de página completa; subir su radio al mismo nivel
que una tarjeta de formulario las haría desproporcionadamente redondeadas para su tamaño.

---

## 6. Mapeo de dominio → color (referencia para Badges y componentes futuros)

**Corregido el 2026-07-29.** El mapeo original de este documento (`ANUNCIADO=primary` azul,
`RECIBIDO=warning` ámbar) estaba invertido respecto al que el staff ya usa a diario en producción,
y además estaba inventado sin verificar contra el sistema real. El mapeo real, confirmado en
`CODE/src/static/css/components/status.css` de producción:

| Estado de dominio | Color real (producción) | Rol semántico local |
|---|---|---|
| `ANUNCIADO` | ámbar/amarillo (`--papyrus-yellow`, `#d97706`) | **Ninguno de los 4 roles** — acento propio, ver nota abajo |
| `RECIBIDO` | azul (`--papyrus-blue`, `#1e40af`) | `primary` |
| `ENTREGADO` | verde (`--papyrus-green`, `#059669`) | `success` |
| `CANCELADO` | rojo (`--papyrus-red`, `#dc2626`) | `danger` |
| `DEVUELTO` *(no existe hoy en `EstadoPaquete` local — ver nota)* | naranja (`--papyrus-orange`, `#ea580c`) | `warning` |

Este mapeo es vinculante para Badges (sección 7), Timeline (sección 12) y los chips de estado de
Búsqueda y filtros (sección 16).

### Por qué `ANUNCIADO` no es uno de los 4 roles genéricos

Los 4 roles (`primary`/`success`/`warning`/`danger`) existen para botones y feedback genérico de
UI, y en producción cada uno de `RECIBIDO`/`ENTREGADO`/`CANCELADO`/`DEVUELTO` coincide exactamente
con uno de esos 4 colores de botón. `ANUNCIADO`, en cambio, usa un 5º color (ámbar) que no
corresponde a ningún botón semántico — es un acento dedicado solo a ese estado. Los componentes
que necesiten pintar `ANUNCIADO` con relleno sólido (no solo badge/texto) deben usar
`bg-amber-500` + `text-amber-950` (el mismo carve-out de contraste que antes aplicaba a todo el
rol `warning` — ver sección 1) en vez de intentar forzarlo dentro de uno de los 4 roles.

### Nota: `DEVUELTO` no existe en el dominio local todavía

`EstadoPaquete` en `src/app/domain/paquete.py` solo define ANUNCIADO/RECIBIDO/ENTREGADO/CANCELADO
— el rebuild nunca modeló un 5º estado "Devuelto al transportador" como estado propio (aunque sí
existe como *motivo de cancelación*, `MotivoCancelacion.DEVUELTO_AL_TRANSPORTADOR`). Badges
(sección 7) incluye la clase para `DEVUELTO` de todas formas, por si el dominio lo incorpora más
adelante — es una decisión de producto pendiente, no de diseño, y no se agrega a los chips de
filtro de Búsqueda (sección 16) porque hoy no existe ningún paquete con ese estado para filtrar.

---

## 7. Badges (componente cerrado)

**Forma aprobada:** fondo suave (soft) — pastel de fondo, texto y borde en tono fuerte. Deliberadamente
distinta a la forma sólida de Botones (`rounded-full` en vez de `rounded-lg`, sin sombra) para que un
badge nunca se confunda visualmente con un botón interactivo.

Implementación de referencia: `src/app/web/templates/components/_badge.html`
Preview visual: `docs/design-system/previews/badges.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Radio de borde | píldora completa | `rounded-full` |
| Padding | — | `px-3 py-1` |
| Tipografía | — | `text-xs font-semibold` |
| Borde | 1px, tono del rol (no siempre `-200`, ver tabla — depende del color real de producción) | `border border-{color}-{tono}` |
| Sombra | ninguna (a propósito — no es interactivo) | — |

### Mapeo de estado → clases — **corregido el 2026-07-29 a los valores exactos de producción**

`CODE/src/static/css/components/status.css` de producción, línea por línea (no aproximado):

| Estado | Texto mostrado | Clases | Hex real (fondo / texto / borde) |
|---|---|---|---|
| `ANUNCIADO` | Anunciado | `bg-amber-100 text-amber-600 border-amber-200` | `#fef3c7` / `#d97706` / `#fde68a` |
| `RECIBIDO` | Recibido | `bg-blue-100 text-blue-800 border-blue-300` | `#dbeafe` / `#1e40af` / `#93c5fd` |
| `ENTREGADO` | Entregado | `bg-emerald-100 text-emerald-600 border-green-300` (sí, borde `green` no `emerald` — así está en producción) | `#d1fae5` / `#059669` / `#86efac` |
| `CANCELADO` | Cancelado | `bg-red-100 text-red-600 border-red-300` | `#fee2e2` / `#dc2626` / `#fca5a5` |
| `DEVUELTO` | Devuelto | `bg-orange-200 text-orange-600 border-orange-300` | `#fed7aa` / `#ea580c` / `#fdba74` |
| *(no reconocido)* | capitalización del valor recibido, o "Desconocido" | `bg-gray-50 text-gray-600 border-gray-200` (fallback defensivo, nunca falla) | — |

Nota: el fondo pasó de `-50` a `-100` y el borde de `-200` a `-300` en varios estados respecto a
la primera versión de este documento — no es un ajuste estético nuestro, es literalmente lo que
usa producción. `DEVUELTO` no es un estado real de `EstadoPaquete` hoy (ver sección 6) pero el
macro lo incluye por si el dominio lo agrega — no falla, solo no se usa todavía.

El macro `badge(estado)` acepta tanto el miembro del enum `EstadoPaquete` como su string plano
(`.value` o texto ya en mayúsculas/minúsculas) y resuelve el mapeo internamente.

---

## 8. Inputs de texto (componente cerrado)

**Forma aprobada:** Opción 1 — Clásico (label fija arriba, borde simple). El patrón más
predecible (Jakob's Law), sin floating labels ni acentos de color — pensado para formularios
rápidos de mostrador. Reutiliza el mismo radio de borde y anillo de foco ya fijados en Botones
(sección 2 y 3), no se reinventan.

Implementación de referencia: `src/app/web/templates/components/_inputs.html`
Preview visual: `docs/design-system/previews/inputs.html`

**Tamaño corregido el 2026-07-31** — igual que Botones (sección 4): el padding/texto original
(`px-3 py-2 text-sm`, ≈38px de alto) quedaba más chico que el input real de producción (medido en
vivo: 50px de alto, texto 16px, `padding: 12px`). Pasó a `px-3.5 py-3 text-base` (≈50px con el
borde de 1px incluido).

| Token | Valor | Clase Tailwind |
|---|---|---|
| Radio de borde | 8px | `rounded-lg` |
| Padding / texto | `px-3.5 py-3`, 16px | `px-3.5 py-3 text-base` |
| Borde normal | 1px, `slate-300` | `border border-slate-300` |
| Foco (normal) | primary | `focus-visible:border-blue-600 focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2` |
| Borde error | danger, 1px | `border border-red-600` + `focus-visible:ring-2 focus-visible:ring-red-300` |
| Borde disabled | `gray-200` + fondo `gray-50` | `border border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed` |
| Label | fija arriba, siempre visible | `text-sm font-medium text-slate-700 mb-1` |
| Mensaje de error | rojo + ícono, debajo del input | `text-xs text-red-600` + `<svg>` de alerta |
| Texto de ayuda | gris, debajo del input | `text-xs text-slate-500` |

### Prioridad error > ayuda

Si el campo tiene `error`, el mensaje de ayuda (`help_text`) se oculta para no duplicar texto
bajo el input — el macro `input_texto(...)` resuelve esto internamente. `aria-invalid` y
`aria-describedby` se fijan automáticamente para que el mensaje visible (error o ayuda) quede
enlazado al campo para lectores de pantalla.

---

## 9. Tarjetas de paquete y cliente (componente cerrado)

**Forma aprobada:** Opción 1 — Compacta de lista. Identidad + badge de estado en la primera
línea, metadatos en gris debajo, acciones en ancho completo (pulgar-friendly). Máxima densidad
para operador de mostrador escaneando muchas tarjetas en el celular. Reutiliza el badge de estado
ya cerrado (sección 7) — el color por estado no se reinventa aquí.

Implementación de referencia: `src/app/web/templates/components/_tarjetas.html`
Preview visual: `docs/design-system/previews/tarjetas.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Radio de borde | 8px | `rounded-lg` |
| Borde | 1px, `gray-200` | `border border-gray-200` |
| Sombra | sutil, sin hover (no es interactiva) | `shadow-sm` |
| Padding | — | `p-4` |
| Título (identidad) | — | `text-slate-900` (via `<strong>`) |
| Metadato primario (ubicación/código) | — | `text-sm text-slate-500` |
| Metadato secundario (guía/actor) | — | `text-xs text-slate-400` |
| Advertencia inline | mismo tono que `warning` pero sin sombra, embebida en la tarjeta | `text-xs text-amber-800 bg-amber-50 border border-amber-100 rounded-md px-2 py-1` |

### Acciones vía `{% call %}`, no hardcodeadas en el macro

Los botones de acción (Entregar/Recibir/Corregir/Cancelar) varían según `estado` y disparan
modales — eso es lógica de flujo de la vista, no de diseño. Los macros `tarjeta_paquete(p)` /
`tarjeta_cliente(cliente, ubicacion=None)` solo definen el contenedor visual y aceptan las
acciones inyectadas por `{% call %}...{% endcall %}`; sin bloque, la tarjeta no muestra fila de
botones.

### Badge de notificaciones (tarjeta cliente)

No es un estado de `EstadoPaquete`, así que no usa los 4 roles semánticos de la sección 1: activo
reutiliza `success` (`bg-emerald-50 text-emerald-700 border-emerald-200`), inactivo usa el mismo
gris neutro que el fallback de Badges (`bg-gray-50 text-gray-500 border-gray-200`) — nunca `danger`,
porque tener notificaciones apagadas no es un estado de peligro.

---

## 10. Formularios de flujo — anunciar/recibir/entregar (componente cerrado)

**Forma aprobada:** Opción 1 — Tarjeta única. Todos los campos en una sola sección, sin
subdivisiones — apta para flujos cortos (2-4 campos). No reinventa Inputs ni Botones: el
contenedor solo aporta la tarjeta, el título y el `<form>` real; los campos se inyectan vía
`{% call %}` con `input_texto(...)` (sección 8) y el CTA final es `boton(..., full_width=True)`
(sección 2, ver extensión abajo).

Implementación de referencia: `src/app/web/templates/components/_formularios.html`
Preview visual: `docs/design-system/previews/formularios.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | tarjeta centrada, ancho máx. de formulario corto | `max-w-md mx-auto bg-white border border-gray-200 rounded-xl shadow-sm p-6` |
| Título | — | `text-lg font-bold text-slate-900` |
| Subtítulo (opcional) | contexto del flujo | `text-sm text-slate-500` |
| Separación entre campos | — | `space-y-4` |
| Separación antes del CTA | — | `mt-6` |

### Extensión a Botones: `full_width`

`boton(..., full_width=True)` agrega `w-full justify-center` — el único cambio hecho al macro de
Botones (sección 2) para soportar este componente. Es aditivo y con default `False`: ningún
botón existente cambia de aspecto por esta extensión.

---

## 11. Tablas de datos (componente cerrado)

**Forma aprobada:** Opción 1 — Scroll horizontal en móvil. `<table>` real sin transformar,
envuelta en un contenedor `overflow-x-auto` con ancho mínimo — en pantallas angostas se desliza en
vez de romper el layout. Ajustes pedidos en retroalimentación: (1) las acciones tipo CRUD (Editar,
Resetear, Activar/Desactivar…) van como íconos accesibles, nunca como texto plano; (2) cada ícono
usa el color del rol semántico ya fijado (sección 1), no un gris neutro con color solo al hover.

Implementación de referencia: `src/app/web/templates/components/_tablas.html`
Preview visual: `docs/design-system/previews/tablas.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | scroll horizontal, borde redondeado | `overflow-x-auto rounded-lg border border-slate-200` |
| Ancho mínimo de tabla | fuerza el scroll en vez de aplastar columnas | `w-full min-w-[640px] text-sm` |
| Encabezado (`thead`) | fondo distinto, texto pequeño en mayúsculas | `bg-slate-50 text-xs uppercase tracking-wide text-slate-500` |
| Filas | separador fino + hover sutil | `divide-y divide-slate-100` en `tbody`, `hover:bg-slate-50` por fila |
| Celda | — | `px-4 py-3` (`px-4 py-2.5` en `th`) |
| Alineación de la columna Acciones | a la derecha | `text-right` en el `th`, contenido envuelto en `flex items-center gap-1.5 justify-end` |

### Acciones CRUD = ícono, coloreado por rol semántico

`accion_icono(icono, titulo, href=None, variant=None, type='button', ...)` — botón/enlace
solo-ícono de 32×32px (`h-8 w-8`, `rounded-lg` como Botones — no `rounded-full` como Badges, para
que se lea como interactivo), con `aria-label` + `title` obligatorios (accesibilidad: el ícono
nunca es la única pista). El fondo/borde/texto reutiliza exactamente la fórmula "soft" de Badges
(sección 7: `bg-{color}-50 text-{color}-700 border-{color}-200`, `-800` en `warning` por AA) y el
anillo de foco de la sección 3 — no se inventó una paleta nueva para esto.

Cada ícono tiene un rol semántico por defecto (sobreescribible con `variant`):

| Ícono | Rol por defecto | Uso |
|---|---|---|
| `editar` (lápiz) | `primary` | Editar un registro |
| `ver` (ojo) | `primary` | Ver detalle |
| `resetear` (llave) | `warning` | Acción sensible no destructiva (ej. reset de contraseña) |
| `activar` (check) | `success` | Reactivar un registro |
| `desactivar` (x) | `danger` | Desactivar un registro |
| `eliminar` (papelera) | `danger` | Eliminar (irreversible) |

No existe un macro que genere la tabla completa a partir de datos: cada página tiene columnas
distintas y esa abstracción agregaría más complejidad Jinja de la que ahorra. El `<table>` se
escribe directo en cada página (igual que hoy cada página escribe su propio `<style>`), reutilizando
`badge()` para columnas de estado/rol y `accion_icono()` para la columna Acciones.

---

## 12. Timeline de seguimiento (componente cerrado)

**Forma aprobada:** Vertical con línea conectora, encajonada (cada paso es su propia tarjeta), con
más información real del paquete por paso (fecha, actor, ubicación/guía/tipo/condición como
chips). Regla de color acordada en retroalimentación (2 rondas de ajuste sobre la Opción 1
original): **el color deja de significar "completado" y pasa a significar "esto es lo que está
pasando ahora"** — solo el paso que coincide con el estado ACTUAL del paquete se resalta; todo lo
demás, ya haya ocurrido o esté pendiente, va en gris neutro con su información igual de completa.

Implementación de referencia: `src/app/web/templates/components/_timeline.html`
Preview visual: `docs/design-system/previews/timeline.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | lista vertical relativa (ancla la línea conectora) | `<ol class="relative">` |
| Línea conectora | fina, gris, entre el ícono de un paso y el siguiente (se omite en el último) | `absolute left-[15px] top-8 bottom-0 w-0.5 bg-slate-200` |
| Ícono del paso actual | círculo relleno en el rol semántico + anillo suave | `bg-{color}-600/800 text-white ring-4 ring-{color}-100` (`amber-500 text-amber-950` solo para el acento ANUNCIADO, por AA — ver sección 6) |
| Ícono de paso no-actual (ya ocurrió) | círculo gris, mismo ícono de check | `bg-slate-100 text-slate-400 border border-slate-200` |
| Ícono de paso pendiente | círculo vacío, sin ícono | `bg-slate-100 text-slate-400 border-2 border-slate-200` |
| Caja del paso actual | borde + anillo en el rol semántico | `border-{color}-300 ring-1 ring-{color}-100` |
| Caja de paso no-actual | borde gris sólido | `border-slate-200` |
| Caja de paso pendiente | borde gris punteado (sin información) | `border border-dashed border-slate-200` |
| Título del paso actual | máximo énfasis | `text-slate-900` |
| Título de paso no-actual | énfasis medio | `text-slate-500` |
| Título de paso pendiente | mínimo énfasis | `text-slate-400` |
| Badge del paso | mismo rol que la caja/ícono, o gris si no es el actual | fórmula "soft" de Badges (sección 7) |
| Chips de detalle (guía/tipo/condición/ubicación) | gris siempre — el chip nunca lleva el color del rol | `text-slate-600 bg-slate-100 rounded px-2 py-0.5` |

### `rol` = el mismo mapeo estado→color de la sección 6, aplicado solo al paso activo — **corregido**

`paso_timeline(titulo, badge_texto, rol=None, ...)` recibe `rol` únicamente para el paso cuyo
nombre coincide con `p.estado`, usando el mapeo REAL de la sección 6 (corregido 2026-07-29):
`RECIBIDO=primary` (azul), `ENTREGADO=success` (verde), `CANCELADO=danger` (rojo), y
`ANUNCIADO='anunciado'` — un 5º valor especial (no uno de los 4 roles genéricos) que renderiza
`bg-amber-500 text-amber-950` en vez de reusar `warning` (que ahora es naranja, un color distinto
al ámbar de Anunciado). Para cualquier otro paso, `rol=None` produce automáticamente el
tratamiento gris. `pendiente=True` fuerza la caja punteada sin información (para un paso que
todavía no ocurrió) sin importar qué `rol` se le pase. `ultimo=True` en el último paso omite la
línea conectora hacia abajo.

---

## 13. Alertas / notificaciones — toast (componente cerrado)

**Forma aprobada:** Toast flotante con auto-dismiss. Reemplaza el `<div class="error">`/`<div
class="ok">` que hoy se repite a mano en ~10 plantillas — no empuja el layout, se auto-oculta a
los pocos segundos y también se puede cerrar a mano. Requiere JS mínimo (regla 6: se justifica
porque el auto-dismiss lo exige) — el propio macro emite su `<script>` autocontenido, ninguna
página necesita wirear nada aparte.

Implementación de referencia: `src/app/web/templates/components/_toast.html`
Preview visual: `docs/design-system/previews/toast.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Posición | fija, ancho completo en móvil, tarjeta a la derecha desde `sm:` | `fixed left-3 right-3 sm:left-auto sm:right-4 sm:w-80` |
| **Offset inferior — CRÍTICO** | `bottom-24` (96px), NUNCA `bottom-4` | ver regla de posición abajo |
| Apilamiento | por debajo de modales (z-50), por encima del contenido normal | `z-40` |
| Caja | fondo blanco (contraste sobre cualquier página), sombra elevada | `bg-white shadow-lg border rounded-lg px-4 py-3` |
| Borde por rol | `border-{color}-200` — el mismo color por rol de Badges, no relleno | ver sección 1 |
| Ícono | `text-{color}-600/700` a juego con el borde | `h-5 w-5` |
| Accesibilidad | `warning`/`danger` son urgentes, `primary`/`success` son informativos | `role="alert"` vs `role="status"` |

### Regla de posición — por qué `bottom-24` y no `bottom-4`

`base.html` tiene una barra de navegación inferior **fija** (`.site-footer-mobile`,
`position:fixed; bottom:0`) visible en **todos** los anchos de pantalla, no solo móvil. Desde el
2026-07-29 esa barra mide **80px totales en móvil** (56px de nav con íconos + 24px de línea de
crédito "Desarrollado por JEMAVI | © PAPYRUS", agregada para igualar el footer real de
producción) y **44px en desktop** (≥768px, donde se compacta a una sola fila delgada — crédito a
la izquierda, enlaces inline a la derecha, estilo producción v1). El `<body>` le reserva
`padding-bottom:80px` en móvil y `48px` en desktop. Un toast anclado a `bottom-4` queda literalmente encima de esos botones de navegación
(Anunciar / Buscar / Ayuda / Whatsapp / Teléfono). `bottom-24` (96px) libra la altura de móvil
(80px + 16px de respiro) y con más margen la de desktop (44px) — nunca menos. **Estos dos números están acoplados a
propósito**: si la altura del footer en `base.html` vuelve a cambiar, el offset del toast debe
corregirse en el mismo commit (hay un comentario cruzado en el `<style>` de `base.html` y en
`_toast.html` recordándolo). Cualquier componente flotante futuro que se ancle abajo debe heredar
este mismo offset, no reinventar uno.

### Auto-dismiss + cierre manual, sin dependencias

`toast(mensaje, variant='success', duracion_ms=5000, id='toast-flash')` — `duracion_ms=None`
desactiva el auto-dismiss (el usuario solo lo cierra a mano). Pensado para UN flash message por
carga de página (patrón Post/Redirect/Get ya usado en todo el proyecto) — si algún caso necesita
varios simultáneos, pasar un `id` distinto por instancia.

---

## 14. Modales / confirmación (componente cerrado)

**Forma aprobada:** Centrado siempre — diálogo centrado en cualquier tamaño de pantalla, sin el
bottom-sheet-en-móvil que tenía el modal ad-hoc anterior (`packages/_modal.html`). Ajuste aprobado
en retroalimentación: todo `<select>` dentro de un modal con **menos de 5 opciones** se reemplaza
por un grupo de chips clickeables; con 5 o más, sigue siendo un `<select>` normal.

Implementación de referencia: `src/app/web/templates/components/_modales.html`
Preview visual: `docs/design-system/previews/modales.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Backdrop | negro semitransparente | `bg-black/40` |
| Tarjeta del modal | centrada, radio grande, sombra elevada | `bg-white rounded-2xl shadow-xl p-5` |
| Ancho | `sm` (24rem) por defecto, `md` (28rem) para formularios más cargados | `max-w-sm` / `max-w-md` |
| Alto | limitado con scroll interno si el contenido no entra | `max-h-[85vh] overflow-y-auto` |
| Apilamiento | por encima del toast (z-40, sección 13) | `z-50` |
| Confirmación destructiva | ícono circular + texto centrado, en vez de solo una franja de color | `h-12 w-12 rounded-full bg-{color}-100 text-{color}-600` |

### Contrato de toggle: idéntico al modal ad-hoc ya en producción

`data-open="modal-<id>"` abre, `data-close="modal-<id>"` cierra, vía el mismo JS que ya usan
`packages/list.html` / `admin/staff.html` (`elemento.hidden = false/true`). Se reutiliza el
contrato a propósito — si esas páginas migran a este componente, el JS existente no cambia. Cada
instancia emite su propio `<style>#modal-id[hidden]{display:none}</style>` porque combinar el
atributo `hidden` con una clase `flex` permanente pierde contra la cascada de Tailwind (mismo
problema que ya resolvía a mano `.modal[hidden]{display:none}` en el modal anterior).

### Selects de menos de 5 opciones → chips, no dropdown

`grupo_chips(nombre, opciones, seleccionado=None, variant='primary', etiqueta=None)` — SOLO para
enums fijos de menos de 5 opciones. `opciones` es una lista de tuplas `(valor, texto)`. Cero
JavaScript: `<input type="radio">` real oculto (`sr-only`) + `<label>` estilizado vía
`peer-checked`, navegable por teclado igual que un `<select>` nativo. `variant='danger'` para
grupos dentro de una confirmación destructiva (ej. motivo de cancelación). Listas de tamaño
variable (ej. candidatos de corrección de destinatario, que dependen de cuántas personas coincidan
con un teléfono) NO usan este macro — siguen siendo un `<select>` normal, porque no son un enum
fijo acotado.

---

## 15. Zona de carga S3 — fotos (componente cerrado)

**Forma aprobada:** Arrastrar y soltar. Recuadro punteado grande (clic o drag&drop), tira de
miniaturas removibles debajo, contador "X de {max} fotos usadas". La lógica de dominio no cambia:
`_MAX_FOTOS_POR_PAQUETE = 3` (`paquete_foto_service.py`), subida real vía `S3FotoStorage` — este
componente es solo la capa visual sobre el mismo `<input type="file" multiple>`.

Implementación de referencia: `src/app/web/templates/components/_carga_fotos.html`
Preview visual: `docs/design-system/previews/carga-fotos.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Input real | oculto visualmente, sigue en el árbol de foco | `class="sr-only"` (NO `display:none` ni `hidden`) |
| Zona (label) | recuadro punteado, radio y tokens ya fijados | `rounded-lg border-2 border-dashed border-slate-300 px-4 py-6 text-center` |
| Hover / drag activo | mismo azul primary de foco, sin inventar color | `hover:border-blue-400 hover:bg-blue-50/40` |
| Foco (input oculto recibe Tab) | anillo visible en la caja, no en el input invisible | `focus-within:ring-2 focus-within:ring-blue-300 focus-within:ring-offset-2` |
| Miniatura | cuadrada, recortada | `h-16 w-16 rounded-lg bg-slate-200 overflow-hidden object-cover` |
| Botón quitar (por miniatura) | círculo flotante en la esquina | `absolute -top-1 -right-1 h-5 w-5 rounded-full bg-white shadow border border-slate-200` |

### Progresivo: funciona sin JavaScript, el JS solo mejora

Sin JS, sigue siendo un `<input type="file" multiple>` real asociado a su `<label>` — clic para
elegir archivos funciona nativo y el formulario se envía igual. El `<script>` autocontenido que
emite `carga_fotos(...)` (mismo patrón que `_toast.html`) solo agrega: arrastrar y soltar,
vista previa en miniatura, y poder quitar una foto de la selección antes de enviar — reconstruyendo
el `FileList` vía `DataTransfer` porque `FileList` es inmutable por spec. `max_fotos` es solo una
guía visual del lado del cliente; el límite real lo sigue aplicando
`paquete_foto_service.agregar_foto` en el servidor — este componente no lo reemplaza ni lo duplica.

---

## 16. Búsqueda y filtros (componente cerrado)

**Forma aprobada:** Barra de filtros inline (reskin del filtro real de `/paquetes`), con dos
ajustes de retroalimentación: (1) búsqueda libre + Torre + Apartamento viven en UNA sola barra
unificada, un marco compartido — el foco resalta la barra entera, no cada campo suelto; (2) los
chips de Estado reutilizan la MISMA gama de color por estado ya fijada en Badges (sección 6/7), no
gris neutro genérico. Un solo `<form>`, un solo botón de envío — todo sale de la misma barra en un
solo submit (GET, sin JS/HTMX).

Implementación de referencia: `src/app/web/templates/components/_busqueda_filtros.html`
Preview visual: `docs/design-system/previews/busqueda-filtros.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | tarjeta centrada, mismo ancho que Formularios (sección 10) | `max-w-lg mx-auto bg-white border border-gray-200 rounded-xl shadow-sm p-5` |
| Barra unificada | un solo marco, campos internos sin borde propio | `rounded-lg border border-slate-300 overflow-hidden` + `border-0` en cada `<input>` interno |
| Foco de la barra | en el contenedor completo, no por campo | `focus-within:ring-2 focus-within:ring-blue-300 focus-within:ring-offset-2 focus-within:border-blue-800` |
| Separador entre campos internos | línea fina, no doble borde | `border-l border-slate-200` en cada campo salvo el primero |
| Chip "Todos" (sin filtro) | gris oscuro neutro — nunca se confunde con un estado real | suave `border-slate-300 bg-white text-slate-700`, activo `peer-checked:bg-slate-800` |
| Chip por estado | mismo mapeo REAL que `badge()` (sección 7), versión clickeable | suave = fórmula de Badges corregida, activo (`peer-checked:`) = color sólido correspondiente |

### `filtro_estado` vs `grupo_chips` — por qué son macros distintos

`grupo_chips` (sección 14, componente 9) asume UN rol de color para todo el grupo (todas las
opciones del mismo tono). `filtro_estado(seleccionado)` necesita que CADA opción tenga su propio
color — el mismo mapeo REAL corregido de la sección 6 (Anunciado=ámbar especial, Recibido=azul
`primary`, Entregado=verde `success`, Cancelado=rojo `danger`), igual que usa `badge()` (sección
7), solo que como `<input type="radio">` clickeable en vez de una etiqueta de solo lectura. No se
generalizó un macro único para ambos casos porque las firmas son distintas por diseño (un color
vs. color-por-opción), no por descuido.

---

## 17. Paginación (componente cerrado)

**Forma aprobada:** Numerada con ventana ±2. Anterior, hasta 5 números centrados en la página
actual, Siguiente — mismo patrón que ya existía en `packages/list.html`, reskineado.

Implementación de referencia: `src/app/web/templates/components/_paginacion.html`
Preview visual: `docs/design-system/previews/paginacion.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Enlace/número | — | `rounded-lg border border-slate-300 text-slate-700 px-3 py-1.5 text-sm font-medium hover:bg-slate-50` |
| Página activa | sólido primary, no clickeable | `bg-blue-600 border-blue-600 text-white` + `aria-current="page"` |
| Anterior/Siguiente deshabilitado | gris claro, `<span>` no `<a>` | `border-slate-200 text-slate-300 cursor-not-allowed` + `aria-disabled="true"` |

### Generalización: `params` en vez de filtros hardcodeados

El macro local anterior escribía `estado`/`q`/`torre`/`apartamento` directo en cada link — atado
a `/paquetes` únicamente. `paginacion(pagina_actual, total_paginas, base_url, params=None)` recibe
los filtros a preservar como diccionario, así que sirve para cualquier listado paginado
(`/residentes` sin filtros, `/paquetes` con los 4 suyos, o cualquier otro futuro). No renderiza
nada si `total_paginas <= 1`.

### Nota técnica: `{% set %}` dentro de un `{% for %}` no persiste en Jinja2

Al construir el query string preservado se necesitó `namespace()` (`{% set ns = namespace(qs='')
%}` ... `{% set ns.qs = ns.qs ~ ... %}`) — un `{% set %}` normal dentro de un bucle se resetea en
cada iteración y no sobrevive fuera del `{% for %}`, un gotcha real de Jinja2 (no de Python).
Cualquier componente futuro que necesite acumular un valor dentro de un bucle debe usar el mismo
patrón, no `{% set %}` directo.

---

## 18. Breadcrumbs / nav secundaria (componente cerrado)

**Forma aprobada:** Encabezado contextual con volver integrado — la flecha de volver vive pegada
al título, en la misma línea (patrón de barra de navegación de app móvil nativa), no ocupa una
fila propia. Resuelve un vacío real: `customers_manage/detail.html` no tenía ninguna forma de
volver a la lista de clientes.

Implementación de referencia: `src/app/web/templates/components/_breadcrumbs.html`
Preview visual: `docs/design-system/previews/breadcrumbs.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Botón de volver | ícono solo, cuadrado, mismo tamaño que `accion_icono` (sección 11) | `h-8 w-8 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-blue-600` |
| Título | pegado al botón, misma línea | `flex items-center gap-2` + `text-lg font-bold text-slate-900` |
| Subtítulo (opcional) | debajo, alineado con el título (no con la flecha) | `text-sm text-slate-500 ml-10` |

### `texto_volver` es obligatorio ser específico

El `aria-label` del enlace de volver es literalmente el texto de `texto_volver` — nunca queda en
un "Volver" genérico por defecto sin que quien llama lo piense, porque el ícono de flecha por sí
solo no dice a dónde vuelve ("Volver a Clientes", no "Volver"). `nivel='h1'` por defecto (título
principal de la página); `nivel='h2'` si se anida dentro de una sección más chica.

---

## 19. Empty states (componente cerrado)

**Forma aprobada:** Ícono + texto + acción sugerida. Reemplaza el texto gris genérico que hoy
repiten 4 pantallas distintas (`packages/list.html`, `search/form.html`,
`customers_manage/search.html`, `customer/paquetes.html`) sin distinguir dos situaciones que en
realidad son distintas: una búsqueda/filtro sin coincidencias vs. una lista que genuinamente no
tiene nada todavía.

Implementación de referencia: `src/app/web/templates/components/_estado_vacio.html`
Preview visual: `docs/design-system/previews/empty-states.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | tarjeta centrada | `bg-white border border-gray-200 rounded-xl shadow-sm py-8 px-6 text-center` |
| Ícono | círculo, 48px | `h-12 w-12 rounded-full flex items-center justify-center` |
| Ícono "sin resultados" | gris neutro (`icono='buscar'`, default) | `bg-slate-100 text-slate-400` |
| Ícono "vacío real" | azul primary (`icono='paquete'`) | `bg-blue-50 text-blue-600` |
| Título | — | `text-sm font-semibold text-slate-700` |
| Mensaje | — | `text-sm text-slate-500 mt-1` |
| CTA (solo en "vacío real") | reutiliza el botón primary ya fijado | `bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 shadow-sm` |

### Por qué dos íconos y no uno solo

"Sin resultados" (`buscar`) implica que la acción correcta es ajustar lo que el usuario ya
escribió — nunca lleva botón, porque no hay a dónde navegar, solo a qué volver a intentar. "Vacío
real" (`paquete`) implica que todavía no existe nada y casi siempre se acompaña de
`boton_texto`/`boton_href` apuntando a la acción que llena ese vacío (ej. Anunciar un paquete) —
mezclar ambos casos bajo un solo ícono/mensaje neutro (como hacía el texto gris genérico anterior)
le hacía perder al usuario la pista de qué hacer a continuación.

---

## 20. Estados de carga / skeleton (componente cerrado — último de los 15)

**Forma aprobada:** Spinner centrado simple. Un solo spinner + texto en el centro del área que
está cargando, sin imitar la forma del contenido real — un solo macro sirve para cualquier
contexto (tarjeta, tabla, página completa). Hoy el único estado de carga real en el sitio es el
spinner de botón (sección 5); este componente es para cuando una vista futura sí tenga datos que
tarden en llegar del lado del cliente.

Implementación de referencia: `src/app/web/templates/components/_estado_carga.html`
Preview visual: `docs/design-system/previews/skeleton.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Contenedor | centrado vertical y horizontal, alto configurable | `flex flex-col items-center justify-center gap-2` |
| Ícono | mismo spinner SVG de `boton(loading=True)` — no uno nuevo | `animate-spin h-6 w-6 text-blue-600` |
| Texto | — | `text-sm text-slate-400` |
| Accesibilidad | anuncia el cambio sin interrumpir | `role="status" aria-live="polite"` |

`alto` (default `'h-40'`) fija la altura mínima del contenedor para que el spinner quede centrado
dentro del espacio real que va a ocupar el contenido cuando llegue, evitando un salto de tamaño al
reemplazarlo.

---

## 21. Confirmación de anuncio (componente cerrado — componente 16, agregado durante la migración)

**Forma aprobada:** "Recibo con código destacado". Tarjeta centrada con ícono de éxito (círculo
`emerald`, mismo check que usaría un toast `success`), título, subtítulo opcional, y el código de
acceso en un bloque propio con borde punteado azul — 4 caracteres con `tracking-[0.35em]`, porque
es el único dato que la persona necesita anotar de toda la pantalla. No existía en los 15
originales: ninguno cubría una "página de éxito" completa. Se cerró el 2026-07-30 al migrar
`announce/confirmacion.html`, la última plantilla real sin el tema.

Implementación de referencia: `src/app/web/templates/components/_confirmacion.html`
Preview visual: `docs/design-system/previews/confirmacion.html`

| Token | Valor | Clase Tailwind |
|---|---|---|
| Ícono de éxito | mismo rol `success` de Badges/Toast | `bg-emerald-100 text-emerald-600`, círculo `h-12 w-12` |
| Bloque de código | fondo suave `primary`, borde punteado | `rounded-xl border-2 border-dashed border-blue-200 bg-blue-50` |
| Texto del código | grande, muy espaciado, `primary` | `text-4xl font-bold tracking-[0.35em] text-blue-800` |
| Tarjeta | mismo lenguaje que Modales (`rounded-2xl`, no el `rounded-xl` del resto) | `bg-white border border-gray-200 rounded-2xl shadow-sm` |

El macro `confirmacion_exito(titulo, subtitulo=None, codigo=None, etiqueta_codigo='Código de
acceso')` solo define la cáscara fija — la recapitulación de datos y los enlaces de acción se
inyectan vía `{% call %}` porque varían por página (número de campos, hrefs) y hoy solo hay un
caso de uso real. `codigo=None` omite el bloque completo, para no atar el macro a paquetes
específicamente si mañana hace falta una confirmación de éxito sin código. `fila_dato(etiqueta,
valor)` es un helper opcional para las filas de la recapitulación.

---

## Design system completo — migración completa

Los 16 componentes de `docs/design-system/README.md` están cerrados: Botones, Badges, Inputs,
Tarjetas, Formularios, Tablas, Timeline, Toast, Modales, Carga de fotos, Búsqueda y filtros,
Paginación, Breadcrumbs, Empty states, Estados de carga, y Confirmación de anuncio. Cada uno tiene
su macro en `src/app/web/templates/components/_*.html`, su preview aprobado en
`docs/design-system/previews/`, y su entrada en este documento. Al 2026-07-30, además, **todas
las plantillas reales del rebuild ya usan estos componentes** — la migración página por página
documentada en `IMPLEMENTACION.md` sección 5 terminó con esta última pantalla.

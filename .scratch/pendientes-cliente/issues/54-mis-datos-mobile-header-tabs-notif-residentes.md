# 54 — `/mis-datos`: quitar encabezado con avatar, tabs en grid mobile, tarjetas de Notificaciones, fix overflow en Residentes

**Pedido original (cliente):** "para la vista de '/mis-datos', para iniciar,
de que forma me puedes colaborar removiendo la seccion correspondiente a
'flex items-center gap-3 mb-4' que incluye el nombre de 'JESUS MARIA
VILLALOBOS BULA' y una especie de logo con una 'J'. Adicional a esto para
la version movil de que forma puedes hacer que los tabs de 'Datos,
Notificaciones, Apartamento y Residentes' se pueda ver de una mejor manera
[...] En esta misma vista, la seccion de 'Notificaciones' muestra una
tabla [...] no se muestra toda la tabla y hay que hacer scroll. En la
seccion de 'Residentes' [...] el campo 'telefono' tiene una especie de
overflow en la pantalla, este campo se sale de la pantalla."

**Status:** implementado

## Contexto

Se presentaron alternativas para cada uno de los 3 problemas de UX (tabs,
tabla de notificaciones, overflow del campo teléfono) vía `AskUserQuestion`
con mockups ASCII — el cliente eligió la opción recomendada en los 3 casos.
Archivo único: `app/web/templates/customer/verify.html`.

## Implementación

**1. Encabezado con avatar "J" + nombre** — eliminado por completo (era un
bloque autocontenido, `flex items-center gap-3 mb-4`). Queda solo el título
"Mis datos".

**2. Tabs en mobile** — el bug real: `flex-1` (ancho igual) +
`whitespace-nowrap` (prohíbe salto de línea) compitiendo entre sí, así que
"Notificaciones" se apretaba/cortaba en pantallas angostas. Mismo patrón
que usa `/mis-paquetes` (no tocado en este pedido, pero vale la pena
replicar el fix ahí después). Fix: grid 2x2 en mobile (`grid grid-cols-2`),
fila única en desktop (`lg:flex`) — los 4 tabs se ven de una vez sin scroll
ni recorte.

**3. Tabla de Notificaciones** — el `<table>` forzaba `min-w-[420px]`, más
ancho que cualquier celular, de ahí el scroll horizontal obligatorio.
Reemplazado por un layout responsivo SIN duplicar los `<input>`: cada fila
(evento) es un mismo `<div>` que se acomoda distinto según el viewport —
`flex flex-wrap` (tarjeta apilada) en mobile, `lg:grid` (columnas
alineadas, se ve como la tabla de siempre) en desktop. Es el mismo
conjunto de checkboxes en los dos casos — nunca hay dos `<input>` con el
mismo `name`, así que no hay riesgo de que el formulario mande valores
contradictorios entre el layout mobile y el desktop (evaluado y
descartado a propósito un enfoque con dos bloques duplicados +
habilitar/deshabilitar por JS, por el riesgo de que ambos conjuntos de
checkboxes queden desincronizados).

**4. Overflow del campo "Teléfono" en "Agregar un nuevo Residente"** — bug
de flexbox: dos `<input flex-1>` sin `min-w-0` no pueden encogerse más allá
del ancho de su contenido, así que en pantallas angostas empujan el layout
fuera de la pantalla. Mismo fix ya usado en `announce_new/form.html` para
este mismo par de campos (Nombre + Teléfono): agregar `min-w-0`. Aplicado
también a los otros dos campos de teléfono del mismo panel (Actualizar /
Agregar teléfono de un Ocupante existente) por consistencia — mismo bug,
mismo panel, no fue pedido explícitamente pero es el mismo arreglo ya
decidido aplicado a sus pares idénticos.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- `tests/web/test_customer_verify.py`: 45/45.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Clases de Tailwind (incluida la columna de grid con valor arbitrario
  `grid-cols-[1fr_repeat(4,minmax(0,1fr))]`) verificadas contra un rebuild
  local de `tailwindcss` — se generan correctamente. El CSS compilado no
  se commitea a mano: el Dockerfile corre `npm run build:css` en cada
  build de deploy, así que se regenera solo.
- Pendiente: confirmar en `test.papyrus.com.co`, en un dispositivo móvil
  real, que los 4 tabs se ven sin recorte, que la tabla de Notificaciones
  ya no necesita scroll horizontal, y que el campo Teléfono de "Agregar un
  nuevo Residente" ya no se sale de la pantalla.

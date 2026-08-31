# 274 — Overflow en mobile: contenido se sale del contenedor (modales y tarjetas)

**Pedido original (cliente):** "veo que algunos modales y en general
algunas secciones como por ejemplo 'Eliminar residente' no mantiene el
texto dentro del tamaño del contenedor reservado para esto, el
contenido aquí presente se sale del contenedor y no es visible, puedes
analizar inicialmente los modales para corregir esto y también analiza
las secciones cuando se pasan a mobil para que esto no pase o sea
controlado."

**Status:** implementado

## Diagnóstico

Sin navegador conectado esta sesión -- análisis estático de código, no
visual. Se revisó `components/_modales.html` completo (`modal()` y
`modal_confirmacion()`, las dos únicas fuentes de TODOS los modales de
la app) -- ningún texto dinámico vive ahí dentro de una fila `flex`
compitiendo por espacio con un sibling sin poder encoger (el título de
`modal_confirmacion` y el mensaje son bloque simple, con wrap normal;
el título+✕ de `modal()` sí es una fila `flex justify-between`, pero
sin un caso concreto reportado ahí).

La causa real encontrada, específica al ejemplo dado ("Eliminar
residente"): esa tarjeta existe en DOS vistas -- `/residentes` (staff,
`customers_manage/detail.html`) y `/mis-datos` (cliente,
`customer/verify.html`). El lado STAFF recibió una tanda completa de
arreglos de overflow en esta misma sesión (issues 253/254/255/264/265:
`min-w-0`+`truncate` en el nombre, chips que dejaron de tener texto
largo, apilado `flex-col` en mobile) -- pero **esos arreglos nunca se
portaron a `/mis-datos`**, que sigue con el patrón viejo:

- `<p class="font-medium text-slate-900 text-sm">{{ ocupante.nombre }}</p>`
  sin `truncate`, sin `min-w-0` en su `<div>` envolvente.
- Los chips de acción (✅ Confirmar / ❌ Eliminar-Rechazar) llevan
  TEXTO visible (`chip_accion`, no el `chip_icono` compacto que ya usa
  `/residentes`) en una fila `flex items-center justify-between` SIN
  `flex-col` en mobile ni `flex-wrap` en esa fila puntual -- en un
  viewport angosto, nombre + 2 chips de texto no caben en una sola
  línea, y sin encoger ni apilar, algo queda fuera del contenedor.

## Alcance (fix scoped, no un rediseño completo)

Port MÍNIMO del patrón ya probado en `/residentes` a esa misma fila de
`/mis-datos` -- no el rediseño completo a iconos (`chip_icono`), que
sería un cambio más grande y no fue lo pedido (el pedido es "que no se
salga del contenedor", no una paridad visual total):

1. `min-w-0` en el `<div>` del nombre + `truncate` en el `<p>`.
2. La fila nombre+badge vs. chips pasa a `flex-col sm:flex-row
   sm:items-center sm:justify-between` (mismo breakpoint/patrón que
   issue 264 en `/residentes`) -- en mobile se apila, desde `sm:`
   vuelve a una sola fila.
3. `flex-wrap` agregado a la fila de chips Confirmar/Eliminar (la
   segunda fila, Promover/Editar/Notificaciones, ya lo tenía).

## Seguimiento (mismo día): causa real en los modales

El cliente marcó que el punto de los MODALES seguía sin corregirse
después de la primera tanda (`min-w-0`/`break-words` en título y
mensaje) -- la causa real era otra: `overflow-y-auto` estaba fijado
pero `overflow-x` nunca se fijaba explícitamente (default `visible`).
Cualquier contenido adentro que no encogiera/envolviera bien podía
salirse visualmente por los bordes redondeados de la caja hacia el
fondo oscuro de atrás -- exactamente "se sale del contenedor y no es
visible". Fix de raíz: `overflow-x-hidden` agregado a la caja de AMBOS
macros (`modal()` y `modal_confirmacion()`) -- cierra el problema sin
importar qué combinación de contenido dinámico traiga cada instancia,
independiente de los arreglos de `min-w-0`/`break-words` (que siguen
ahí como capa adicional para que el texto ENVUELVA en vez de necesitar
recortarse).

## Verificación

- Suite completa (`tests/web` + `tests/data_model`): 1259 passed (antes
  de agregar `overflow-x-hidden`, cambio puramente aditivo de CSS sin
  riesgo). Re-verificado después: `test_customer_verify.py` +
  `test_customers_manage.py`: 217 passed.
- Verificado en vivo: `overflow-x-hidden` presente 5 veces en la ficha
  de `/residentes` (una por cada modal renderizado en esa página); en
  `/mis-datos` (login real por OTP), la fila de cada residente
  confirma `min-w-0`, `truncate`, y `flex-col sm:flex-row
  sm:items-center sm:justify-between` -- 5 ocurrencias cada uno.

## Seguimiento #2 (mismo día): "Eliminar residente" en la LISTA de /residentes

El cliente reportó que un modal puntual (`modal-eliminar-{persona_id}`)
seguía con el mismo problema pese a lo de arriba -- resultó ser una
vista DISTINTA a la ficha (`customers_manage/_resultados.html`, la
LISTA/resultados de búsqueda de `/residentes`, no la ficha individual)
que nunca se había revisado. Confirmado server-side que SÍ servía
`overflow-x-hidden` (viene del mismo macro compartido), así que el CSS
del modal en sí ya estaba bien -- la causa estructural real: el modal
(`position:fixed`) vivía DENTRO del `<table>`, que a su vez vive dentro
de un `<div class="overflow-x-auto">` (scroll horizontal de la tabla en
mobile). Un `fixed` anidado en un contenedor con su propio scroll es
una combinación conocida de comportamiento inconsistente entre
navegadores.

Fix: los 48 modales `modal-eliminar-*` de esa lista se sacaron
COMPLETO de adentro de `<table>`/`overflow-x-auto` -- mismo bucle sobre
`resultados`, pero renderizado DESPUÉS de cerrar ese wrapper, para que
queden anclados al viewport sin depender de ningún ancestro con scroll
propio. Verificado: 0 instancias de `id="modal-eliminar-"` quedan
dentro de `<table>...</table>` en el HTML servido (antes eran 48/48).
Suite `test_customers_manage.py`: 151 passed.

Nota: el navegador se reconectó durante esta misma conversación --
verificado VISUALMENTE (viewport móvil 390x844) contra
`/residentes` (lista) y `/residentes/{id}` (ficha): el modal "Eliminar
residente" en ambas vistas renderiza contenido, sin desbordar, texto
completo. Confirmado también en vivo que ningún dato real se tocó
durante la verificación (se abrió y cerró el modal sin confirmar la
acción).

Hallazgo aparte (no es un bug de PaqueteX): durante la verificación,
varios clicks físicos simulados no llegaban al botón -- resultó ser
una extensión de Chrome del propio navegador (`bit-notification-bar-
root`, probablemente un gestor de contraseñas tipo Bitwarden)
inyectando un elemento que interceptaba el click en esa posición.
Nada que corregir del lado de la app.

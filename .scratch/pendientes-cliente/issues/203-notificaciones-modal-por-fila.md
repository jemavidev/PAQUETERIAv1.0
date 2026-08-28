# 203 — `/administracion/notificaciones`: cada fila abre en modal, no acordeón

**Pedido original (Jesús, en sesión):** primero preguntó "posibilidades de
combertir las opciones de esta vista /administracion/notificaciones a
modales cada una, de esta forma vea mejor". Tras explicarle el trade-off
(ancho del macro `modal()` vs. la vista previa de Email, pérdida del flujo
"editar varias seguidas sin cerrar nada") confirmó: "lo que necesito es que
cada opcion se abra con un modal, puedes hacerlo" — sin pasar por
`?variant=` esta vez, pidió el reemplazo directo.

**Status:** implementado

## Contexto

Construye sobre [[200-notificaciones-layout-acordeon]]: esa vez se
prototiparon 3 layouts en vivo y el cliente eligió acordeón (`<details>`,
una fila abierta a la vez, cero JS). Este pedido reemplaza ESE acordeón por
el macro `modal()` ya existente en `components/_modales.html` (mismo
contrato `data-open`/`data-close` que usan `admin/staff.html` y
`packages/_resultados.html`).

## Implementación

- `components/_modales.html`: el macro `modal()` solo definía anchos
  `sm`/`md` (hasta 448px) — se agregó `lg` (`max-w-2xl`, 672px, el mismo
  ancho que ya tenía el contenedor de esta página) porque el preview de
  Email es un iframe de 420px de alto que no cabía en `md`.
- `admin/notificaciones.html`: la lista principal pasa de 8 `<details>`
  siempre-en-la-página a 8 botones compactos (evento/motivo + chevron) que
  abren `data-open="modal-notif-N"`. El contenido interno (pestañas de
  canal, forms, preview de Email) es el mismo de siempre, solo cambió el
  contenedor exterior — igual que hizo el issue 200 con el acordeón.
- Default: TODOS los modales cerrados al cargar la página (a diferencia del
  acordeón, que forzaba la primera fila abierta para que la página no
  arrancara 100% colapsada — con una lista compacta de botones eso ya no
  hace falta, se ve todo de un vistazo). Igual que antes, la fila con un
  error de validación propio o que se acaba de guardar abre su modal
  automáticamente (`abierto=es_fila_error or es_fila_guardada`, mismo
  criterio que ya usaban `agregar-usuario` en staff.html y varios modales de
  `_resultados.html`).
- Se quitó `name="notif-acordeon"` (agrupación nativa de `<details>` para
  que abrir uno cerrara los demás) — no aplica a modales: cada uno es
  independiente, y solo puede haber UNO con `abierto=True` a la vez de
  todas formas (error o guardado exitoso nunca coinciden en la misma
  respuesta).
- Script de toggle inline al final del archivo (mismo patrón que
  `customers_manage/search.html`: un solo listener delegado en `document`
  con `closest('[data-open]')`/`closest('[data-close]')`, en vez de un
  listener por botón).

## Verificación

- Tests actualizados en `tests/web/test_admin_notificaciones.py`: los 4
  tests específicos de `<details>`/acordeón se reescribieron para modal
  (`hidden` en vez de `open`); se quitó el test de agrupación `name`
  compartido (ya no aplica). El resto (21 tests de contenido/guardado) sigue
  pasando sin tocarlos.
- Verificado en vivo contra el servidor de dev local.

## Pendiente

- Deploy a test.papyrus.com.co.

# 318 — "Agrupar por apartamento" se activa solo al escribir "apt<número>"

**Pedido original (cliente):** en `/residentes`, si escribís "apt302" (o cualquier número de
apartamento con ese esquema) en la barra de búsqueda, el botón "Agrupar por apartamento" se debe
activar SOLO -- sin tener que clickearlo aparte -- para llegar en un solo paso al grid fijo de 10
Torres de issue 317. Debe funcionar así para cualquier número.

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-05, commit `bcac30d`) --
pendiente que el cliente lo confirme visualmente (extensión de Chrome confirmada NO conectada en
esta sesión -- no se pudo probar el comportamiento de JS en un navegador real, solo revisión de
código + smoke test de que la página sigue cargando bien).

## Implementación

Puramente JS, en `_busqueda_filtros.html` (sin cambios de backend/Python -- issue 317 ya hace
todo el trabajo pesado). El listener `input` del campo `q` (solo en callers con `vistaInput`,
osea `/residentes`) chequea el texto actual contra el MISMO esquema `apt<número>` que ya usa el
backend (`_ESQUEMA_APARTAMENTO_RE` en customers_manage.py, replicado acá como regex JS
`/^apt\s*\d+$/i`) -- si matchea, fuerza `vista=agrupado`.

`vistaActivadaAuto` (flag local) distingue "lo activó este atajo" de "el staff lo activó a
mano" -- clickear cualquier botón de vista (o "Quitar filtros") apaga la bandera, así que un
click manual NUNCA se pisa por este atajo. Si el auto-activó y el texto DEJA de matchear
"apt<número>" (se borra o se escribe otra cosa), vuelve a apagar "Agrupar" solo -- comportamiento
simétrico, para no dejar el botón activado "pegado" tras una búsqueda de apartamento que ya no
está.

## Sin verificación en vivo

No hay forma de probar comportamiento de JS con pytest (los tests de este proyecto solo
verifican HTML server-renderizado) ni con curl -- se revisó la lógica a mano trazando varios
escenarios (tipeo progresivo "a"->"apt302", borrar hasta salir del esquema, click manual de
"Principales" mientras hay un número de apartamento en el campo) pero falta la confirmación
visual real del cliente.

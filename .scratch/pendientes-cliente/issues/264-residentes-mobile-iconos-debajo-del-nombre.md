# 264 — `/residentes` tab Residentes, mobile: iconos de acción debajo del nombre

**Pedido original (cliente):** "para la vista movil de /residentes en
el tab de Residentes los iconos deberian ir debajo del nombre del
residente."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html`, roster de la tab Residentes -- la fila
de cada tarjeta (`flex flex-wrap items-center justify-between gap-2`)
hoy solo envuelve por `flex-wrap` cuando los iconos no caben, pero el
nombre (`min-w-0 truncate`) se encoge primero -- en mobile los iconos
terminan apretados junto al nombre en vez de bajar a su propia línea.

Mismo problema que ya se había resuelto una vez (issue 253, revertido
en 255 cuando los iconos pasaron a ser compactos) -- ahora que hay más
iconos posibles por fila (issue 263 sumó Confirmar/Rechazar/Editar para
Ocupantes sin contacto), vuelve a hacer falta. Cambio: `flex-col
sm:flex-row sm:items-center sm:justify-between` en la fila -- en mobile
(`<sm`), el bloque de iconos baja a su propia línea debajo del nombre;
desde `sm:` (640px) en adelante, vuelve a ser una sola línea inline
como está hoy.

## Verificación

Suite completa `test_customers_manage.py`: 150 passed (ningún test
depende de las clases exactas de esta fila). Sin navegador conectado
esta sesión -- verificado por análisis estático: la clase `flex flex-col
sm:flex-row sm:items-center sm:justify-between gap-2` se confirmó
renderizada en vivo (curl contra `/residentes/c75f7cdd-...`, dev
local). No se pudo confirmar visualmente en un viewport móvil real.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

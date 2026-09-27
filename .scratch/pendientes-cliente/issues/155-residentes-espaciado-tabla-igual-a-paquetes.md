# 155 — `/residentes`: espaciado de la tabla de resultados igual a `/paquetes`

**Pedido original:** "vamos a trabajar en la vista /residentes, primero veo que los espacion en
la lista que aparece en esta vista no es similar a la de los paquetes por ejemplo, veo que esta
esta mas compacta, la idea es que el look and feel sea similar, puedes corregir esta lista"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Diagnóstico

`customers_manage/search.html` (tabla de resultados de `/residentes`) usaba `px-3 py-2` en cada
`<th>`/`<td>`. `packages/_resultados.html` (tabla de `/paquetes`) usa `px-4 py-2.5` en las suyas —
mismo layout de tabla (`overflow-x-auto rounded-lg border border-slate-200`, `divide-y
divide-slate-100`, header `bg-slate-50 text-xs uppercase`), pero con menos padding interno en
`/residentes`, de ahí la sensación de "más compacta".

## Cambio

`px-3 py-2` → `px-4 py-2.5` en las 4 columnas del `<thead>` y las 4 celdas del `<tbody>` de
`customers_manage/search.html`. Sin tocar los badges internos ("Auto"/"Principal", `px-2 py-0.5`)
ni la estructura de la tabla — solo el padding de celda, para igualar el aire vertical/horizontal
de `/paquetes`.

## Verificación

Verificado en vivo contra `localhost:8010` (recarga en caliente de plantilla, sin reinicio de
servidor necesario): las 4 celdas de encabezado de `/residentes` traen `px-4 py-2.5` en el HTML
servido.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

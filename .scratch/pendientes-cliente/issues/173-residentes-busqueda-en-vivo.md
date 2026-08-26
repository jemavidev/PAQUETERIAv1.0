# 173 — `/residentes`: búsqueda en vivo (autocompletado), como `/paquetes`

**Pedido original:** "necesito que en esta barra de busqueda se implemente el auto completado
donde vaya coincidiendo todo" → aclarado con pregunta de opción múltiple: el cliente eligió
"Búsqueda en vivo (como /paquetes)" -- al escribir, la TABLA de abajo se actualiza sola
(fetch + debounce ~300ms) con los residentes que coinciden, sin recargar la página ni tocar
Enter. Descartada la otra opción ofrecida (dropdown de sugerencias flotante) -- no existe hoy en
ningún buscador del proyecto y hubiera sido una interacción nueva.

**Status:** implementado

## Cambio

- `customers_manage/search.html` → `customers_manage/_resultados.html`: se extrae el bloque de
  paginación + tabla + estados vacíos a un fragmento nuevo, mismo patrón que
  `packages/_resultados.html` (`.scratch/paquetes-busqueda-viva`, ticket 03) -- se puede devolver
  SOLO (sin el layout completo) en la petición fetch en vivo.
- `customers_manage.py` (`customers_manage_search`): nueva `_peticion_en_vivo(request)` (mismo
  mecanismo que ya usa `packages.py` -- header `X-Requested-With: fetch`), decide entre
  `search.html` (carga normal) y `_resultados.html` (fetch en vivo). Mismo contexto para ambas
  plantillas, sin bifurcar.
- `search.html`: `busqueda_filtros(...)` ahora pasa `resultados_id='resultados-residentes'`,
  activando el JS de `_busqueda_filtros.html` (fetch + debounce ~300ms + `AbortController`,
  mismo mecanismo que `/paquetes`, no hay JS nuevo que escribir). El fragmento vive en
  `<div id="resultados-residentes">`.
- `search.html`: el toggle de `data-open`/`data-close` del modal "Eliminar residente" pasa de
  bindeado directo (`querySelectorAll` + `addEventListener` una sola vez al cargar) a delegado
  sobre `document` (mismo patrón que `components/_recibir_paquete.html` ya usa para `/paquetes`)
  -- un `<script>` inyectado por `innerHTML` nunca se ejecuta, así que un binding directo se
  perdía en cada actualización en vivo.
- `components/_busqueda_filtros.html`: comentario de cabecera actualizado -- ya no es cierto que
  "`/residentes` usa su propio form inline" (issue 172 lo unificó) ni que solo `/paquetes` activa
  `resultados_id`.
- `components/_paginacion.html`: comentario del bug de la píldora mobile actualizado -- ya no es
  cierto que "`/residentes` no lo sufre (su búsqueda es un form normal)"; ahora comparte el mismo
  fix genérico (`window.paqueteXInicPaginacionFlotante`, re-llamado tras cada `innerHTML`).

## Verificación

- 3 tests nuevos en `test_customers_manage.py`, mismo patrón que
  `test_peticion_en_vivo_devuelve_solo_el_fragmento` de `test_packages.py`: carga normal trae
  `<h1`/`<html`, el fetch con `X-Requested-With: fetch` trae solo el fragmento; el fragmento
  respeta `q`; el fragmento en vivo sigue trayendo el toggle de "Eliminar residente" (ADMIN).
- Suite completa: 289/289 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`) con curl (header `X-Requested-With: fetch`): carga
  normal vs. fragmento, filtro con resultados, filtro sin resultados ("Sin resultados"), y el
  modal "Eliminar residente" presente en el fragmento en vivo.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

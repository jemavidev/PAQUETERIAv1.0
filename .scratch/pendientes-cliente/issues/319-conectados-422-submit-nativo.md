# 319 — Error 422 al presionar Enter en la barra de búsqueda de /paquetes

**Pedido original (cliente):** "Veo que al escribir algo en la barra de busqueda de la vista
/paquetes este dato se filtra de inmediato, pero si presiono enter aparece algo asi como esto
`{"detail":[{"type":"bool_parsing","loc":["query","conectados"],...}]}`".

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-05, commit `bcac30d`) --
pendiente que el cliente lo confirme visualmente (extensión de Chrome confirmada no conectada en
esta sesión). Reproducido y corregido contra el servidor real.

## Diagnóstico

`busqueda_filtros()` deja un `<button type="submit" class="sr-only">` a propósito, para que Enter
funcione como fallback nativo del navegador CON o SIN JavaScript (ver docstring del macro). La
búsqueda en vivo normal (mientras se escribe) pasa por `fetch()` en JS, que arma la URL a mano y
OMITE `conectados` cuando su valor está vacío -- pero el submit NATIVO (Enter) manda TODOS los
campos del form tal cual, incluido el `<input type="hidden" name="conectados" value="">`
(vacío cuando el toggle está apagado) -- llega `conectados=` (presente, vacío) al backend.

`packages_list()` (`packages.py`) declaraba `conectados: bool = False` -- Pydantic v2 rechaza la
cadena vacía `""` como `bool` con un 422, aunque `False`/ausente sí funcionaban bien. Reproducido
tal cual contra el servidor real: `q=jesus&estado=&conectados=` -> 422 antes del fix, 200 después.

## Fix

`conectados: str = None` en la ruta (en vez de `bool`), con conversión manual
`conectados_activo = conectados == "true"` -- acepta `""`/`None`/cualquier cosa que no sea
literalmente `"true"` como "apagado", igual que ya lo interpreta el propio HTML
(`value="{{ 'true' if conectados_actual else '' }}"`). 2 tests nuevos reproducen el submit nativo
exacto (`estado=`, `conectados=` vacíos) y confirman que `conectados=true` sigue activando el
modo. Suite completa en verde.

## Nota para el futuro

Cualquier query param FastAPI tipado `bool` que se alimente de un `<input type="hidden"
value="">` (el patrón que usa esta app para togles binarios) es vulnerable al mismo bug si algún
día se agrega un nuevo toggle así -- revisé el resto de la app (`grep ": bool = "` en
`src/app/web/routes/`) y `conectados` era el único caso real expuesto a un submit nativo de
formulario; los demás `bool` son parámetros internos de funciones Python (no query params) o
dependencias inyectadas (`Depends(...)`), no vulnerables a esto.

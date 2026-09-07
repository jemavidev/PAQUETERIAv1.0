# 02 — Carga diferida (lazy) del historial en el modal "Ver" de `/paquetes`

**Status:** implementado y verificado localmente. Solo localhost -- no desplegado a
test.papyrus.com.co (pedido explícito del cliente: "implementa en localhost").

## Origen

Pedido del cliente (2026-09-06), en el mismo hilo de la optimización de búsqueda (issue 01), pero
un problema distinto: percepción de lentitud en `/paquetes` **en localhost**, más marcada en móvil
-- "la página realiza todas las consultas pertinentes y luego, después de consultar, es que se
muestra el footer, dando una apariencia de lentitud al cargar la vista." Pidió explorar que el
header/footer carguen primero y los datos después (shell-first), evaluar si eso se puede unificar
entre vistas, y una opinión sobre un enfoque "lazy query".

## Diagnóstico

El HTML inicial de `/paquetes` incluye, para cada una de las 20 filas de la página, el modal "Ver"
completo -- y dentro de ese modal, el timeline de historial completo del paquete (armado por
`timelines_de_paquetes`, llamado una vez para todo el batch antes de renderizar). Ese contenido casi
nunca se necesita en la carga inicial: el modal solo se abre cuando el staff hace clic en "Ver" de
una fila puntual (o, más raro, vía deep-link `?ver=<id>`).

Contra la base de dev local: el payload de `/paquetes` (20 filas) pesaba ~1.08 MB, con el timeline
de historial representando la porción dominante del contenido por fila en el escenario medido.

## Alcance elegido (opción 2 de las discutidas con el cliente)

Reusar el patrón de fetch-fragment que ya existe en el repo (`X-Requested-With: fetch`, usado por
`/announce` y otros) en vez de introducir un mecanismo nuevo. Se descartó diferir la carga de TODA
la lista (`_listar()` completo) porque:

- Rompía 103 tests que asumen contenido completo en la respuesta inicial de `GET /paquetes`.
- El costo real que el cliente reportó como molesto es específicamente el peso del modal "Ver", no
  el listado en sí -- el header/footer sí se sirven junto con el listado en la misma respuesta HTML
  (no hay una petición de red separada de por medio que los bloquee; la sensación de lentitud es de
  tiempo-a-primer-render en el navegador, dominado por el tamaño total del documento a parsear).

Se acotó el fix a diferir SOLO el historial dentro de cada modal "Ver", que es la porción de peso
identificada y evitable sin tocar la semántica de búsqueda/paginación/filtros.

## Implementación

- `app/web/routes/packages.py`: se quitó la llamada batch a `timelines_de_paquetes(db, paquetes)`
  en `_listar` (ya no se resuelve el historial de las 20 filas en cada carga). Nueva ruta:

  ```python
  @router.get("/paquetes/{paquete_id}/timeline", response_class=HTMLResponse)
  def paquete_timeline(paquete_id, request, db, staff):
      paquete = _get_paquete_o_404(db, paquete_id)
      return templates.TemplateResponse(
          "packages/_timeline_fragment.html",
          {"request": request, "timeline": timeline_de_paquete(db, paquete)},
      )
  ```

- `packages/_ver_timeline.html` (nuevo): macro `historial_paquete(timeline)` con el HTML de
  historial extraído tal cual (mismo markup, mismas clases) de donde vivía inline en
  `_resultados.html`.
- `packages/_timeline_fragment.html` (nuevo): plantilla delgada que solo invoca esa macro -- es lo
  que responde el endpoint nuevo.
- `packages/_resultados.html`: el bloque de historial inline se reemplaza por un placeholder
  (`#timeline-diferido-<id>`) con un esqueleto (`animate-pulse`), sin contenido real.
- `components/_recibir_paquete.html` (JS del modal, ya presente y compartido por todas las filas):
  - `cargarTimelineDiferido(paqueteId)`: si el contenedor no se ha cargado ya
    (`dataset.cargado`), hace `fetch('/paquetes/<id>/timeline', {headers: {'X-Requested-With':
    'fetch'}})` y reemplaza el `innerHTML` del placeholder con la respuesta.
  - Se dispara al abrir el modal "Ver" (dentro del handler delegado de clic ya existente, detectando
    `data-open="modal-ver-<id>"`).
  - También se dispara para cualquier modal "Ver" que nazca ya abierto (deep-link `?ver=<id>`,
    escaneado al cargar el script).
  - Fallback de red: mensaje de error simple, sin clase de color (evitar colisión de texto con la
    clase de advertencia real de "destinatario mudado" que vive en el mismo fragmento -- ver
    "Errores encontrados" abajo).

## Errores encontrados durante la implementación (y cómo se resolvieron)

1. **Intento inicial demasiado amplio**: la primera versión difería la carga de TODA la lista de
   paquetes (no solo el historial del modal), rompiendo 103 tests que esperaban contenido completo
   en la respuesta inicial de `/paquetes`. Se revirtió (`git checkout --` sobre `packages.py` y
   `list.html`) y se acotó el alcance al historial del modal únicamente.
2. **Revert colateral**: ese `git checkout --` también deshizo, sin querer, el fix de la issue 01
   (`condiciones_busqueda_paquetes(db, ...)` en los call-sites de `packages.py`), reintroduciendo la
   firma vieja de 2 argumentos y causando `TypeError` en ~30 tests de búsqueda. Se reaplicó
   manualmente.
3. **Colisión de string en test helper**: el mensaje de fallback de red incluía la clase
   `text-red-600` (y, en un segundo intento, la mencionaba en un comentario JS) -- coincide
   literalmente con la clase real que usa `_resultados.html` para la advertencia de "destinatario
   que ya se mudó" (issue 307). El helper de test `_segmento_modal()` cae al final del documento
   cuando no hay otro modal después, así que barría ese string compartido y producía un falso
   positivo en `test_direccion_normal_si_destinatario_sigue_en_la_misma_unidad`. Se resolvió
   quitando la clase de color del fallback (y de cualquier comentario que repitiera el string
   literal).

## Verificación

- `tests/web/test_packages.py`: 217/217 en verde (incluye 3 tests actualizados para pedir el
  historial vía el nuevo endpoint en vez de esperarlo inline).
- `tests/web/test_announce.py`, `tests/data_model/test_ocupante_service.py`,
  `tests/data_model/test_announce_paquete.py`, `tests/web/test_customers_manage.py`: 363/363 en
  verde (suites relacionadas al mismo módulo de paquetes/timeline).
- Suite completa del repo: **1450/1450 en verde**.
- Verificación manual contra el servidor de dev local (`localhost:8010`, login como
  `info@papyrus.com.co`), vía `curl` (sin navegador conectado en esta sesión):
  - `GET /paquetes`: 20 placeholders `#timeline-diferido-<id>` presentes, sin contenido de
    historial real filtrado a la respuesta inicial (`grep` no encuentra `Anunció` ni el macro de
    historial en el HTML).
  - `GET /paquetes/<id>/timeline` (con `X-Requested-With: fetch`): 200, ~1.7 KB, con el historial
    real del paquete (`Historial`, `Anunció`, etc.).
  - Deep-link `?ver=<id>`: el modal correspondiente nace sin `hidden` y su placeholder se carga vía
    el mismo mecanismo (escaneo al inicio del script).

## Pendiente / fuera de alcance de este ticket

- **No se implementó** el shell-first (header/footer antes que los datos) que el cliente preguntó
  originalmente -- en este repo el header/footer ya viajan en la misma respuesta HTML que los
  datos (no hay una petición de red aparte que los bloquee); lo que se percibía como lentitud era
  tiempo de parseo/render de un documento grande en el navegador, que es lo que este ticket reduce.
  Si el cliente sigue viendo lentitud tras esta verificación, vale la pena repetir la medición en
  localhost con este cambio antes de considerar un rediseño de carga por streaming/SSR incremental.
- **No desplegado** a test.papyrus.com.co -- el pedido fue explícito de solo localhost. Antes de
  desplegar convendría re-medir el peso real de payload con datos de producción (no los 50.000
  sintéticos de la issue 01, que no se usaron para este ticket).
- Unificar el patrón de carga diferida a otras vistas (`/residentes`, `/administracion`) no se
  evaluó -- el cliente solo reportó lentitud en `/paquetes`.

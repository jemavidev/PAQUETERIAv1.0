# Catálogo editable de motivos de cancelación

Fuente: conversación en vivo 2026-09-03 (grilling), pedido directo de Jesús (quien opera este repo). Reemplaza el enum fijo `MotivoCancelacion` (`app/domain/paquete.py`) por un catálogo administrable desde `/administracion/notificaciones`, consumido tanto por el modal "Cancelar paquete" de `/paquetes` como por las filas CANCELADO de esa misma pantalla de plantillas.

**Status:** ready-for-agent

## Problem Statement

Hoy los motivos de cancelación de un paquete (`ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`) son un enum Python fijo (`MotivoCancelacion`). Cambiar, agregar o quitar un motivo requiere una release de código — el ADMIN no tiene ninguna forma de ajustar esa lista por su cuenta, aunque en la práctica es solo texto informativo (una "bandera" que describe por qué se canceló un paquete, sin lógica de negocio atada a valores específicos). El cliente quiere poder gestionar esa lista él mismo, igual que ya gestiona el contenido de las notificaciones desde esa misma pantalla.

## Solution

Se reemplaza el enum `MotivoCancelacion` por una tabla `motivos_cancelacion` con un único campo de contenido (`etiqueta`, texto libre) que el ADMIN gestiona con un CRUD simple (crear / editar / borrar) embebido en `/administracion/notificaciones`. Los dos consumidores actuales del enum pasan a leer de esta tabla:

- El radiogroup de motivos del modal "Cancelar paquete" en `/paquetes`.
- Las filas del tab CANCELADO en `/administracion/notificaciones` (una fila de plantillas de notificación por motivo, igual que hoy).

Se mantiene deliberadamente simple, sin las piezas que un catálogo "serio" tendría: sin código interno separado de la etiqueta (la etiqueta ES el valor guardado, igual que ya pasaba con el texto libre de "Otro"), sin activo/inactivo (borrado duro), sin orden manual (orden de creación), sin historial de auditoría propio. La única regla de negocio nueva es no dejar el catálogo sin ningún motivo, porque cancelar un paquete sigue exigiendo un motivo obligatorio (regla de dominio ya existente en `paquete_lifecycle.cancel`).

Una migración de datos de una sola vez reescribe los valores crudos ya guardados (`ANUNCIO_ERRONEO`, etc.) a etiquetas legibles, tanto en el catálogo nuevo como en las filas ya existentes de `plantillas_notificacion` y `paquetes.cancel_reason`, para que las plantillas ya personalizadas por el cliente sigan enganchadas.

## User Stories

1. Como ADMIN, quiero ver la lista completa de motivos de cancelación desde `/administracion/notificaciones`, para saber qué opciones existen hoy sin tener que ir a mirar el código.
2. Como ADMIN, quiero crear un motivo nuevo escribiendo solo su texto, para agregar una razón de cancelación que no estaba contemplada sin pedirle una release a nadie.
3. Como ADMIN, quiero editar el texto de un motivo existente, para corregir una redacción sin tener que borrarlo y crear uno nuevo.
4. Como ADMIN, quiero borrar un motivo que ya no tiene sentido, para que deje de aparecer como opción al cancelar un paquete nuevo.
5. Como ADMIN, si intento guardar un motivo con el texto vacío, quiero ver un error claro y que no se guarde nada, para no terminar con una opción en blanco en el picker de cancelación.
6. Como ADMIN, si intento crear o renombrar un motivo a un texto que ya existe exactamente igual en otra fila, quiero ver un error claro y que no se guarde, para no terminar con dos opciones idénticas e indistinguibles.
7. Como ADMIN, si intento borrar el único motivo que queda en el catálogo, quiero que el sistema me lo impida con un mensaje claro, para no dejar el modal de cancelar un paquete sin ninguna opción para elegir.
8. Como STAFF cancelando un paquete desde `/paquetes`, quiero ver como opciones exactamente los motivos que el ADMIN configuró, en el mismo orden en que fueron creados, para elegir la razón real sin encontrarme opciones desactualizadas.
9. Como STAFF, al elegir el motivo "Otro" en el modal de cancelar, quiero que se revele un campo de texto libre donde puedo describir la razón real, igual que hoy, para cubrir casos que no calzan con ninguna opción predefinida.
10. Como desarrollador, quiero que ese comportamiento especial de "Otro" siga funcionando exactamente igual que hoy (basado en el texto literal "Otro"), sin agregar un flag nuevo por fila, porque el cliente decidió explícitamente mantenerlo simple y es el único caso que lo necesita hoy.
11. Como ADMIN, si borro o renombro la fila "Otro" del catálogo, entiendo que el campo de texto libre deja de aparecer en el modal de cancelar (el catálogo no impide esto — es una consecuencia aceptada de que "Otro" no es un caso protegido).
12. Como ADMIN, quiero que cada motivo del catálogo tenga su propia fila de plantillas de notificación (SMS/Email/WhatsApp) en el tab CANCELADO, igual que ya pasa hoy con los 4 motivos fijos, para poder personalizar el aviso según la razón de cancelación.
13. Como ADMIN, si creo un motivo nuevo, quiero que automáticamente aparezca una fila nueva de plantillas para él (con el texto por defecto hasta que lo personalice), para no tener que hacer un paso adicional para habilitar sus notificaciones.
14. Como ADMIN, si borro un motivo que ya tenía una plantilla de notificación personalizada, entiendo que esa plantilla deja de mostrarse (ya no hay fila del catálogo que la despliegue) pero no se borra de la base de datos — es un dato huérfano silencioso, no una pérdida activa.
15. Como ADMIN, si vuelvo a crear un motivo con el mismo texto exacto que uno que borré antes, entiendo que puedo "recuperar" sin darme cuenta la plantilla de notificación vieja asociada a ese texto (porque la búsqueda de plantilla es por texto exacto, no por un id estable) — comportamiento aceptado explícitamente por el cliente a cambio de simplicidad.
16. Como desarrollador, quiero que el mensaje de notificación que usa `{motivo}` (para el evento CANCELADO) muestre el texto del motivo tal cual el ADMIN lo escribió, sin ninguna transformación de mayúsculas/formato encima, para no alterar silenciosamente lo que el ADMIN redactó a propósito.
17. Como desarrollador, quiero que los 4 motivos que ya existen hoy (`ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`) se migren automáticamente a filas del catálogo con etiquetas legibles ("Anuncio erróneo", "Devuelto al transportador", "No reclamado", "Otro"), para que el catálogo nazca poblado con las mismas opciones que ya existían, sin que el ADMIN tenga que recrearlas a mano.
18. Como desarrollador, quiero que esa misma migración reescriba los valores crudos ya guardados en `plantillas_notificacion.motivo` y en `paquetes.cancel_reason` (de "ANUNCIO_ERRONEO" a "Anuncio erróneo", etc.) para que las plantillas de notificación que el cliente ya personalizó para esos motivos sigan encontrándose después del cambio, sin que el ADMIN tenga que volver a escribirlas.
19. Como desarrollador, quiero que el enum Python `MotivoCancelacion` se elimine del código una vez migrado, para no dejar dos fuentes de verdad (el enum viejo y la tabla nueva) conviviendo sin necesidad.
20. Como ADMIN, quiero que solo el rol ADMIN pueda crear/editar/borrar motivos, igual que el resto de `/administracion/notificaciones`, para que el catálogo oficial de cara al cliente final no lo pueda tocar cualquier miembro del staff.
21. Como OPERADOR (no-ADMIN), al intentar gestionar el catálogo de motivos debo recibir 403, igual que el resto de esa pantalla, para que quede claro que es exclusivo de ADMIN. (El picker de cancelación en `/paquetes`, en cambio, sigue siendo visible para cualquier STAFF que ya pueda cancelar paquetes hoy — solo la gestión del catálogo es ADMIN-only, no el uso del picker.)
22. Como STAFF cancelando un paquete, si el motivo que elegí fue borrado del catálogo por otro ADMIN justo antes de que yo enviara el formulario, quiero que el servidor rechace el envío con un error claro (motivo inválido), en vez de guardar silenciosamente un `cancel_reason` que ya no corresponde a ninguna opción vigente — mismo criterio de "el servidor no confía en la forma del POST" que ya usa el resto de `admin.py`.

## Implementation Decisions

- **Nueva tabla `motivos_cancelacion`:**
  - `id` (UUID PK, mismo patrón que el resto del esquema).
  - `etiqueta` (`String`, `NOT NULL`, `UNIQUE`) — el único campo de contenido. No hay columna de código separado: la etiqueta ES el valor que se guarda en `Paquete.cancel_reason` y en `PlantillaNotificacion.motivo` cuando se elige ese motivo.
  - `creado_en` (`DateTime`, default ahora) — usado únicamente para ordenar (orden de creación, ascendente); no hay columna `orden` editable.
  - Sin columna `activo` (no hay soft-delete) y sin tabla de historial asociada — decisiones explícitas del cliente a favor de simplicidad.

- **Nuevo módulo de dominio `motivo_cancelacion_service.py`** (seam principal, junto a `notificacion_service.py`):
  - `listar_motivos(session) -> list[MotivoCancelacion]` — todas las filas, ordenadas por `creado_en` ascendente.
  - `crear_motivo(session, etiqueta) -> MotivoCancelacion` — valida no vacío (tras `strip()`) y no duplicado exacto (comparación case-sensitive, igual que el resto de comparaciones de texto en este dominio); `ValueError` en caso contrario.
  - `editar_motivo(session, motivo_id, etiqueta) -> MotivoCancelacion` — misma validación que crear (no vacío, no duplicado contra las DEMÁS filas). No propaga el rename a `plantillas_notificacion`/`paquetes` ya existentes (comportamiento aceptado, ver historias 14-15).
  - `eliminar_motivo(session, motivo_id) -> None` — `ValueError` si es la última fila restante del catálogo. Borrado duro (no toca `plantillas_notificacion` ni `paquetes` — quedan intactos con el texto que ya tenían).
  - `motivo_valido(session, etiqueta) -> bool` — helper para que la ruta de cancelar en `packages.py` valide server-side que el motivo elegido sigue existiendo en el catálogo (historia 22); "Otro" es un caso especial que se valida por su propia regla de texto libre no vacío, no contra el catálogo.

- **`/administracion/notificaciones` (misma ruta, misma dependencia `require_admin`):**
  - Se agrega una sección/modal de gestión del catálogo (crear / editar / borrar), en el mismo estilo visual (modales `data-open`/`data-close`, toasts de error/éxito) que ya usa el resto de la pantalla.
  - `_filas_plantillas` deja de iterar `MotivoCancelacion` y pasa a iterar `listar_motivos(db)` para generar las filas CANCELADO — cada fila usa `motivo.etiqueta` como el `motivo` que ya viaja hoy a `_canales_de`/`obtener_texto_actual`/`guardar_plantilla` (sin cambios de firma en esas funciones, siguen recibiendo un `str`).

- **`/paquetes` (modal "Cancelar paquete"):**
  - `_render_lista` dejar de pasar `"motivos": list(MotivoCancelacion)` y pasa `"motivos": listar_motivos(db)` (o el shape equivalente que ya arma `opciones_motivo` en el template) — el radiogroup en `packages/_resultados.html` no cambia de mecanismo (radio real oculto + `peer-checked`), solo su fuente de datos.
  - El bloque especial de "Otro" (JS que revela `cancelar-otro-wrap-{{ p.id }}`) sigue comparando contra el literal `"Otro"` (antes `"OTRO"`) — se actualiza el string comparado en el JS y en `cancel_action` (`packages.py:1208`) para que calce con la nueva etiqueta legible sembrada por la migración.
  - `cancel_action` valida server-side que el `motivo` recibido exista en el catálogo (vía `motivo_valido`) o sea el caso especial "Otro" con `motivo_otro` no vacío — `ValueError` → mismo manejo de error que ya existe para otras validaciones de esa ruta.

- **`notificacion_service.py`:**
  - `_variables()` y `variables_ejemplo()` dejan de aplicar `_motivo_legible()` sobre `motivo` — usan el valor tal cual (ya es texto legible elegido por el ADMIN o tecleado libremente por el STAFF vía "Otro"). `_motivo_legible()` se elimina si queda sin otros usos tras este cambio (confirmar durante la implementación).

- **`app/domain/paquete.py`:** se elimina la clase `MotivoCancelacion` y sus imports en `admin.py`, `packages.py`, `paquete_lifecycle.py`. `paquete_lifecycle.cancel()` deja de tener la rama `isinstance(motivo, MotivoCancelacion)` — `motivo` pasa a ser siempre un `str` no vacío (el caller ya resuelve el texto final antes de llamar, igual que hoy hace `cancel_action` para el caso "Otro").

- **Migración Alembic (una sola revisión):**
  1. Crea la tabla `motivos_cancelacion`.
  2. Inserta las 4 filas iniciales: "Anuncio erróneo", "Devuelto al transportador", "No reclamado", "Otro" — en ese orden (mismo orden que el enum original), para que `creado_en` preserve el orden histórico del picker.
  3. `UPDATE` sobre `plantillas_notificacion` y `paquetes`: reescribe cada valor crudo del enum (`ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`) a su etiqueta legible correspondiente, en las columnas `motivo` y `cancel_reason` respectivamente. Cualquier `cancel_reason` que NO calce con ninguno de esos 4 valores crudos (texto libre ya tecleado alguna vez vía "Otro") se deja intacto — no es un valor del catálogo, nunca lo fue.

## Testing Decisions

Los tests verifican comportamiento observable (qué devuelve una función pública del dominio, qué responde una ruta HTTP) — mismo criterio que el resto del repo, nada de aserciones sobre implementación interna.

- **Seam de dominio** — `tests/data_model/test_motivo_cancelacion.py` (nuevo, junto a `test_notificacion_service.py`):
  - `crear_motivo` guarda la etiqueta y aparece en `listar_motivos`.
  - `crear_motivo` con etiqueta vacía (o solo espacios) lanza `ValueError`, no guarda nada.
  - `crear_motivo` con una etiqueta ya existente (exacta) lanza `ValueError`, no guarda un duplicado.
  - `editar_motivo` cambia el texto de una fila existente sin crear una fila nueva; sigue validando vacío/duplicado contra las demás filas.
  - `eliminar_motivo` borra la fila cuando hay más de una en el catálogo.
  - `eliminar_motivo` sobre la última fila restante lanza `ValueError`, la fila sigue existiendo.
  - `listar_motivos` devuelve las filas ordenadas por `creado_en` ascendente.
  - `motivo_valido` devuelve `True` para una etiqueta existente y `False` para una que no está en el catálogo.
  - Extender `tests/data_model/test_cancelar_paquete.py`: `paquete_lifecycle.cancel()` acepta cualquier `str` no vacío como motivo (sin depender de `MotivoCancelacion`), mismo comportamiento de siempre para motivo `None`/vacío.
  - Extender `tests/data_model/test_notificacion_service.py`: el `{motivo}` resuelto en un mensaje de CANCELADO es el texto tal cual (sin capitalización ni reemplazo de guiones bajos).

- **Seam web — `/administracion/notificaciones`** — extender `tests/web/test_admin_notificaciones.py` (mismo patrón `_login_admin`/`_login_operador` ya presente):
  - Gate sin cambios: `OPERADOR` recibe 403 al intentar crear/editar/borrar un motivo; solo `ADMIN` puede.
  - Crear un motivo nuevo lo agrega a la lista de filas CANCELADO mostradas (con sus 3 canales, texto por defecto).
  - Crear con etiqueta vacía o duplicada devuelve error, sin alterar el catálogo.
  - Borrar un motivo lo quita de las filas CANCELADO mostradas.
  - Intentar borrar el último motivo devuelve error, la fila sigue apareciendo.

- **Seam web — `/paquetes`** — extender `tests/web/test_packages.py`:
  - El modal "Cancelar paquete" muestra como opciones exactamente las etiquetas del catálogo actual.
  - Cancelar con un motivo del catálogo persiste `cancel_reason` igual a esa etiqueta.
  - Cancelar con motivo "Otro" + `motivo_otro` persiste el texto libre tecleado (comportamiento sin cambios).
  - Cancelar con un `motivo` que no existe en el catálogo (ni es "Otro") devuelve error, el paquete no transiciona.

- **Migración:** se verifica manualmente contra el ambiente de desarrollo local (`scripts/paquetex_dev_up.sh`) aplicando la migración sobre los datos reales ya presentes (los 2 paquetes cancelados y las 12 filas de `plantillas_notificacion` de CANCELADO que ya existen hoy) y confirmando que las etiquetas quedan legibles y las plantillas siguen encontrándose desde `/administracion/notificaciones`. Cubierto además por el guard existente `test_parity_esquema_orm` (esquema↔ORM), sin test de migración dedicado nuevo — mismo criterio que el resto de migraciones del repo.

## Out of Scope

- Código interno estable separado de la etiqueta — la etiqueta es el único valor, por decisión explícita del cliente.
- Soft-delete / flag `activo` por motivo — el borrado es siempre duro.
- Reordenamiento manual (drag-and-drop, campo `orden`) — el orden es siempre el de creación.
- Historial de auditoría de cambios al catálogo (quién creó/editó/borró cada motivo y cuándo) — a diferencia de `plantillas_notificacion_historial`, este catálogo no lleva rastro propio.
- Generalizar "permite texto libre" a un flag por fila — "Otro" sigue siendo el único caso especial, hardcodeado por su texto literal.
- Cancelación self-service por el cliente final — el picker de motivos sigue siendo exclusivo del flujo de STAFF en `/paquetes`; no existe hoy una vista de cliente que cancele su propio paquete, y este trabajo no la introduce.
- Pantalla propia (`/administracion/motivos-cancelacion` o similar) — el CRUD vive embebido en `/administracion/notificaciones`, por decisión explícita del cliente.
- Reconciliar automáticamente una plantilla de notificación huérfana cuando se borra o renombra un motivo — es un efecto aceptado (historias 14-15), no algo que este trabajo prevenga o limpie.

## Further Notes

- Precedente directo: `.scratch/plantillas-notificacion-multicanal` (extendió `plantillas_notificacion` con `canal`) y `.scratch/notificaciones-enviar-prueba` (agregó el envío de prueba a la misma pantalla) — este trabajo sigue extendiendo la misma pantalla `/administracion/notificaciones` como punto único de gestión de todo lo relacionado a notificaciones/motivos.
- Dato de partida verificado en el ambiente de desarrollo local (2026-09-03): ya existen las 12 filas de `plantillas_notificacion` (4 motivos × 3 canales) para CANCELADO, y 2 paquetes cancelados con `cancel_reason` en valores crudos del enum (`ANUNCIO_ERRONEO`, `NO_RECLAMADO`) — la migración descrita arriba debe cubrir exactamente estos datos reales, no solo un esquema vacío.
- El cliente fue explícito en que este catálogo es "solo una etiqueta... una especie de bandera informativa, nada más" — cualquier decisión de implementación ambigua durante la construcción debe resolverse a favor de la opción más simple, no de la más "completa" o defensiva.

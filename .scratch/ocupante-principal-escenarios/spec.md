Status: ready-for-agent
Feature: ocupante-principal-escenarios
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · `.scratch/ocupante-principal-escenarios/escenarios.md` (matriz de ~55 escenarios verificados contra el código, punto de partida de esta spec) · `docs/adr/0006-ocupante-residentes-sin-persona-propia.md` y `docs/adr/0007-persona-telefono-o-whatsapp.md` (no se reabren) · `.scratch/apartamento-catalogo-confirmacion/spec.md` (el modelo pending/confirmado que esta spec extiende, no reemplaza)

---

## Problem Statement

El modelo actual de Ocupante/Principal (confirmación manual únicamente, por staff o por el propio principal) resultó incompleto frente a cómo se usa el sistema en la práctica: varios residentes de un mismo apartamento pueden empezar a anunciar paquetes antes de que nadie confirme quién es el principal, y no hay ninguna señal automática que resuelva esa ambigüedad — la unidad puede quedar sin principal indefinidamente si el staff no interviene a mano.

Por separado, se auditó el comportamiento de las 5 vistas que tocan Ocupante/Apartamento (`/announce`, `/residentes` tabs Dirección y Residentes, `/mis-datos`, `/paquetes` → Corregir destinatario) contra ~55 escenarios concretos, y salieron varias inconsistencias reales entre vistas: WhatsApp como identidad de un residente nuevo solo funciona desde `/announce` (las otras 3 vías solo tienen campo Teléfono); las notificaciones de un paquete siempre caen al principal cuando el destinatario no tiene contacto propio, incluso cuando quien anunció SÍ se identificó y sería el remitente lógico; no hay forma de mover a un residente de una unidad a otra sin un paso manual de "dar de baja" primero; y un Ocupante puede quedar creado en la base de datos aunque la acción que lo originó (anunciar, corregir destinatario) haya fallado.

## Solution

Un solo cambio de fondo — un segundo camino automático hacia "principal", disparado por la recepción de un paquete — más un conjunto de correcciones de consistencia entre las 5 vistas, decididas juntas porque todas dependen del mismo modelo de datos (Ocupante/Persona/Apartamento).

1. **Promoción a principal por dos caminos.** El camino manual existente (staff confirma, o el propio principal confirma a un conviviente) sigue igual. Se agrega un camino nuevo: al **recibir** un paquete (`ANUNCIADO`→`RECIBIDO`), si la unidad del destinatario todavía no tiene principal y el destinatario resuelto tiene Persona propia (Teléfono o WhatsApp), se promueve automáticamente en el mismo acto — sin paso manual. Si el destinatario resuelto no tiene contacto propio, la promoción simplemente no se dispara esa vez; la unidad queda sin principal hasta que alguien con contacto reciba algo. Cualquiera de los dos caminos, al promover, marca **tanto** `es_principal=True` **como** `confirmado_en` en la misma operación — ya no puede quedar un principal sin confirmar.

2. **Contacto opcional para residentes secundarios, en todas las vistas por igual.** Un residente secundario puede o no tener Teléfono/WhatsApp propio (sin cambios en esa regla). Lo que cambia es que las 3 vías que hoy solo aceptan Teléfono al crear/editar un residente (tab Residentes, `/mis-datos`, Corregir destinatario) pasan a aceptar también WhatsApp, con el mismo campo único autoclasificado que ya usa `/announce` — sin duplicar inputs.

3. **Las notificaciones caen a quien anunció, no siempre al principal.** Cuando el destinatario de un paquete no tiene contacto propio, `recipient_phone` deja de resolver su propio fallback-a-principal de forma aislada — usa a quien quedó como Anunciante del paquete. En la práctica esto no cambia nada cuando no se sabe quién llama (Torre+Apto directo, donde el Anunciante ya se resolvía al principal) pero sí cambia cuando sí se sabe (Teléfono/WhatsApp con co-residentes): ahí la notificación le llega a quien anunció, no al principal de la unidad.

4. **Recibir gana un paso de resolución, no solo un modal de tipo/condición/guía.** Si el destinatario de un paquete no tiene apartamento todavía, el staff puede declarar Torre+Apartamento ahí mismo. Si ya tiene (o se lo acaba de declarar), el staff ve el roster de residentes de esa unidad y puede confirmar que es para quien ya estaba, elegir a otro residente ya existente, o registrar uno nuevo — reusando el mismo mecanismo que ya existe en Corregir destinatario, no una pantalla nueva. Este paso es también el que le da a la promoción automática del punto 1 un Ocupante concreto sobre el cual actuar (el Paquete nunca guarda una referencia directa a Ocupante, solo el snapshot congelado — ver Implementation Decisions).

5. **Mover un residente secundario de una unidad a otra, en un solo paso.** Staff puede hacerlo directo (sin el paso manual de "dar de baja" primero) en cualquiera de las 4 vistas que hoy bloquean con "ya es Ocupante activo" — pero nunca para un principal, que sigue exigiendo el camino de siempre (promover a otro primero si hay más gente, o desvincularse si está solo).

6. **El picker de Torre+Apartamento en tab Dirección pasa de informativo a restrictivo.** Solo se pueden elegir unidades completamente vacías desde ahí — agregar más residentes a una unidad que ya tiene gente se hace exclusivamente desde tab Residentes, nunca desde tab Dirección.

7. **Cupo máximo de Ocupantes activos por unidad: 5 → 10** (incluye al principal).

8. **Desvincular el propio Teléfono desde tab Datos**, nueva acción — solo si la Persona ya tiene WhatsApp como respaldo, con advertencia explícita de que pierde acceso a `/mis-datos` (el login sigue siendo estrictamente por Teléfono) y cierre de sesión inmediato al confirmar.

9. **Integridad transaccional cuando "crear Ocupante + acción siguiente" falla a medio camino** (Corregir destinatario → nuevo ocupante; `/announce` Torre+Apto → nueva persona): rollback explícito antes de devolver el error, para que el Ocupante recién creado no quede persistido si la acción completa no se concretó.

Queda fuera de esta rebanada: habilitar login/OTP por WhatsApp (sigue sin existir — la advertencia del punto 8 asume esa limitación, no la resuelve), y revertir que `/mis-datos` sea de solo lectura para Torre/Apartamento (sigue siendo exclusivo de staff).

### Seam

Esta rebanada toca 5 vistas HTTP con comportamiento genuinamente distinto entre sí (picker restrictivo solo en tab Dirección, paso de resolución solo en Recibir, etc.), así que la costura principal y única es la **capa web** (rutas FastAPI vía `TestClient`), extendiendo los 4 archivos de test que ya existen uno por vista (`test_announce_new.py`, `test_customers_manage.py`, `test_customer_verify.py`, `test_packages.py`) en vez de abrir costuras nuevas — mismo patrón ya usado en todo el repo: request real contra el `client` fixture, aserciones tanto sobre el HTML de la respuesta como sobre el estado de dominio resultante vía `client.db` (ej. `client.db.get(Ocupante, id).es_principal`).

La única regla que es puramente de máquina de estados sin contraparte HTML directa — "promover también confirma", y la resolución de qué Ocupante corresponde a un Paquete recibido — se prueba en la costura de dominio ya existente (`tests/data_model/test_ocupante_service.py`), porque ahí ya vive el resto de la lógica de `promover_a_principal`/`confirmar_ocupante` y es más directo verificarla sin pasar por HTTP en cada caso. Es la única excepción al seam único, y es la misma que ya usa `apartamento-catalogo-confirmacion/spec.md` para el mismo tipo de regla.

## User Stories

### Promoción automática al recibir

1. Como staff, quiero que recibir el primer paquete de un residente de una unidad sin principal lo promueva automáticamente, para no depender de acordarme de confirmarlo a mano.
2. Como residente que fue el primero de mi unidad en recibir un paquete, quiero quedar como principal de inmediato, para poder gestionar al resto de mi unidad sin pedirle a nadie que me confirme.
3. Como staff, quiero que esta promoción automática aplique sin importar por cuál de los 3 caminos de `/announce` (o `/anunciar`) se haya anunciado el paquete originalmente, para no tener que recordar excepciones por vista.
4. Como desarrollador, quiero que la promoción automática no se dispare si el destinatario resuelto no tiene Teléfono ni WhatsApp propio, para no violar la regla de que todo principal tiene contacto propio.
5. Como staff, quiero que una unidad sin nadie con contacto propio simplemente quede sin principal hasta que alguien con contacto reciba algo, en vez de que el sistema falle o fuerce datos incompletos.
6. Como desarrollador, quiero que promover a principal (por cualquiera de los 2 caminos) marque también `confirmado_en` en el mismo acto, para que nunca quede un Ocupante `es_principal=True` sin confirmar.

### Recibir: resolución de apartamento y destinatario

7. Como staff, quiero poder declarar Torre+Apartamento al recibir un paquete de alguien que todavía no tiene unidad asignada, para no tener que ir a otra pantalla antes de continuar.
8. Como staff, quiero, al recibir un paquete de alguien que ya tiene unidad, ver el roster de residentes de esa unidad y confirmar o corregir a nombre de quién es, para no depender de que el anuncio original haya identificado bien al destinatario.
9. Como staff, quiero poder registrar un residente nuevo de esa unidad directamente desde el paso de Recibir, para no tener que ir a `/residentes` aparte cuando me doy cuenta en ese momento de que falta alguien.
10. Como desarrollador, quiero reusar el mismo mecanismo de candidatos que ya existe en Corregir destinatario para este paso, para no mantener dos implementaciones del mismo concepto.

### Contacto (Teléfono/WhatsApp) de residentes secundarios

11. Como staff, quiero poder registrar a un residente nuevo con WhatsApp (no solo Teléfono) desde tab Residentes, Corregir destinatario, o `/mis-datos`, para no tener que usar `/announce` como única vía cuando la persona no tiene celular con SMS.
12. Como principal, quiero poder agregar un conviviente con solo WhatsApp desde `/mis-datos`, con la misma facilidad que ya tengo para Teléfono.
13. Como staff, quiero poder asociar/editar/desvincular el WhatsApp de un residente secundario desde tab Residentes, con el mismo patrón que ya existe para Teléfono.
14. Como usuario del sistema (staff o cliente) escribiendo un contacto nuevo, quiero un solo campo que detecte automáticamente si es Teléfono o WhatsApp, para no tener que elegir un tipo de campo a mano.

### Notificaciones

15. Como residente que anuncia un paquete a nombre de un conviviente sin contacto propio, quiero recibir yo las notificaciones de ese paquete, para enterarme del estado sin depender de que el principal de la unidad me avise.
16. Como desarrollador, quiero que este comportamiento no cambie el caso donde no se sabe quién llama (Torre+Apto directo), para no romper el fallback-a-principal que ya funciona bien ahí.
17. Como staff, quiero que, al identificar a alguien por Teléfono/WhatsApp que vive con más residentes, esa persona quede preseleccionada en la lista de a quién se le anuncia, para agilizar el caso más común (anunciar para uno mismo) sin perder la opción de elegir a otro.

### Mover residentes entre unidades

18. Como staff, quiero poder mover a un residente secundario de una unidad a otra en un solo paso, para no tener que darlo de baja y volver a agregarlo por separado.
19. Como staff, quiero que esto NO sea posible para un principal bajo ninguna circunstancia, para no dejar una unidad sin nadie que la administre de forma implícita.
20. Como staff, quiero que al intentar asociar un Teléfono/WhatsApp que ya es Ocupante activo de otra unidad, el sistema me muestre de qué unidad es y me ofrezca moverlo ahí mismo (si no es principal), en vez de solo bloquear con un error genérico.
21. Como staff, quiero que esta capacidad de mover funcione igual en las 4 vistas que hoy bloquean este caso (tab Dirección, tab Residentes, `/announce` Torre+Apto nueva persona, Corregir destinatario), para no tener un comportamiento distinto según por dónde entré.

### Picker de Torre+Apartamento (tab Dirección)

22. Como staff, quiero que el picker de tab Dirección solo me deje elegir unidades completamente vacías, para no asociar por error a alguien a una unidad que ya tiene gente sin darme cuenta.
23. Como staff, quiero seguir pudiendo agregar más residentes a una unidad que ya tiene principal, pero desde tab Residentes (no desde tab Dirección), para tener un solo lugar claro para esa acción.

### Cupo máximo

24. Como staff, quiero poder registrar hasta 10 Ocupantes activos por unidad (antes 5), para cubrir unidades con más residentes reales sin toparme con el límite.

### Desvincular el propio Teléfono

25. Como principal que solo quiere identificarse por WhatsApp de ahora en adelante, quiero poder quitar mi propio Teléfono desde tab Datos, si ya tengo WhatsApp asociado.
26. Como usuario a punto de quitar mi propio Teléfono, quiero una advertencia explícita de que voy a perder acceso a `/mis-datos` (el login es solo por Teléfono hoy), para no hacerlo sin saber la consecuencia.
27. Como desarrollador, quiero que al confirmar esta acción se cierre la sesión de inmediato, para que no quede una sesión activa con una identidad que ya no puede volver a autenticarse.

### Integridad transaccional

28. Como staff, quiero que si registro un residente nuevo y la acción que lo originó (anunciar, corregir destinatario) falla después, ese residente NO quede creado a medias, para no ensuciar el padrón con registros huérfanos que nadie pidió.

### Ajustes menores

29. Como staff, quiero ver un indicador claro cuando el código Torre+Apto que tecleé en `/announce` no corresponde a ninguna unidad real, en vez de que no aparezca nada.
30. Como staff, quiero que la acción "Confirmar" no se me ofrezca sobre un Ocupante que ya está confirmado, para no encontrarme con un error evitable.
31. Como staff, quiero mensajes de error distintos para "el paquete no tiene apartamento en su snapshot" y "falta el nombre" al usar Corregir destinatario → nuevo ocupante, para saber cuál de las dos cosas corregir.
32. Como staff, quiero que si el sistema detecta y limpia un dato huérfano de apartamento, me lo explique con un mensaje claro, para entender qué pasó.

## Implementation Decisions

### Promoción a principal — dos caminos, una sola operación

- `ocupante_service.promover_a_principal` pasa a marcar también `confirmado_en = ahora()` si todavía era `None`, además de `es_principal=True` — sin importar si se llama desde el botón "Promover" explícito o desde el disparador nuevo de abajo.
- Disparador nuevo: al final de `paquete_lifecycle.receive()` (después de que la transición `ANUNCIADO`→`RECIBIDO` tuvo éxito), resolver qué Ocupante corresponde al destinatario del paquete y, si su unidad todavía no tiene ningún `es_principal=True`, promoverlo. Si no se puede resolver un Ocupante concreto (ver más abajo), o el resuelto no tiene `persona_id`, no se dispara nada — el `receive()` en sí nunca falla por esto.
- **Resolución de "qué Ocupante"**: `Paquete` no guarda una FK a `Ocupante` (ADR-0001, solo snapshot congelado — `recipient_name`/`recipient_phone`/`snapshot_conjunto/torre/apartamento`). La resolución intenta, en orden: (a) si `recipient_phone` no es nulo, buscar la Persona por ese teléfono y su Ocupante activo; (b) si no, buscar dentro del roster de la unidad del snapshot (`snapshot_torre`/`snapshot_apartamento`) un Ocupante cuyo `nombre` coincida con `recipient_name` — mismo patrón que ya usa `_resolver_ocupante_por_nombre` en `paquete_service.py` para un caso análogo. Si ninguna de las dos resuelve, no se promueve nada esa vez.
- El paso nuevo de Recibir (ver abajo) es la vía principal para que esta resolución sea exacta cuando había ambigüedad — cuando no hay ambigüedad (el destinatario ya tenía contacto propio, match directo por teléfono), la promoción puede dispararse sin que el staff toque nada de ese paso.

### Recibir — paso de resolución de apartamento/destinatario

- Se extiende el flujo de Recibir (compartido entre `/paquetes` y `/announce`, mismo componente ya documentado en `announce_new.py`) con un paso opcional, mostrado según el estado del destinatario:
  - Sin apartamento en el snapshot todavía → ofrece declarar Torre+Apartamento (mismo picker que tab Dirección, con la restricción de "solo unidades vacías" — ver más abajo — **no aplica acá**, porque acá se está asociando a una persona ya identificada por Teléfono/WhatsApp, no como el flujo de tab Dirección que arranca desde cero).
  - Con apartamento (ya tenía, o se lo acaba de declarar) → muestra el roster de esa unidad, reusando el mecanismo de candidatos de `candidatos_correccion`/Corregir destinatario: confirmar al ya resuelto, elegir otro residente existente, o registrar uno nuevo (con el input único de contacto autoclasificado, ver abajo).
- Este paso NO es obligatorio para completar Recibir — si el destinatario ya resuelve sin ambigüedad, Recibir funciona exactamente igual que hoy (tipo/condición/guía) sin fricción adicional.

### Contacto único autoclasificado, reusado en 4 vistas

- El clasificador `_clasificar` (hoy privado en `announce_new.py`: 10 dígitos empezando en `3` → Teléfono; ≥3 letras iniciales → WhatsApp) se mueve a un módulo compartido de dominio, para que las rutas web lo reusen sin duplicar la regla.
- Se reemplaza el campo "Teléfono" (input único) por un campo "Teléfono o WhatsApp" (input único, autoclasificado en el servidor) en: tab Residentes → agregar Ocupante; `/mis-datos` → agregar Ocupante; Corregir destinatario → nuevo ocupante.
- `ocupante_service` gana `asociar_whatsapp_a_ocupante`/`editar_whatsapp_ocupante`/`desvincular_whatsapp_ocupante`, mismo contrato y mismas restricciones que ya tienen sus contrapartes de Teléfono (el principal no se edita/desvincula por acá, se edita desde tab Datos).

### Notificaciones — recipient_phone cae al Anunciante, no a un fallback propio

- En `paquete_service.announce()`, para `Destinatario.OCUPANTE`: cuando el Ocupante resuelto no tiene `persona_id` propio, `recipient_phone` deja de resolver `telefono_notificacion_ocupante` (que hoy cae a la Persona del principal por su cuenta) — usa directamente el Teléfono de la Persona `anunciante` que la misma llamada a `announce()` ya resolvió (`None` si el Anunciante es solo-WhatsApp, mismo criterio de siempre: `recipient_phone` es estrictamente Teléfono).
- Efecto ya verificado en los dos caminos existentes: Torre+Apto directo (el Anunciante ya se resuelve al principal vía `anunciante_para_ocupante`, sin cambio de resultado) vs. Teléfono/WhatsApp con co-residentes (el Anunciante es quien llamó, cambia el resultado — la notificación deja de caer al principal y cae a quien anunció).
- En la pantalla de co-residentes (`_identificar_unidad.html`), la fila de quien identificó por Teléfono/WhatsApp aparece preseleccionada (mismo estado que si el staff la hubiera clickeado) — el resto de la lista sigue disponible para cambiar la elección.

### Mover residentes entre unidades (solo no-principal, solo staff)

- Se reemplaza el bloqueo actual ("ya es Ocupante activo, debe darse de baja antes") por una acción de "mover": si la Persona/Ocupante activo en la otra unidad NO es principal ahí, se da de baja en la unidad anterior y se agrega a la nueva en la misma operación de dominio. Si SÍ es principal, el bloqueo actual se mantiene sin cambios (mismo mensaje de siempre: promover a otro primero, o darse de baja si está solo).
- Aplica en las 4 vistas que hoy usan `agregar_ocupante`/`reasignar_apartamento` y chocan con este caso: tab Dirección, tab Residentes, `/announce` Torre+Apto nueva persona, Corregir destinatario nuevo ocupante.
- No se ofrece dentro de Anunciar/Recibir — es una acción de gestión de residentes aparte, staff-only (no disponible en `/mis-datos`).
- El mensaje de error/UI cuando se detecta el conflicto pasa a indicar de qué unidad es Ocupante actualmente (Torre+Apartamento), para que el staff sepa qué está moviendo.

### Picker de tab Dirección — solo unidades vacías

- El picker de `/residentes/{id}/apartamento` dejar de usar `apartamentos_con_principal` como indicador informativo — pasa a deshabilitar (no solo marcar) cualquier unidad con **al menos un Ocupante activo** (con o sin principal confirmado), no solo las que ya tienen principal. Se necesita una consulta nueva/más amplia que la actual (`apartamentos_con_principal` solo cubre las que ya tienen principal).
- Agregar residentes a una unidad que ya tiene gente sigue disponible, pero exclusivamente desde tab Residentes de la ficha de alguien que ya pertenece a esa unidad.

### Cupo máximo

- `ocupante_service.MAX_OCUPANTES_ACTIVOS` pasa de `5` a `10`. Cambio mecánico, sin lógica adicional — el chequeo existente (`agregar_ocupante`) sigue igual, solo cambia la constante.

### Desvincular el propio Teléfono (tab Datos)

- Nueva función en `persona_service.py` (junto a `cambiar_telefono_propio`): quita `telefono` de la Persona logueada, exige que `whatsapp_usuario` ya esté presente (si no, rechaza con mensaje claro).
- La ruta web exige una confirmación explícita (ej. modal/checkbox de "entiendo que voy a perder acceso a este panel") antes de ejecutar — mismo espíritu que otras confirmaciones destructivas ya existentes en el repo.
- Al confirmar con éxito, cierra la sesión de ese dispositivo de inmediato (mismo patrón que ya usa `cambiar_telefono_propio` al cambiar a un número nuevo, que también fuerza reverificación).

### Integridad transaccional (rollback explícito)

- En `/announce` (Torre+Apto → nueva persona) y en `/paquetes` → Corregir destinatario → nuevo ocupante: si `agregar_ocupante` tiene éxito pero el paso siguiente de esa misma acción compuesta falla (no se puede anunciar por falta de Anunciante resolvible; `corregir_destinatario` falla por cambio de estado concurrente), la ruta llama `db.rollback()` explícito antes de devolver la respuesta de error — en vez de dejar que el `commit()` automático de `get_db` persista el Ocupante a medias.
- No hace falta tocar `get_db` ni introducir savepoints: ninguna de las dos rutas hace otra escritura antes de este punto en el mismo request, así que un rollback completo es seguro.

### Ajustes menores de UI

- `/announce` Torre+Apto: cuando el código tecleado no calza con ninguna unidad real del catálogo, mostrar un mensaje/indicador explícito (hoy no muestra nada).
- Ocultar la acción "Confirmar" en la UI cuando el Ocupante ya tiene `confirmado_en` (hoy la acción sigue visible y el servidor la rechaza con error).
- Corregir destinatario → nuevo ocupante: separar el mensaje de error genérico actual en dos mensajes específicos ("este paquete no tiene apartamento resuelto" vs. "falta el nombre del nuevo residente").
- Cuando `reasignar_apartamento` detecta y limpia un `apartamento_actual_id` huérfano (sin Ocupante real detrás), mostrar un mensaje explicando qué se corrigió, en vez de limpiarlo en silencio.

## Testing Decisions

Un buen test acá verifica comportamiento observable — qué queda en la base de datos y qué ve el staff/cliente en la respuesta — nunca implementación interna (qué función privada se llamó, cuántas queries, salvo los tests de rendimiento ya existentes que son un caso aparte y no tocan esta rebanada).

- **Seam principal — capa web (`tests/web/`)**, extendiendo los archivos que ya existen por vista: `test_announce_new.py` (los 3 caminos + el paso nuevo de Recibir + preselección del llamante), `test_customers_manage.py` (tab Dirección: picker restrictivo, mover no-principal, bloqueo de mover principal; tab Residentes: WhatsApp, cupo 10, ocultar Confirmar), `test_customer_verify.py` (`/mis-datos`: WhatsApp, desvincular propio teléfono + advertencia + cierre de sesión), `test_packages.py` (Recibir con resolución de destinatario, Corregir destinatario con WhatsApp + rollback en fallo).
  - Prior art directo dentro de estos mismos archivos: ya combinan aserciones sobre el HTML devuelto (`assert "..." in r.text`) con aserciones directas de estado de dominio vía `client.db` (`client.db.get(Ocupante, id)`, `client.db.query(Persona)...`) — mismo patrón para todo lo nuevo.
- **Seam secundaria — capa de dominio (`tests/data_model/test_ocupante_service.py`)**, solo para las reglas de máquina de estados sin contraparte HTML directa:
  - `promover_a_principal` marca `confirmado_en` además de `es_principal`, sin importar el origen de la llamada.
  - La resolución de "qué Ocupante corresponde a este Paquete recibido" (por teléfono, luego por nombre dentro de la unidad del snapshot, luego ninguno).
  - El disparador de `receive()` no promueve cuando el Ocupante resuelto no tiene `persona_id`.
- **Regresión explícita para el rollback (H6/punto 9)**: un test que fuerza el fallo del segundo paso (ej. hace que el paquete cambie de estado entre la resolución y `corregir_destinatario`) y verifica que el Ocupante creado en el primer paso **no existe** después — mismo patrón de "provocar el estado RED antes del fix" ya usado en la sesión de diagnóstico de rendimiento de este mismo proyecto (contar filas antes/después, no solo status code).
- Full suite (`pytest -q`, ~800 tests hoy) se corre igual al final de cada ticket, como ya es costumbre en este repo.

## Out of Scope

- Login/OTP por WhatsApp — sigue sin existir. La advertencia de "vas a perder acceso a `/mis-datos`" al desvincular el propio Teléfono asume esta limitación, no la resuelve.
- Revertir que Torre/Apartamento sea de solo lectura en `/mis-datos` — se queda exclusivo de staff, sin cambios.
- Backfill retroactivo de unidades/paquetes que ya estén en un estado inconsistente con las reglas nuevas (ej. un principal sin confirmar que ya exista hoy en datos reales) — si aparece, se trata aparte.
- Rediseño visual de las pantallas tocadas más allá de lo que cada Implementation Decision pide explícitamente — no es una rebanada de UI/UX general.
- `/anunciar` (autoservicio público del cliente) no gana ninguna pantalla ni campo nuevo en esta rebanada — solo se ve afectado indirectamente porque un paquete anunciado ahí también puede disparar la promoción automática al recibirse (punto 3 de Promoción automática).

## Further Notes

- La matriz completa de ~55 escenarios (`escenarios.md`, misma carpeta) documenta el comportamiento verificado **antes** de esta spec, escenario por escenario, con cita de archivo:línea — útil como checklist al desglosar tickets, para no perder ningún caso ya cubierto por accidente.
- Varios de los escenarios de esa matriz quedan **sin cambios** (confirmado explícitamente durante el grilling, no es una omisión): los 4 escenarios del camino Teléfono/WhatsApp directo de `/announce`, la mayoría de Torre+Apto (salvo el indicador de "no existe" y el ajuste de notificaciones), tab Dirección 3.4-3.7 (el botón "Quitar" para desvincular ya existe hoy, no hacía falta pedirlo de nuevo), y la mayor parte de tab Residentes/`/mis-datos` fuera de lo listado arriba.

Status: ready-for-agent
Feature: announce-rapido
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · `docs/adr/0003-telefono-llave-universal.md` (se reabre, ver Further Notes) · `docs/adr/0006-ocupante-residentes-sin-persona-propia.md` (no se reabre) · `.scratch/apartamento-catalogo-confirmacion/spec.md` (catálogo cerrado + confirmación de Ocupante, no se reabre, se reutiliza) · `.scratch/paquetes-busqueda-viva/spec.md` (patrón de búsqueda en vivo por `fetch`, se reutiliza) · CONTEXT.md (glosario, se actualiza)

---

## Problem Statement

Hoy el staff anuncia un paquete en `/announce` con 3 bloques totalmente desconectados entre sí: un picker de Torre/Apartamento con selects estáticos, una lista de filas para registrar Residentes de esa unidad, y un bloque de "Anunciar" aparte que vuelve a pedir Teléfono + Nombre de cero — sin reutilizar nada de lo que el staff ya tecleó arriba. No hay forma de anunciar un paquete a un Teléfono o usuario de WhatsApp ya conocido sin volver a escribirlo todo, y no hay ningún flujo para el caso real más común: alguien golpea con un paquete para un apartamento, el staff sabe la unidad pero no sabe todavía a cuál de los residentes de esa unidad pertenece — puede ser alguien ya registrado o una persona nueva.

El cliente necesita que esta pantalla sea rápida y ágil de verdad — es una herramienta operativa que el staff usa muchas veces seguidas por turno — y hoy no lo es: demasiados campos, demasiados clics, ningún atajo para identificar a alguien por lo que el staff ya tiene a mano (el teléfono que le dictan, la unidad que conoce de memoria, o el usuario de WhatsApp).

## Solution

Rediseño completo de `/announce` (staff) alrededor de un solo campo de identificación con detección automática de formato, que resuelve a la persona correcta con el mínimo de tecleo y de clics posible, y termina siempre en una de dos acciones: **Anunciar** o **Recibir** (que además dispara de inmediato el flujo de recepción, sin tener que ir a buscar el paquete después en `/paquetes`). El caso de "declarar un apartamento sin anunciar nada" se muda por completo a `/residentes`, con un enlace directo desde `/announce` para quien lo necesite.

Como prerrequisito de dominio, esta pantalla necesita que una Persona pueda existir con **usuario de WhatsApp en vez de Teléfono** (hoy el Teléfono es obligatorio sin excepción, ADR-0003) — el cliente decidió explícitamente habilitar esto, incluyendo que una Persona solo-WhatsApp pueda ser Ocupante **principal** de su unidad. Login/OTP y notificaciones automáticas para una Persona así quedan fuera de alcance (dependen de un canal de envío por WhatsApp que todavía no existe) — es una limitación conocida y aceptada, no un bug.

### Secuencia de implementación

Este spec cubre dos rebanadas relacionadas pero de riesgo distinto, y el cliente pidió explícitamente que se sequencien así al pasar por `/to-tickets`:

1. **Primero, como base:** el cambio de dominio (Persona acepta Teléfono o WhatsApp) — Seam A + Seam B, sin ninguna superficie nueva de UI.
2. **Después:** la pantalla nueva de `/announce` sobre esa base — Seam C.

## User Stories

### Identificación (campo único inteligente)

1. Como staff, quiero un solo campo de texto arriba de todo en `/announce`, con foco automático al cargar la página, para no tener que elegir de antemano qué tipo de dato voy a escribir.
2. Como staff, quiero que escribir un número que empieza en `3` (teléfono celular colombiano) dispare la búsqueda por Teléfono automáticamente, sin tener que indicar que es un teléfono.
3. Como staff, quiero que escribir un código que empieza en `0` o `1` (Torre+Apartamento) dispare la búsqueda de esa unidad automáticamente, sin tener que indicar que es Torre+Apartamento.
4. Como staff, quiero que escribir texto que empieza con una letra dispare la búsqueda por usuario de WhatsApp automáticamente, sin tener que indicar que es un usuario de WhatsApp.
5. Como desarrollador, quiero que la detección de formato se vuelva a aplicar en el servidor (no solo confiar en lo que el cliente clasificó), para que la clasificación final sea siempre la misma sin importar el JS del navegador.
6. Como staff, quiero armar el código de Torre+Apartamento como Torre de 2 dígitos (`01`–`10`) seguido del número de Apartamento tal cual (ej. `01106` = Torre 1 / Apto 106, `041304` = Torre 4 / Apto 1304), para no tener que recordar un separador ni el formato exacto de cada torre.
7. Como staff, quiero que la búsqueda de Torre+Apartamento se dispare automáticamente en cuanto los dígitos tecleados calzan EXACTO con una unidad real del catálogo, sin tener que presionar Enter ni ningún botón.
8. Como desarrollador, quiero un debounce defensivo corto (~150ms) tras el último dígito antes de disparar esa búsqueda, para no quedar expuesto si en el futuro el catálogo dejara de cumplir la garantía de "ningún código válido es prefijo de otro" (hoy sí la cumple, verificado contra las 804 unidades reales).

### Teléfono / WhatsApp ya registrados

9. Como staff, quiero que un Teléfono o usuario de WhatsApp que coincide con una Persona ya registrada resuelva directo a esa Persona, sin pasos intermedios.
10. Como staff, quiero que un Teléfono que NO coincide con ninguna Persona registrada cree una Persona nueva ahí mismo (pidiéndome el Nombre), igual que ya pasa hoy — sin apartamento asociado todavía.
11. Como staff, quiero que un usuario de WhatsApp que NO coincide con ninguna Persona registrada cree una Persona nueva solo-WhatsApp ahí mismo (pidiéndome el Nombre), sin apartamento asociado todavía.

### Torre + Apartamento

12. Como staff, quiero ver la lista de residentes activos de la unidad en cuanto el código de Torre+Apartamento resuelve, para elegir directo a quién pertenece el paquete si ya está registrado.
13. Como staff, quiero que la opción "Nueva persona" esté SIEMPRE visible junto a la lista de residentes (exista la lista o no), para cubrir tanto una unidad vacía como una unidad con residentes donde el paquete es para alguien nuevo (un familiar, un arrendatario).
14. Como staff, quiero que "Nueva persona" me pida Nombre + un campo de contacto único (el mismo campo inteligente Teléfono/WhatsApp), para no tener dos inputs separados.
15. Como staff, quiero que el residente que acabo de agregar quede disponible de inmediato para anunciarle un paquete, aunque todavía no esté confirmado, para no tener que esperar ningún paso administrativo antes de poder atenderlo.
16. Como desarrollador, quiero que agregar un residente nuevo desde `/announce` reutilice `agregar_ocupante` tal cual existe hoy (nace `pending`, sin `es_principal`), sin ningún cambio de comportamiento ahí.
17. Como desarrollador, quiero que la regla "si ya hay un Principal, el próximo en confirmarse queda Secundario" siga resuelta enteramente por `confirmar_ocupante` (sin cambios), y que `/announce` no duplique ni reimplemente esa lógica.
18. Como staff o Principal ya confirmado, quiero seguir siendo yo quien confirma un residente `pending` agregado desde `/announce` (vía el flujo que ya existe en `/residentes`/`/mis-datos`), sin que `/announce` agregue una superficie de confirmación propia.

### Identificar y decidir (Anunciar / Recibir)

19. Como staff, quiero que un clic/tap sobre un residente de la lista (o la resolución directa de Teléfono/WhatsApp) muestre de inmediato dos botones — Anunciar y Recibir — sin un paso de "seleccionar y luego confirmar" aparte.
20. Como staff, quiero que "Anunciar" deje el paquete en estado `ANUNCIADO`, igual que el flujo de hoy.
21. Como staff, quiero que "Recibir" anuncie el paquete Y abra de inmediato el formulario completo de recepción (guía con escáner, tipo, condición, fotos) para ESE paquete recién creado, para no tener que ir a buscarlo después en `/paquetes`.
22. Como desarrollador, quiero que el formulario de recepción que se abre desde "Recibir" sea el MISMO componente que ya usa `/paquetes` (mismo escáner ZXing, mismos campos), no una reimplementación aparte.
23. Como staff, quiero que tras "Anunciar" (no "Recibir") aparezca un toast de confirmación con a nombre de quién quedó anunciado y el código de acceso, el formulario se limpie solo, y el foco vuelva al campo principal, para poder anunciar el siguiente paquete de inmediato sin tocar el mouse.

### Fuera de "solo declarar apartamento"

24. Como staff, quiero que `/announce` ya no ofrezca la opción de "solo declarar el apartamento sin anunciar nada" — esa vía queda en `/residentes`.
25. Como staff, quiero un enlace directo desde `/announce` hacia el flujo de `/residentes` para registrar residentes sin que haya un paquete de por medio.

### Dominio: Persona acepta Teléfono o WhatsApp

26. Como desarrollador, quiero que `Persona.telefono` pase a ser nullable, exigiendo que Teléfono o `whatsapp_usuario` estén presentes (nunca los dos vacíos a la vez), para poder representar una Persona identificada solo por WhatsApp.
27. Como desarrollador, quiero un índice único parcial sobre `whatsapp_usuario` (cuando no es nulo), para que dos Personas no puedan compartir el mismo usuario de WhatsApp — mismo criterio de unicidad que ya tiene el Teléfono.
28. Como desarrollador, quiero una función `get_or_create_persona_por_whatsapp` simétrica a `get_or_create_persona`, para resolver o crear una Persona por su usuario de WhatsApp.
29. Como desarrollador, quiero que `paquete_service.announce` acepte identificar al Anunciante por Teléfono O por usuario de WhatsApp (exactamente uno de los dos), para que un anuncio pueda originarse desde una Persona solo-WhatsApp.
30. Como desarrollador, quiero que `Paquete.announced_by_phone` pase a ser nullable (queda `NULL` cuando el Anunciante no tiene Teléfono), sin tocar `announced_by_persona_id` (que sigue apuntando a la Persona real, tenga o no Teléfono).
31. Como owner, quiero que el límite de "máx. 10 anuncios activos por Teléfono" simplemente no aplique a un Anunciante solo-WhatsApp por ahora (no hay Teléfono contra el cual contar), dejando un límite equivalente por WhatsApp fuera de esta rebanada.
32. Como desarrollador, quiero un nuevo constructor `Destinatario.ocupante(ocupante_id)` que generalice la resolución que hoy hace `_resolver_ocupante_por_nombre` (identificar a un Ocupante puntual y resolver su nombre/teléfono de notificación, cayendo al Teléfono del Principal si el Ocupante no tiene contacto propio), para que `/announce` lo use al anunciar a un residente elegido de la lista de Torre+Apartamento.
33. Como Principal solo-WhatsApp, quiero poder ser promovido a principal igual que cualquier otro Ocupante con contacto propio (Teléfono o WhatsApp), aunque hoy no pueda loguearme ni recibir notificaciones automáticas.
34. Como desarrollador, quiero que `promover_a_principal`/`confirmar_ocupante` dejen de exigir específicamente `persona_id` con Teléfono, y pasen a exigir solo que la Persona tenga Teléfono O `whatsapp_usuario` (cualquier Persona real basta).
35. Como arquitecto, quiero un ADR nuevo que documente esta relajación de ADR-0003 (por qué el WhatsApp pasa a ser una llave alterna válida, y qué queda expresamente sin resolver — login/notificaciones), para que la decisión quede trazable igual que el resto del dominio.
36. Como desarrollador, quiero que `CONTEXT.md` (glosario de Persona/Ocupante e invariante "el Teléfono nunca falta") se actualice para reflejar que la llave real es "Teléfono o WhatsApp", no solo Teléfono.

## Implementation Decisions

### Detección de formato (cliente Y servidor)

- Reglas, aplicadas en ambos lados (cliente para decidir cuándo disparar la búsqueda; servidor como autoridad final de qué significa el valor recibido):
  - Empieza en `3`, todo dígitos → candidato Teléfono. Se valida/normaliza con `normalizar_telefono` (ya existe) — si no calza como celular colombiano válido de 10 dígitos, no resuelve nada (el staff sigue escribiendo).
  - Empieza en `0` o `1`, todo dígitos → candidato Torre+Apartamento. Se parte en los primeros 2 dígitos (Torre, `"01"`..`"10"` → `"TORRE 1"`..`"TORRE 10"`) y el resto tal cual (número de Apartamento) — se intenta resolver contra `resolver_apartamento` (ya existe); si no calza con ninguna unidad real, no resuelve nada todavía.
  - Empieza con una letra → candidato usuario de WhatsApp. Se normaliza igual que ya hace `update_datos_personales` (recorta `@` inicial) antes de buscar.
  - Cualquier otro caso (vacío, empieza en `2`/`4`-`9`, símbolos) → sin candidato, no se dispara nada.
- Endpoint nuevo bajo `/announce` (nombre a criterio de quien implemente, ej. `GET /announce/identificar`) que recibe el valor crudo tecleado, re-aplica estas reglas server-side, y devuelve un fragmento HTML: la lista de residentes + "Nueva persona" (caso Torre+Apto), la Persona resuelta con sus botones Anunciar/Recibir (caso Teléfono/WhatsApp con match), el formulario de "Persona nueva" pre-listo (caso Teléfono/WhatsApp sin match, o Torre+Apto con unidad vacía), o nada (sin candidato aún). Mismo patrón de fragmento-reemplaza-`innerHTML` que ya usa la búsqueda en vivo de `/paquetes` (`paquetes-busqueda-viva`).
- Debounce de ~150ms tras el último carácter tecleado, aplicado a TODOS los candidatos (no solo Torre+Apto) — evita ráfagas de requests mientras el staff sigue escribiendo un Teléfono o un usuario de WhatsApp largo.

### Torre + Apartamento → residentes

- Reutiliza `listar_ocupantes` (ya existe, activos primero el Principal) para la lista.
- "Nueva persona" siempre presente junto a la lista (o sola, si la unidad está vacía) — Nombre + campo inteligente Teléfono/WhatsApp.
- Alta de residente nuevo reutiliza `agregar_ocupante` sin cambios (exige Teléfono O WhatsApp si es el primero de la unidad — ver más abajo el ajuste a esa exigencia).
- Elegir un residente de la lista (clic/tap) resuelve el Destinatario vía el nuevo `Destinatario.ocupante(ocupante_id)` (ver Dominio abajo) y revela Anunciar/Recibir.

### Anunciar / Recibir

- Ambos botones llaman a `announce()` (con el Destinatario ya resuelto por cualquiera de los 3 criterios). La diferencia es solo lo que pasa DESPUÉS:
  - Anunciar: toast de confirmación (nombre + código de acceso), reset del formulario, foco de vuelta al campo principal.
  - Recibir: mismo `announce()`, y a continuación se muestra inline el formulario de recepción ya existente (el mismo componente/JS que usa `/paquetes` para "Recibir" — escáner ZXing de guía, Tipo, Condición, hasta 3 fotos), scoped al `paquete_id` recién creado. Completar ese formulario transiciona el paquete a `RECIBIDO` con el mismo `receive()` de siempre.
- "Solo declarar apartamento" desaparece de `/announce`. Un enlace visible lleva a `/residentes` para ese caso.

### Dominio: Persona acepta Teléfono o WhatsApp

- Migración: `personas.telefono` pasa a nullable. Constraint nueva a nivel de base de datos: `CHECK (telefono IS NOT NULL OR whatsapp_usuario IS NOT NULL)`. Índice único parcial nuevo sobre `whatsapp_usuario` (`WHERE whatsapp_usuario IS NOT NULL`), mismo estilo que `uq_ocupantes_principal_por_apartamento`.
- Migración: `paquetes.announced_by_phone` pasa a nullable. `announced_by_persona_id` **no cambia** (sigue `NOT NULL` — toda Persona, tenga Teléfono o WhatsApp, sigue siendo una fila real referenciable por FK).
- `persona_service.get_or_create_persona_por_whatsapp(session, whatsapp_usuario, nombre)`: mismo contrato que `get_or_create_persona`, pero busca/crea por `whatsapp_usuario` normalizado (reutiliza la misma validación/normalización que ya usa `update_datos_personales`).
- `paquete_service.announce`: gana una vía alterna para identificar al Anunciante — Teléfono (como hoy) o `whatsapp_usuario` (nuevo), exactamente uno de los dos. Internamente resuelve la Persona con el `get_or_create_*` que corresponda.
- `Destinatario.ocupante(ocupante_id)`: constructor nuevo. `announce()` resuelve: si el Ocupante tiene Persona propia (Teléfono o WhatsApp), el Destinatario es esa Persona; si no, cae al mismo mecanismo que ya usa `telefono_notificacion_ocupante` (Teléfono/WhatsApp del Principal activo de la misma unidad) para el contacto de notificación, conservando el nombre propio del Ocupante como `recipient_name` — mismo criterio que hoy aplica `_resolver_ocupante_por_nombre` dentro del caso `DECLARADO_POR_CLIENTE`, generalizado a un constructor propio en vez de resolución implícita por nombre.
- `ocupante_service.promover_a_principal`/`confirmar_ocupante`: el guard "sin Teléfono no puede ser Principal" pasa a "sin Teléfono NI WhatsApp no puede ser Principal" — cualquier Persona real (con cualquiera de los dos) puede ser promovida.
- `agregar_ocupante`: la exigencia de "el primer Ocupante de una unidad vacía debe tener Teléfono" pasa a "debe tener Teléfono o WhatsApp".
- Nuevo `docs/adr/0007-*.md` documentando esta relajación de ADR-0003 (qué cambia, qué NO — login/OTP y notificaciones automáticas siguen exigiendo Teléfono real, sin excepción, hasta que exista un canal de envío por WhatsApp). Actualización de `CONTEXT.md`: sección Persona/Ocupante e invariante 1 ("El Teléfono es la llave universal") pasan a reflejar "Teléfono o WhatsApp".

## Testing Decisions

Un buen test acá verifica comportamiento observable (qué Persona/Ocupante queda en la base, qué Paquete queda anunciado, qué aparece en la respuesta HTTP) — no la forma interna de la query SQL, mismo criterio que el resto del repo.

### Seam A — servicios de dominio (pytest contra Postgres efímero real, `alembic upgrade head`)

- `test_persona_service.py` (se extiende, ya tiene tests de `whatsapp_usuario`): crear Persona solo con `whatsapp_usuario` (sin Teléfono) funciona; crear Persona sin Teléfono NI WhatsApp falla; `get_or_create_persona_por_whatsapp` reutiliza la misma Persona en llamadas repetidas con el mismo usuario (con/sin `@`); dos Personas no pueden compartir el mismo `whatsapp_usuario` (constraint observable).
- `test_announce_paquete.py` (se extiende): `announce()` con Anunciante identificado por `whatsapp_usuario` (sin Teléfono) deja `announced_by_phone` en `NULL` y `announced_by_persona_id` apuntando a la Persona correcta; `Destinatario.ocupante(id)` resuelve nombre + Teléfono/WhatsApp de notificación igual que hoy hace la resolución por nombre, incluida la caída al Principal cuando el Ocupante no tiene contacto propio.
- `test_ocupante_service.py` (se extiende): un Ocupante solo-WhatsApp puede promoverse a Principal; `confirmar_ocupante` promueve a un Ocupante solo-WhatsApp como primer Principal de una unidad vacía; `agregar_ocupante` acepta el primer Ocupante de una unidad vacía con solo `whatsapp_usuario` (sin Teléfono).

### Seam B — grafo de migración (aserción delgada)

- `upgrade head` → `downgrade base` limpio sobre Postgres vacío para la migración de `personas`/`paquetes`.
- Insertar una Persona con `telefono=NULL, whatsapp_usuario='algo'` funciona; insertar con ambos `NULL` viola la constraint; dos filas con el mismo `whatsapp_usuario` violan el índice único.

### Seam C — HTTP vía `TestClient` (extiende `test_announce_new.py`)

- El endpoint de identificación devuelve el fragmento correcto para cada uno de los 3 criterios (Teléfono con/sin match, Torre+Apto con/sin residentes, WhatsApp con/sin match), y nada para un valor que no calza con ningún patrón.
- Un código de Torre+Apto incompleto o inválido no dispara ningún resultado (no revienta).
- "Anunciar" sobre un Destinatario resuelto por cada uno de los 3 criterios deja el Paquete en `ANUNCIADO` con el snapshot correcto.
- "Recibir" dispara `announce()` y devuelve/muestra el formulario de recepción para el `paquete_id` correcto; completar ese formulario transiciona a `RECIBIDO` (reusa las aserciones que ya tiene `test_packages.py` para `receive`).
- `/announce` ya no acepta declarar solo el apartamento sin anunciar (el caso se elimina de esta ruta; se verifica que el enlace a `/residentes` esté presente).

### Fuera de la suite automatizada

- Detección de formato en vivo en el navegador (JS), el debounce de 150ms, y que los botones Anunciar/Recibir aparezcan y funcionen tras la resolución — se verifica a mano en navegador real con el skill `run`, mismo criterio que ya se documentó para la búsqueda en vivo de `/paquetes`.

## Out of Scope

- **Envío de notificaciones por WhatsApp** — una Persona solo-WhatsApp no recibe ningún aviso automático todavía (ni de su propio paquete). Es un canal aparte, a construir en una rebanada futura.
- **Login/OTP para Persona solo-WhatsApp** — sigue sin poder loguearse a `/mis-datos` ni a ningún flujo de autogestión; el login sigue exigiendo Teléfono real. Conocido y aceptado por el cliente.
- **Límite de anuncios activos por WhatsApp** (equivalente a `MAX_ANUNCIADOS_ACTIVOS_POR_TELEFONO`) — no se construye en esta rebanada; un Anunciante solo-WhatsApp no tiene tope por ahora.
- **Búsqueda por Nombre** del residente como 4to criterio — el cliente lo dejó explícitamente fuera de esta ronda.
- **Autocompletado/sugerencias mientras se escribe Torre+Apartamento** — se descartó a favor de la resolución por match exacto (ver User Story 7-8).
- **Formulario de "solo declarar apartamento" dentro de `/announce`** — se elimina de esta ruta; vive solo en `/residentes`.
- **Sucesión de Principal** al mudarse/desvincularse — fuera de alcance, ya diferido en `apartamento-catalogo-confirmacion` y no se reabre acá.
- **Migración de datos existentes** de Personas ya creadas — no aplica, el cambio de esquema es puramente aditivo (nullable + constraint), ninguna fila existente puede violar la constraint nueva (todas ya tienen Teléfono).

## Further Notes

- **Reabre ADR-0003** ("El Teléfono es la llave universal de la Persona") — la opción que esa ADR rechazaba explícitamente ("Surrogate-id con teléfono nullable... reintroduce personas sin llave") se acepta ahora de forma acotada: el Teléfono sigue siendo la llave preferida y la única que habilita login/notificaciones, pero deja de ser la ÚNICA llave posible — WhatsApp es una alterna válida y con la misma garantía de unicidad. El ADR nuevo (0007) debe dejar explícito que esto NO reabre la opción rechazada de "id opaco sin ninguna llave" — sigue exigiéndose Teléfono O WhatsApp, nunca ninguno de los dos.
- CONTEXT.md necesita actualizarse en la misma rebanada que la migración (no como afterthought): sección Persona, sección Ocupante (línea que hoy dice "Teléfono obligatorio" para el Principal) y el invariante 1 ("El Teléfono es la llave universal... nunca falta").
- El endpoint de identificación de `/announce` reaplica la detección de formato en el servidor aunque el cliente ya la haya hecho — es intencional (el cliente decide CUÁNDO preguntar, el servidor decide QUÉ significa la respuesta), no una duplicación de lógica de negocio a limpiar.
- El mecanismo exacto de "mostrar el formulario de recepción inline tras Recibir" (fetch + swap vs. redirect) queda a criterio de quien implemente esa ficha — el requisito duro es que reuse el componente de recepción existente, no que lo reimplemente.

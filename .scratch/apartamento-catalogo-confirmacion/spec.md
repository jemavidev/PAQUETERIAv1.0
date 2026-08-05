Status: ready-for-agent
Feature: apartamento-catalogo-confirmacion
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · `.scratch/data-model/spec.md` (Apartamento/Ocupante base) · `docs/adr/0006-ocupante-residentes-sin-persona-propia.md` (no se reabre) · `.scratch/ocupante-entidad/spec.md` y `.scratch/mis-datos/issues/{01,02,03,04,10}` (funcionalidad ya construida que este spec extiende, no reemplaza)

---

## Problem Statement

Hoy `Apartamento` (`apartamento_service.get_or_create_apartamento`) crea una unidad nueva la primera vez que alguien escribe cualquier combinación de Torre/Apartamento — texto libre, sin catálogo. El cliente ya tiene el listado real y cerrado de las 804 unidades que existen en el conjunto (10 torres) y no quiere que el sistema seguir aceptando cualquier valor: los errores de digitación crean unidades fantasma, y cualquiera puede declararse residente de un apartamento que no es el suyo con solo escribir el número correcto — no hay ninguna verificación humana de por medio.

Por separado, el sistema de Ocupantes (ADR-0006, ya implementado y en producción de código — `ocupante_service.py`, tickets `.scratch/mis-datos/{01,02,03,04,10}`, todos `Status: done`) deja que el principal o el staff agreguen un Ocupante nuevo y este queda **activo de inmediato**, incluyendo el primer Ocupante de un apartamento vacío, que se marca `es_principal` automáticamente sin que nadie lo verifique. No hay ningún paso de confirmación humana entre "alguien dice que vive ahí" y "el sistema lo trata como residente real" — para el cliente, ese es el hueco real de suplantación, más que el catálogo en sí.

## Solution

Dos cambios, decididos juntos en la misma sesión de diseño porque ambos atacan el mismo problema (evitar que alguien quede asociado a un apartamento que no es el suyo):

1. **Catálogo cerrado de Apartamento.** Las 804 unidades reales del conjunto (ver catálogo completo al final de este documento) se siembran una vez vía migración Alembic, bajo el nombre de Conjunto vigente en ese momento (ver punto 3). `get_or_create_apartamento` deja de crear: pasa a **resolver contra el catálogo sembrado**, y falla explícitamente si la terna Torre/Apartamento no existe ahí. Cualquier UI que hoy captura Torre/Apartamento como texto libre pasa a ofrecer una lista de estas 804 unidades.

2. **Confirmación de Ocupante.** Todo Ocupante nuevo — **incluido el primero de un apartamento vacío** — nace `pending` (sin confirmar), sin excepción y sin auto-promoción a principal en el momento de crearse. Un Ocupante `pending` **no pierde ninguna funcionalidad**: ya puede anunciar y recibir paquetes en esa unidad desde el instante en que se registra — la confirmación es un sello administrativo posterior, no una puerta de acceso. Confirmar es una acción explícita que solo puede tomar el Ocupante **principal ya confirmado** del apartamento, o cualquier miembro del **staff**. El primer Ocupante confirmado de un apartamento vacío se vuelve principal automáticamente **en el momento de la confirmación** (no antes). Rechazar un pending simplemente lo retira (reutiliza `dar_de_baja_ocupante`, que ya nunca borra la fila — queda como Ocupante que nunca llegó a confirmarse).

3. **Conjunto como configuración global administrable.** El nombre del Conjunto ("El Club" hoy) deja de ser un valor fijo del seed: es un **único dato global** que solo el rol `ADMIN` puede fijar o renombrar, desde una pantalla nueva de configuración. Es un singleton — hoy y siempre existe exactamente un Conjunto en el sistema, no una lista de varios. Renombrarlo propaga (una sola operación) a las 804 filas de `apartamentos` que ya lo referencian, para que ninguna quede con el nombre viejo. Como consecuencia, `conjunto` deja de ser un dato que el residente o el staff escriben o eligen en ningún formulario — es implícito, no se les pregunta.

La sucesión de quién se vuelve principal cuando el actual se muda o se desvincula **queda fuera de esta rebanada** — es un problema distinto (mudanza), no de confirmación, y el cliente pidió explícitamente diferirlo. El comportamiento actual de `dar_de_baja_ocupante` (el principal no puede darse de baja mientras haya otros Ocupantes activos, sin decir automáticamente quién lo reemplaza) no cambia.

### Seam

Esta rebanada **no abre una costura nueva**: extiende la Seam A ya establecida por `.scratch/data-model/spec.md` y usada por todo lo que toca Apartamento/Ocupante — el módulo de servicio de dominio (`apartamento_service.py`, `ocupante_service.py`), probado con pytest contra un Postgres efímero real levantado con `alembic upgrade head`. Prior art directo: `CODE/tests/data_model/test_apartamento_service.py`, `test_ocupante_service.py`. No hace falta ninguna ruta HTTP nueva más allá de exponer las funciones de dominio nuevas desde las pantallas que ya gestionan Ocupantes (`/mis-datos`, `/residentes/{id}`), siguiendo el mismo patrón que los tickets 03/10 de `.scratch/mis-datos/`.

## User Stories

1. Como residente, quiero elegir mi Torre y Apartamento de una lista preseleccionada de las 804 unidades reales del conjunto, para no equivocarme al escribirlo a mano.
2. Como staff, quiero que declarar un apartamento para un residente solo permita elegir entre las unidades reales del conjunto, para no crear registros con torres o apartamentos que no existen.
3. Como arquitecto, quiero que el catálogo de las 804 unidades quede sembrado por una migración Alembic, para que cualquier ambiente nuevo (CI, staging, producción) arranque exactamente con el mismo catálogo cerrado.
4. Como desarrollador, quiero que resolver una terna Torre/Apartamento que no está en el catálogo falle explícitamente, para que ningún flujo cree apartamentos fantasma por error de integración o de digitación.
5. Como owner, quiero que nunca se puedan crear más apartamentos que las 804 unidades acordadas, para que el catálogo del conjunto no se desvíe de la realidad con el tiempo.
6. Como residente, quiero poder reclamar un apartamento del catálogo con mi teléfono aunque todavía nadie lo haya confirmado, para no quedar bloqueado esperando a que otra persona actúe.
7. Como residente que acaba de reclamar un apartamento, quiero poder anunciar y recibir paquetes en esa unidad desde el primer momento, aunque mi reclamo siga pendiente de confirmación, para no perder funcionalidad mientras se verifica.
8. Como staff, quiero ver cuáles Ocupantes de un apartamento están pendientes de confirmación, para saber a quién todavía hace falta verificar.
9. Como staff, quiero poder confirmar el reclamo de un residente sobre un apartamento, para dejar constancia de que se verificó que realmente vive ahí.
10. Como Ocupante principal ya confirmado, quiero poder confirmar yo mismo a un conviviente que se registra después, para no depender siempre de que el staff intervenga.
11. Como staff, quiero poder confirmar cualquier reclamo pendiente, incluso el de un apartamento que todavía no tiene principal, para poder desbloquear el primer registro de una unidad vacía.
12. Como residente, quiero que ser el primero en reclamar un apartamento vacío NO me convierta automáticamente en principal, para que la verificación humana siga siendo obligatoria incluso en ese caso.
13. Como residente que fue confirmado como el primer Ocupante de un apartamento, quiero volverme principal automáticamente en ese mismo momento, para no necesitar un paso manual adicional de "ahora asígnenme principal".
14. Como staff, quiero poder rechazar el reclamo de alguien que dice vivir en un apartamento pero no es cierto, para mantener confiable el padrón de residentes.
15. Como residente cuyo reclamo fue rechazado, quiero conservar mi teléfono/identidad normalmente, para poder volver a intentar asociarme al apartamento correcto sin perder mi cuenta.
16. Como Ocupante principal confirmado, quiero que un reclamo pendiente de un desconocido en mi apartamento no lo vuelva parte de mi unidad automáticamente, para que solo entre gente real cuando yo o staff lo verifiquemos.
17. Como owner, quiero que el límite de 5 Ocupantes activos por apartamento cuente también a los pendientes, para que nadie sature una unidad con reclamos sin confirmar y evada el límite real.
18. Como desarrollador, quiero que el estado pending/confirmado se registre con el mismo estilo que el resto del dominio de Ocupante (marca de tiempo nullable, la fila nunca se borra), para mantener la misma filosofía de histórico inmutable ya usada en `desvinculado_en`.
19. Como staff, quiero distinguir visualmente en `/residentes/{id}` cuáles Ocupantes están confirmados y cuáles pending, para priorizar mi trabajo de verificación.
20. Como residente, quiero ver en `/mis-datos` si mi propia asociación al apartamento sigue pendiente de confirmación, para saber que falta un paso administrativo aunque ya pueda usar el sistema con normalidad.
21. Como desarrollador, quiero que un actor que no es ni el principal confirmado del apartamento ni staff no pueda confirmar ni rechazar un reclamo ajeno, para que la verificación siga siendo un privilegio real, no una acción abierta a cualquiera.
22. Como administrador, quiero poder fijar y renombrar el nombre del Conjunto desde una pantalla de configuración, para mantenerlo correcto sin tocar la base de datos a mano.
23. Como administrador, quiero que solo mi rol (`ADMIN`, no `OPERADOR`) pueda cambiar el nombre del Conjunto, para que ese dato no lo toque cualquier miembro del staff.
24. Como residente o staff, quiero que el Conjunto nunca me lo pregunten al declarar una Torre/Apartamento, para no tener que saber ni escribir un dato que ya es el mismo para todos.
25. Como desarrollador, quiero que renombrar el Conjunto actualice las 804 filas de Apartamento en la misma operación, para que ninguna quede mostrando el nombre anterior.

## Implementation Decisions

### Conjunto: configuración global administrable

- Entidad nueva y liviana, un único registro vigente en todo momento (singleton — no una lista): guarda el nombre actual del Conjunto. Valor por defecto: **"El Club"** — implementado como tabla de override (mismo patrón que `PlantillaNotificacion`): sin fila, el dominio devuelve ese default hardcodeado; la fila solo aparece cuando un ADMIN renombra por primera vez (ticket 01, ya implementado).
- Función de dominio para leer el nombre vigente, y una para renombrarlo — esta última exige `actor` de rol `ADMIN` (reusa `require_admin`, el mismo guard ya usado en `/administracion/personal`); `OPERADOR` queda rechazado.
- Renombrar es una sola operación transaccional: actualiza el registro singleton **y** hace `UPDATE` en bloque de `apartamentos.conjunto` para las 804 filas — nunca quedan desincronizadas.
- Pantalla nueva bajo `/administracion` (mismo árbol que `/administracion/personal`), con un campo de texto + guardar — sin lista, sin crear/borrar múltiples Conjuntos, solo fijar/editar el único valor vigente.
- `get_or_create_apartamento` deja de tomar `conjunto` como argumento del llamador: lo resuelve internamente contra este valor global. Ni `/mis-datos` ni `/announce-new` vuelven a pedirle Conjunto al residente o al staff — ambos formularios pasan a capturar solo Torre + Apartamento.

### Catálogo cerrado de Apartamento

- Migración Alembic nueva que siembra exactamente 804 filas en `apartamentos` — la terna `(conjunto, torre, apartamento)` normalizada de cada unidad, tal como quedó verificada con el cliente en esta sesión (10 torres; ver catálogo completo al final de este documento). El valor de `conjunto` es el nombre vigente en el registro singleton del punto anterior ("El Club" al momento de escribir este spec) — la migración de seed corre después de sembrar ese registro, nunca antes.
- `apartamento_service.get_or_create_apartamento` cambia de semántica: de "crear si no existe" a **"resolver contra el catálogo sembrado, fallar si la terna no está"** (mismo estilo de `ValueError` que ya usa el módulo para ternas incompletas). Ningún llamador nuevo puede crear un Apartamento fuera de la migración de seed — el nombre de la función puede conservarse o ajustarse a la nueva semántica, a criterio de quien implemente.
- `buscar_apartamento_por_terna` (ya existe, de solo lectura) no cambia — sigue devolviendo `None` si no hay match, útil para los flujos que hoy la usan (Grupo 16, "Corregir").
- Los dos puntos reales de captura libre hoy son `/mis-datos` (residente, `customer_verify.py`) y `/announce-new` (staff, `announce_new.py`, donde hoy además el staff escribe Conjunto a mano). Ambos pasan a ofrecer las 804 unidades como selección de Torre + Apartamento (sin Conjunto, ver punto anterior). En `/mis-datos` esto además retira el candado actual "Tu conjunto todavía no ha sido asignado por el staff" (`customer_verify.py:228-247`) — dejaba de tener sentido: con catálogo cerrado y Conjunto único ya no hace falta que el staff "asigne" nada antes de que el residente pueda declarar su unidad.

### Confirmación de Ocupante

- Columna nueva `Ocupante.confirmado_en` (DateTime nullable), mismo patrón que `desvinculado_en`: `NULL` = pending, con fecha = confirmado en ese instante.
- `ocupante_service.agregar_ocupante` deja de marcar `es_principal=True` para el primer Ocupante de un apartamento vacío. Todo Ocupante nuevo nace `confirmado_en=None`, `es_principal=False`, sin excepción — el resto de su comportamiento actual (exige teléfono si es el primero de la unidad, respeta `MAX_OCUPANTES_ACTIVOS=5`, sincroniza `apartamento_actual_id`) no cambia.
- Función nueva `confirmar_ocupante(session, ocupante, actor)`:
  - Válido solo si `actor` es el Ocupante principal **ya confirmado** del mismo apartamento, o un `Usuario` de staff (`ADMIN`/`OPERADOR`, sin distinción — mismo patrón que el resto de gestión de Ocupantes). Cualquier otro actor: rechazado.
  - Marca `confirmado_en = ahora`.
  - Si el apartamento **no tiene ningún Ocupante con `es_principal=True`** en este momento, este Ocupante se marca `es_principal=True` como parte de la misma operación (reemplaza la auto-promoción que hoy pasa en `agregar_ocupante`, solo que ahora ocurre al confirmar, no al crear).
  - Si el apartamento ya tiene un principal confirmado, confirmar a otro Ocupante no lo toca — `es_principal` sigue igual.
- Rechazar un reclamo pending reutiliza `dar_de_baja_ocupante` tal cual existe hoy — no se crea una función nueva. Un Ocupante rechazado queda con `desvinculado_en` marcado y `confirmado_en` en `NULL` para siempre, lo que por sí solo distingue "nunca llegó a confirmarse" de "fue Ocupante confirmado y luego se fue".
- `MAX_OCUPANTES_ACTIVOS=5` sigue contando por `desvinculado_en IS NULL`, sin filtrar por `confirmado_en` — un pending ya ocupa cupo real, tal como ya funciona hoy para cualquier Ocupante activo.
- Nada de esto toca `Persona.apartamento_actual_id`: sigue asignándose en el mismo momento que hoy (`agregar_ocupante`/`asociar_telefono_a_ocupante`), así que anunciar/recibir paquetes de un Ocupante pending sigue funcionando exactamente igual que para uno confirmado — la confirmación no es un gate funcional, es un sello para el staff.
- Superficie de UI: `/mis-datos` (principal) y `/residentes/{id}` (staff) — que ya listan y gestionan Ocupantes (tickets 03/10 de `.scratch/mis-datos/`) — muestran el estado pending/confirmado de cada uno y agregan las acciones "Confirmar"/"Rechazar" donde el actor tenga permiso, reusando el patrón de rutas ya existente (`_ocupante_gestionable_por` para el principal, `current_staff` para staff).

## Testing Decisions

Mismo criterio que el resto del dominio: probar comportamiento observable a través del servicio (Seam A), no detalles de columnas. Prior art directo: `test_apartamento_service.py`, `test_ocupante_service.py` — se extienden, no se crean archivos nuevos salvo que crezcan demasiado.

- **Conjunto:** leer el nombre vigente devuelve "El Club" recién sembrado; `ADMIN` puede renombrarlo y la lectura posterior refleja el nuevo nombre; `OPERADOR` (o un actor sin sesión de staff) intentando renombrar es rechazado; renombrar con 804 filas ya sembradas deja las 804 con el nombre nuevo, ninguna con el viejo.
- **Catálogo:** resolver una terna válida del catálogo devuelve el Apartamento sembrado (sin crear filas nuevas); resolver una terna fuera del catálogo lanza `ValueError` y no crea nada; dos formatos de la misma terna válida (casing/espacios distintos) resuelven al mismo Apartamento.
- **Migración (Seam B, aserción delgada):** `alembic upgrade head` sobre Postgres vacío deja exactamente 804 filas en `apartamentos`; `downgrade` revierte limpio.
- **Confirmación:** `agregar_ocupante` sobre un apartamento vacío crea un Ocupante `pending`, `es_principal=False` (ya no auto-promueve); `confirmar_ocupante` por staff sobre ese primer Ocupante lo marca `confirmado_en` y lo promueve a principal en la misma operación; `confirmar_ocupante` por el principal ya confirmado sobre un segundo Ocupante lo confirma sin tocar quién es principal; un actor que no es principal confirmado ni staff intentando confirmar es rechazado; `dar_de_baja_ocupante` sobre un pending lo retira dejando `confirmado_en` en `NULL` para siempre; un Ocupante pending ya cuenta para `MAX_OCUPANTES_ACTIVOS=5`; un Ocupante pending puede ser resuelto igual que uno confirmado por los flujos que ya dependen de `apartamento_actual_id` (anunciar/recibir).

## Out of Scope

- **Sucesión del principal** al mudarse o desvincularse — el cliente lo difirió explícitamente en esta sesión; el comportamiento actual de `dar_de_baja_ocupante` (bloquea al principal mientras haya otros Ocupantes activos) no cambia.
- **Notificaciones** de "tienes un reclamo pendiente por confirmar" (push/SMS/WhatsApp) — esta rebanada solo define el estado y las acciones de dominio; el aviso activo es una rebanada aparte si el cliente lo pide.
- **Migración de datos existentes** — no aplica: se verificó en vivo (staging y producción, solo lectura) que las tablas `personas`/`apartamentos`/`ocupantes` todavía no existen en ninguna de las dos bases — este modelo vive solo en el branch `PaqueteXv.2`, sin datos reales que reconciliar.
- **Expiración por tiempo de un pending sin resolver** — no se pidió, no se construye.
- **Múltiples Conjuntos simultáneos** — el cliente confirmó que es y seguirá siendo un único valor global; no se construye ninguna lista, ni crear/borrar Conjuntos — si el negocio cambia a multi-conjunto en el futuro, es una rebanada nueva.
- **Historial de nombres anteriores del Conjunto** — renombrar sobrescribe, no versiona; no se pidió.

## Further Notes

- Este spec **extiende** ADR-0006 y `.scratch/data-model/spec.md` — no reabre ninguna decisión ya aceptada ahí. Las historias #16-19 de `data-model/spec.md` (convivientes compartiendo apartamento vía `declare_unit`/Ocupante) siguen vigentes tal cual: varias personas SÍ pueden compartir una unidad; lo nuevo es que cada una pasa por confirmación antes de que alguien la dé por verificada.
- Verificación en vivo hecha en esta sesión (solo lectura, sin escrituras): 0 filas en `personas`/`apartamentos`/`ocupantes` en staging y producción — confirma que no hay caso real de convivientes ya registrados que migrar.
- El listado original del cliente traía un typo: Torre 3, Piso 3 tenía `303` duplicado (9 valores en vez de 8). Confirmado con el cliente: el piso correcto es `301-308` (8 unidades, igual que su torre gemela, Torre 8) — el catálogo de abajo ya viene con esa corrección aplicada.

### Catálogo completo — 804 unidades (10 torres)

```
TORRE 1
Piso 1: 101, 102, 103, 104, 105, 106
Piso 2: 201, 202, 203, 204, 205, 206
Piso 3: 301, 302, 303, 304, 305, 306
Piso 4: 401, 402, 403, 404, 405, 406
Piso 5: 501, 502, 503, 504, 505, 506
Piso 6: 601, 602, 603, 604, 605, 606
Piso 7: 701, 702

TORRE 2
Piso 1: 101, 102, 103, 104, 105, 106
Piso 2: 201, 202, 203, 204, 205, 206
Piso 3: 301, 302, 303, 304, 305, 306
Piso 4: 401, 402, 403, 404, 405, 406
Piso 5: 501, 502, 503, 504, 505, 506
Piso 6: 601, 602, 603, 604, 605, 606
Piso 7: 701, 702, 703, 704, 705, 706
Piso 8: 801, 802, 803, 804, 805, 806
Piso 9: 901, 902, 903, 904, 905, 906
Piso 10: 1001, 1002

TORRE 3
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304

TORRE 4
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308

TORRE 5
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308

TORRE 6
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308

TORRE 7
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308

TORRE 8
Piso 1: 101, 102, 103, 104, 105, 106, 107, 108
Piso 2: 201, 202, 203, 204, 205, 206, 207, 208
Piso 3: 301, 302, 303, 304, 305, 306, 307, 308
Piso 4: 401, 402, 403, 404, 405, 406, 407, 408
Piso 5: 501, 502, 503, 504, 505, 506, 507, 508
Piso 6: 601, 602, 603, 604, 605, 606, 607, 608
Piso 7: 701, 702, 703, 704, 705, 706, 707, 708
Piso 8: 801, 802, 803, 804, 805, 806, 807, 808
Piso 9: 901, 902, 903, 904, 905, 906, 907, 908
Piso 10: 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008
Piso 11: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108
Piso 12: 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208
Piso 13: 1301, 1302, 1303, 1304

TORRE 9
Piso 1: 101, 102, 103, 104, 105, 106
Piso 2: 201, 202, 203, 204, 205, 206
Piso 3: 301, 302, 303, 304, 305, 306
Piso 4: 401, 402, 403, 404, 405, 406
Piso 5: 501, 502, 503, 504, 505, 506
Piso 6: 601, 602, 603, 604, 605, 606
Piso 7: 701, 702, 703, 704, 705, 706
Piso 8: 801, 802, 803, 804, 805, 806
Piso 9: 901, 902, 903, 904, 905, 906
Piso 10: 1001, 1002

TORRE 10
Piso 1: 101, 102, 103, 104, 105, 106
Piso 2: 201, 202, 203, 204, 205, 206
Piso 3: 301, 302, 303, 304, 305, 306
Piso 4: 401, 402, 403, 404, 405, 406
Piso 5: 501, 502, 503, 504, 505, 506
Piso 6: 601, 602, 603, 604, 605, 606
Piso 7: 701, 702
```

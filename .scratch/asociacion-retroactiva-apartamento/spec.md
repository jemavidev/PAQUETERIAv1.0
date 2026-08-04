Status: ready-for-agent

Origen: `.scratch/pendientes-cliente/issues/44-anunciar-no-resuelve-apartamento-por-nombre-conocido.md`
(paquetes `32TE`/`64E3` reportados por el cliente sin Apartamento resuelto).

## Tickets

Desglosado vía `/to-tickets` — ver `issues/`:

1. `issues/01-deteccion-correccion-paquetes-huerfanos.md` — dominio (sin bloqueos)
2. `issues/02-correccion-automatica-staff-vincula-telefono.md` — bloqueado por 01
3. `issues/03-aviso-autorizacion-manual-residentes.md` — bloqueado por 01 (02 y 03 son paralelos entre sí)

# Asociación retroactiva de Apartamento para Paquetes huérfanos

## Problem Statement

Cuando un Paquete se anuncia, su Apartamento se congela como snapshot en el momento del anuncio
(ADR-0001) — se resuelve a partir del `apartamento_actual` de la Persona relevante. Si esa Persona
(anunciante o destinatario) todavía no tenía ningún Apartamento vinculado en ese instante, el
Paquete queda sin Apartamento **para siempre**: nada en el sistema hoy vuelve a intentar resolverlo,
ni siquiera después de que esa misma Persona se vincule a un Apartamento más tarde (como principal
o como Ocupante).

Esto pasa en un caso real y no raro: un residente anuncia un paquete desde su teléfono antes de
haber declarado su unidad (o de que el principal lo haya agregado como Ocupante). Cuando después
ese teléfono sí queda vinculado a un Apartamento, los paquetes que anunció antes siguen mostrando
"Sin apartamento" — tanto para el propio cliente en `/mis-paquetes` como para el staff en
`/paquetes`, sin ninguna pista de a qué unidad pertenecen en realidad, aunque el sistema ya sepa la
respuesta.

## Solution

Cuando un Teléfono queda vinculado a un Apartamento (como principal o como Ocupante, vía
`/residentes`, `/announce`, o autoservicio en `/mis-datos`), el sistema detecta los Paquetes de ese
Teléfono que están `Anunciado` y sin Apartamento en su snapshot ("Paquetes huérfanos" — término que
introduce este spec). La corrección se aplica de dos formas distintas según quién hizo la
vinculación:

- **Si fue el staff** quien vinculó el Teléfono (en `/residentes` o `/announce`): la corrección se
  aplica en el mismo paso, sin aviso ni confirmación aparte — el staff ya está presente y
  decidiendo.
- **Si fue autoservicio** (el propio residente en `/mis-datos`): la vinculación del Teléfono se
  aplica de inmediato como siempre (no se bloquea), pero la corrección de Paquetes huérfanos NO es
  automática — el staff ve un aviso la próxima vez que abre la ficha de ese cliente/Apartamento en
  `/residentes`, y autoriza (o no) la asociación con un clic por paquete.

Nunca se busca por **nombre** en todo el edificio — la detección es siempre por Teléfono ya
vinculado, para no arriesgar asociar un Paquete al Apartamento equivocado por una coincidencia de
nombre entre dos residentes distintos.

Un Paquete solo es corregible mientras sigue `Anunciado`. Una vez `Recibido`, `Entregado` o
`Cancelado`, su snapshot es tan inmutable como siempre — sin excepción, igual que ya rige hoy para
la corrección de destinatario (ADR-0001).

## User Stories

1. Como staff vinculando un Teléfono nuevo a un Apartamento (agregar un Ocupante o promoverlo en `/residentes`), quiero que el sistema re-asocie automáticamente los Paquetes Anunciados huérfanos de ese Teléfono al Apartamento, para no tener que corregirlos uno por uno a mano.
2. Como staff, quiero que esa re-asociación automática NO me pida una confirmación aparte cuando soy yo quien hace la vinculación, para no duplicar el mismo paso de autorización que ya estoy haciendo.
3. Como staff declarando una unidad completa en lote desde `/announce`, quiero que la misma re-asociación automática aplique a cada Teléfono del grupo, igual que cuando vinculo uno solo desde `/residentes`.
4. Como residente que se auto-registra o declara su Apartamento en `/mis-datos`, quiero que mi vinculación se aplique de inmediato sin quedar bloqueada esperando aprobación de nadie, para no tener fricción en algo tan simple como declarar mi unidad.
5. Como staff, quiero ver un aviso claro cuando abro la ficha de un cliente/Apartamento en `/residentes` y existen Paquetes Anunciados que coinciden por Teléfono con ese Apartamento pero no tienen el snapshot resuelto, para poder decidir si los asocio.
6. Como staff, el aviso debe identificar claramente cada Paquete señalado (código de acceso, nombre del destinatario, fecha de anuncio), para decidir con contexto suficiente sin tener que ir a buscarlo en otro lado.
7. Como staff, quiero poder autorizar con un clic la asociación retroactiva de un Paquete señalado, para no tener que ir a corregirlo manualmente desde otro lugar.
8. Como staff, quiero poder ignorar un Paquete señalado sin asociarlo (dejarlo como está), por si el Teléfono coincide pero ese Paquete en particular no debería ir a esa unidad.
9. Como staff, si un mismo Teléfono tiene varios Paquetes huérfanos, quiero poder asociarlos de a uno (no una acción en bloque que no pueda revisar antes de confirmar cada uno).
10. Como dueño del producto, quiero que un Paquete `Recibido`, `Entregado` o `Cancelado` nunca pueda re-asociarse retroactivamente, para preservar la garantía de que el historial de un paquete resuelto no cambia (ADR-0001).
11. Como dueño del producto, quiero que este mecanismo nunca busque coincidencias por nombre en todo el edificio — solo por Teléfono ya vinculado — para no arriesgar asociar un Paquete al Apartamento equivocado por una coincidencia de nombre entre dos residentes.
12. Como cliente (residente), quiero que un Paquete que anuncié antes de tener mi Apartamento vinculado, una vez el staff lo autorice, se vea con la dirección correcta en `/mis-paquetes` y `/consultar`, para tener mi historial completo y correcto.
13. Como desarrollador, quiero que la detección de Paquetes huérfanos sea una función de dominio reutilizable, para no duplicar la consulta en cada punto de la UI que vincula un Teléfono a un Apartamento.
14. Como desarrollador, quiero que la corrección retroactiva reutilice el mismo patrón ya auditado de `corregir_destinatario` (actor, `corrected_at`/`corrected_by_usuario_id`, guard `Anunciado`), para mantener un solo mecanismo de "excepción acotada a ADR-0001" en vez de dos paralelos con reglas distintas.
15. Como desarrollador, quiero que ningún Paquete quede corregido sin quedar auditado (quién lo autorizó y cuándo), igual que ya pasa con la corrección de destinatario.
16. Como staff usando `/announce` para declarar una unidad, si alguno de los Teléfonos del grupo no tiene Paquetes huérfanos, no quiero ver ningún aviso ni acción de más para ese Teléfono — el flujo normal de declarar la unidad no debe sentirse distinto cuando no hay nada que corregir.
17. Como staff, si entro a la ficha de un cliente/Apartamento sin ningún Paquete huérfano pendiente, no quiero ver el aviso — la ausencia de huérfanos no debe agregar ruido visual a la ficha.
18. Como auditor revisando el historial de un Paquete corregido, quiero poder ver que fue corregido (mismos campos que ya existen), aunque el sistema no distinga explícitamente si la corrección fue de destinatario o de apartamento (ver Out of Scope).

## Implementation Decisions

- **Nuevo término de dominio: "Paquete huérfano".** Un Paquete `Anunciado` cuyo snapshot de
  Apartamento (`snapshot_conjunto`/`snapshot_torre`/`snapshot_apartamento`) está vacío, y cuyo
  Anunciante o Destinatario coincide (por Teléfono) con una Persona que SÍ tiene un
  `apartamento_actual` resuelto hoy.

- **`paquete_service.paquetes_sin_apartamento_de_telefono(session, telefono_canonico) -> list[Paquete]`**
  — nueva función de consulta. Trae Paquetes `estado == ANUNCIADO` con `snapshot_apartamento IS
  NULL` donde `announced_by_phone == telefono_canonico` OR `recipient_phone == telefono_canonico`.
  El teléfono se recibe ya canónico (normalizado por el llamador, mismo criterio que el resto del
  dominio) — la función no normaliza.

- **`paquete_lifecycle.corregir_apartamento(session, paquete, actor, apartamento) -> Paquete`** —
  nueva función, hermana de `corregir_destinatario` (misma rebanada, `paquete_lifecycle.py`). Guard
  idéntico: `raise TransicionInvalida` si `paquete.estado is not EstadoPaquete.ANUNCIADO` (el
  paquete queda intacto). Escribe `snapshot_conjunto`/`snapshot_torre`/`snapshot_apartamento` desde
  `apartamento` (mismo patrón que `_terna_snapshot` en `paquete_service.announce` — copia texto, no
  FK, ADR-0001 se mantiene). Registra `corrected_at`/`corrected_by_usuario_id` con `actor` — se
  **reutilizan las columnas existentes**, no se agrega ninguna columna nueva ni se distingue en el
  esquema si la corrección fue de destinatario o de apartamento (ver Out of Scope, story 18).

- **Disparo automático (staff-initiated) — extensión del patrón `staff_actor` que ya existe en
  `paquete_service.announce`.** `ocupante_service.agregar_ocupante`, `asociar_telefono_a_ocupante` y
  `editar_telefono_ocupante` ganan un parámetro nuevo `staff_actor: Usuario | None = None`. Cuando
  se pasa (llamado desde `/residentes` o `/announce`, ambas rutas ya tienen `Usuario` de sesión
  disponible vía `current_staff`), la función, después de vincular `apartamento_actual_id`, llama a
  `paquetes_sin_apartamento_de_telefono` para ese teléfono y aplica `corregir_apartamento` a cada
  resultado, en la misma transacción que la vinculación. Cuando no se pasa (autoservicio desde
  `/mis-datos`, `customer_verify.py` no tiene `Usuario` de staff en su sesión), no se dispara nada
  automático — el comportamiento de autoservicio no cambia.

- **`announce_new.py` (declarar unidad en lote)** también gana el mismo `staff_actor` al llamar
  `agregar_ocupante`/`asociar_telefono_a_ocupante` por cada Teléfono del grupo — reutiliza la MISMA
  extensión de `ocupante_service`, no un mecanismo aparte.

- **Aviso staff en `/residentes` (ficha de cliente/Apartamento).** Al renderizar la ficha
  (`customers_manage/detail.html` y su ruta en `customers_manage.py`), por cada Ocupante activo del
  Apartamento (o la Persona sola si la ficha es de un cliente sin Apartamento) se llama
  `paquetes_sin_apartamento_de_telefono` con su Teléfono. Si hay resultados, se muestra un aviso
  tipo warning con la lista (código de acceso, destinatario, fecha) y un botón "Asociar" por
  Paquete. Sin resultados, no se muestra nada (story 17).

- **Nueva ruta staff `POST /residentes/paquetes/{paquete_id}/asociar-apartamento`** (o el prefijo
  que ya use `customers_manage.py` para acciones sobre la ficha) — recibe el `paquete_id`, resuelve
  el Apartamento actual de la Persona de la ficha, llama `corregir_apartamento(session, paquete,
  actor=current_staff, apartamento=...)`, redirige de vuelta a la ficha. Gated igual que el resto de
  acciones operativas de `/residentes` (`current_staff`, sin `require_admin` — es una acción
  operativa, no destructiva, mismo criterio que buscar/editar en ese módulo).

- **Sin migración de base de datos.** Todo el mecanismo reutiliza columnas que ya existen
  (`snapshot_*`, `corrected_at`, `corrected_by_usuario_id`).

- **Sin cambio a `paquete_service.announce` ni a la resolución automática al anunciar.** La
  resolución al momento de anunciar (issue 44 original) sigue exactamente igual — este mecanismo
  actúa DESPUÉS, cuando el Teléfono se vincula, nunca durante el anuncio.

## Testing Decisions

- Los tests solo verifican comportamiento observable (estado final del Paquete/consulta), nunca
  detalles de implementación (no verificar SQL generado ni orden de llamadas internas).

- **`paquetes_sin_apartamento_de_telefono`**: tests de integración en `tests/data_model/`, mismo
  arnés que `tests/data_model/test_ocupante_service.py` (fixture `db_session`, marker
  `pytest.mark.integration`, Postgres efímero real vía `alembic upgrade head`). Casos: teléfono con
  huérfanos ANUNCIADO (los trae), teléfono con paquetes ya RECIBIDO/ENTREGADO/CANCELADO (no los
  trae, aunque no tengan apartamento), teléfono sin ningún paquete huérfano (lista vacía), teléfono
  que aparece como destinatario en vez de anunciante (lo trae igual).

- **`corregir_apartamento`**: prior art directo, `tests/data_model/test_corregir_destinatario.py` —
  mismo patrón de casos (corrige un `Anunciado`, `TransicionInvalida` si no está `Anunciado`,
  `corrected_at`/`corrected_by_usuario_id` quedan seteados).

- **Extensión `staff_actor` en `ocupante_service`**: extender
  `tests/data_model/test_ocupante_service.py` — casos nuevos: `agregar_ocupante`/
  `asociar_telefono_a_ocupante`/`editar_telefono_ocupante` con `staff_actor` y huérfanos existentes
  (quedan corregidos), mismas funciones SIN `staff_actor` (autoservicio — huérfanos quedan
  intactos), y el caso sin huérfanos (no falla ni hace nada de más).

- **Superficie web en `/residentes`**: `tests/web/test_customers_manage.py` ya existe y cubre esa
  ruta — extender con: ficha con huérfanos pendientes muestra el aviso con los datos correctos,
  ficha sin huérfanos no lo muestra, `POST .../asociar-apartamento` corrige el Paquete y redirige,
  la misma acción sobre un Paquete que ya no está `Anunciado` (carrera: alguien lo recibió mientras
  tanto) falla de forma controlada sin 500.

- **`/announce` (declarar unidad en lote)**: extender `tests/web/test_announce_new.py` — declarar
  una unidad con un Teléfono que tiene huérfanos los corrige en el mismo submit.

## Out of Scope

- **Distinguir en el esquema si una corrección fue de destinatario o de apartamento.** Ambas
  reutilizan `corrected_at`/`corrected_by_usuario_id`. Si más adelante hace falta auditar el motivo
  específico, es un cambio de esquema aparte (columna nueva o tabla de auditoría), no parte de este
  spec.
- **Búsqueda por nombre en todo el edificio.** Explícitamente descartada (Opción A del issue 44
  original) — el mecanismo es siempre por Teléfono ya vinculado.
- **Asociación en bloque (un clic para todos los huérfanos de un Teléfono a la vez).** Cada Paquete
  se autoriza individualmente (story 9).
- **Notificar al cliente cuando el staff autoriza la asociación.** No se pidió; `/mis-paquetes` y
  `/consultar` simplemente mostrarán el dato correcto la próxima vez que el cliente entre.
  Notificación proactiva (SMS/WhatsApp) queda fuera.
- **Cualquier cambio a cómo se resuelve el Apartamento al momento de `announce()`.** Ese
  comportamiento (issue 44 original, resolución al anunciar) no cambia — este spec es exclusivamente
  la corrección retroactiva posterior.
- **Paquetes huérfanos de un Ocupante SIN teléfono propio** (el "nombre sin teléfono" o un Ocupante
  registrado sin Teléfono, ver glosario en `CONTEXT.md`) — la detección es siempre por Teléfono; un
  Ocupante sin Teléfono no tiene forma de haber "anunciado" nada bajo su propia identidad, así que
  no aplica.

## Further Notes

- Precedente directo y deliberadamente reusado: `corregir_destinatario` en `paquete_lifecycle.py`
  ya es una "excepción acotada y auditada a la inmutabilidad del snapshot (ADR-0001)" — este spec
  agrega una segunda excepción del mismo tipo, mismo guard, mismo mecanismo de auditoría, en vez de
  inventar un mecanismo paralelo.
- Vale la pena, al implementar, actualizar `docs/adr/0001-paquete-snapshot-inmutable.md` con una
  nota corta listando esta como la segunda excepción conocida (la primera es
  `corregir_destinatario`), para que quien lea el ADR más adelante no se sorprenda al encontrar dos
  puntos del código que mutan un snapshot "inmutable".
- El punto exacto de la UI del aviso en `/residentes` (banner en la ficha, no una cola/panel
  centralizado aparte) fue una decisión explícita del cliente durante la conversación de diagnóstico
  — ver `.scratch/pendientes-cliente/issues/44-...md` para el razonamiento completo detrás de cada
  decisión (estados elegibles, cuándo se autoriza, dónde vive el aviso).

Status: ready-for-agent

# Baja administrativa reversible de un residente

## Tickets

1. [Núcleo: dar de baja / reactivar manual, visible en `/residentes`](issues/01-nucleo-dar-de-baja-y-reactivar-manual.md) — sin bloqueos
2. [Reactivación automática al Recibir un paquete](issues/02-reactivacion-automatica-al-recibir.md) — bloqueado por 1
3. [Supresión de notificaciones mientras está de baja](issues/03-supresion-de-notificaciones.md) — bloqueado por 1
4. [Aviso discreto al anunciar para alguien de baja](issues/04-aviso-al-anunciar.md) — bloqueado por 1

## Problem Statement

El staff necesita poder decirle al sistema "este residente ya no está activo ahora mismo" —
alguien que se fue a vivir fuera un tiempo, o cuya situación cambió — **sin borrar sus datos
personales ni perder su historial**, y sin que eso sea permanente. Hoy la única acción de
"eliminar" que existe (`/residentes/{id}/eliminar`) es el mecanismo de derecho al olvido (Ley 1581
de 2012): irreversible, borra el nombre/teléfono/email reales. No hay ninguna forma de "pausar" a
alguien que sigue siendo el mismo cliente y va a volver.

Mientras un residente está en esta situación, el sistema debe dejar de notificarle (no tiene
sentido mandarle avisos de paquetes si administrativamente está "de baja"), pero el resto de la
operación debe poder seguir con normalidad — se le puede seguir anunciando un paquete, y el mismo
hecho de que llegue a recibirse indica que la persona volvió a estar activa, así que el sistema
debe notarlo solo y reactivarla, sin que el staff tenga que acordarse de hacerlo.

Al consultar a ese residente (su ficha, el listado de `/residentes`) debe quedar explícito que está
"de baja" — igual que ya existe un indicador para "Eliminado" (derecho al olvido), pero
visualmente distinto: son dos estados con implicaciones muy diferentes (uno es permanente y borra
datos, el otro es temporal y no toca nada) y no deben confundirse.

## Solution

Un nuevo estado en `Persona`, independiente del derecho al olvido, marcado por un timestamp
nullable (`baja_administrativa_en`) — con fecha = de baja desde cuándo, `NULL` = activo. Ningún
dato personal se modifica.

Al darla de baja (acción de staff, cualquier rol): se desvincula su Ocupante activo de la unidad
(reusando el mecanismo ya existente para el derecho al olvido), y a partir de ahí el sistema deja
de enviarle notificaciones de eventos de paquete — pero se le puede seguir anunciando cosas con
normalidad, con un aviso discreto para el staff de que no se le va a notificar.

Se reactiva de dos formas: automáticamente, en el momento en que cualquier paquete a su nombre
llegue a estado Recibido (side-effect del mismo tipo que ya existe hoy para la promoción automática
a Principal); o manualmente, con un botón "Reactivar" en su ficha, para no depender de que llegue
algo. Ninguna de las dos formas reconecta automáticamente su Ocupante a ninguna unidad — eso queda
a cargo del staff, aparte, si corresponde.

En `/residentes`, un badge ámbar "De baja" (distinto del rojo "Eliminado") marca su estado, tanto
en su ficha como en el listado normal — a diferencia del derecho al olvido, sigue apareciendo en el
listado por defecto (sigue siendo el mismo cliente, solo pausado). No se toca `/paquetes` — el
estado de baja no cambia cómo se lee un paquete ya anunciado.

## User Stories

1. Como miembro del staff (cualquier rol), quiero dar de baja administrativamente a un residente,
   para que deje de recibir notificaciones sin borrar sus datos ni su historial.
2. Como miembro del staff, quiero que dar de baja a un residente lo desvincule de su unidad como
   Ocupante activo, para que ya no aparezca como residente vigente en el buscador de `/announce`,
   "Asignar apartamento", ni bloquee el cupo de Principal de su unidad.
3. Como miembro del staff, quiero que dar de baja a un residente que es Principal promueva
   automáticamente a un sucesor con contacto propio (si existe), para no dejar la unidad huérfana
   de Principal sin necesidad de un paso manual aparte.
4. Como miembro del staff, quiero poder seguir anunciando un paquete a nombre de alguien que está
   de baja, para no bloquear la operación diaria solo porque ese residente está pausado.
5. Como miembro del staff, quiero ver un aviso discreto al anunciar/identificar a alguien que está
   de baja, para saber que no se le va a enviar ninguna notificación de este paquete.
6. Como sistema, quiero suprimir el envío de notificaciones (SMS) a un residente en baja
   administrativa, para respetar el estado "de baja" sin necesidad de que el staff lo recuerde caso
   por caso.
7. Como sistema, cuando el destinatario de un paquete está de baja y por eso no es notificable,
   quiero caer al Anunciante como destino alternativo (mismo fallback que ya existe hoy para un
   destinatario inalcanzable), para no perder la notificación por completo si hay alguien más a
   quien avisar.
8. Como sistema, quiero reactivar automáticamente a un residente en baja administrativa en el
   momento en que un paquete a su nombre llegue a estado Recibido, para que la baja no le impida
   volver a operar con normalidad sin que nadie tenga que acordarse de reactivarlo.
9. Como miembro del staff, quiero un botón "Reactivar" manual en la ficha de un residente de baja,
   para poder revertir la baja aunque nunca le llegue ningún paquete.
10. Como miembro del staff, quiero que la reactivación (automática o manual) NO reconecte
    automáticamente al residente como Ocupante de ninguna unidad, para no revivir un vínculo que ya
    puede no ser correcto (otra persona pudo haber sido promovida en su lugar, o pudo haberse
    mudado de verdad mientras estaba de baja).
11. Como miembro del staff, quiero ver un badge "De baja" (ámbar, distinto del rojo "Eliminado")
    en la ficha del residente y en el listado de `/residentes`, para distinguir de un vistazo un
    estado temporal/reversible de una eliminación permanente.
12. Como miembro del staff, quiero que un residente en baja administrativa siga apareciendo en el
    listado normal de `/residentes` (a diferencia de "Eliminado", que se excluye), para poder
    encontrarlo y reactivarlo sin tener que buscarlo por nombre.
13. Como miembro del staff, quiero que dar de baja y reactivar estén disponibles para cualquier rol
    de staff (no exclusivo de ADMIN), porque es una acción reversible de bajo riesgo, a diferencia
    del derecho al olvido.
14. Como miembro del staff, NO quiero que se toque ningún dato personal (nombre, teléfono, email,
    documento) del residente al darlo de baja, para poder reactivarlo después con exactamente la
    misma identidad de antes.
15. Como cliente que solicitó su baja por otro canal (llamada, WhatsApp, presencial) y aceptó los
    términos y condiciones que explican la reactivación automática, quiero que el staff pueda
    procesar mi solicitud desde `/residentes`, sin que yo tenga que hacerlo desde un portal propio
    (esta baja NO tiene autoservicio, a diferencia del derecho al olvido).

## Implementation Decisions

- **Nueva columna** `Persona.baja_administrativa_en` (`DateTime(timezone=True)`, nullable) —
  mismo patrón que `Persona.eliminado_en` (ADR-0005), pero semánticamente independiente: un
  registro `Persona` puede tener CUALQUIER combinación de `eliminado_en`/`baja_administrativa_en`
  en principio, aunque en la práctica una vez `eliminado_en` está seteado (derecho al olvido,
  irreversible) la baja administrativa deja de tener sentido sobre esa identidad — no hace falta un
  `CheckConstraint` para esto, alcanza con que la UI de "dar de baja" no se ofrezca sobre una
  Persona ya eliminada (mismo criterio que hoy ya excluye a los eliminados del listado por
  defecto).
- **Nuevas funciones en `persona_service.py`**:
  - `dar_de_baja_administrativa(session, persona) -> Persona`: setea `baja_administrativa_en`
    (idempotente, igual que `anonimizar_persona`: si ya estaba de baja, no hace nada). NO modifica
    ningún otro campo.
  - `reactivar_persona(session, persona) -> Persona`: limpia `baja_administrativa_en` (idempotente:
    si no estaba de baja, no hace nada). Usada tanto por el botón manual como por el hook
    automático de abajo. NO reconecta ningún Ocupante.
- **Reusa `ocupante_service.desvincular_ocupante_activo_de_persona`** (ya existe, construido para
  el derecho al olvido) para desvincular el Ocupante activo al dar de baja — mismo comportamiento
  best-effort (promueve sucesor si hay, nunca bloquea).
- **Rutas nuevas en `customers_manage.py`** (staff, cualquier rol — `current_staff`, NO
  `require_admin`):
  - `POST /residentes/{persona_id}/baja-administrativa`: llama a
    `desvincular_ocupante_activo_de_persona` + `dar_de_baja_administrativa`.
  - `POST /residentes/{persona_id}/reactivar`: llama a `reactivar_persona`.
- **Hook de reactivación automática** en `paquete_lifecycle.receive()`, mismo lugar y mismo
  patrón que la promoción automática a Principal (`promover_al_recibir`, ya existe) — se llama
  DESPUÉS de la transición exitosa, nunca bloquea ni falla el recibo en sí.
  - **Decisión técnica de la exploración de código**: NO puede reusar `resolver_ocupante_de_paquete`
    (el mecanismo que ya usa `promover_al_recibir`) porque ese resuelve un Ocupante ACTIVO — y
    alguien de baja administrativa, por definición, ya NO tiene Ocupante activo (fue desvinculado
    al darlo de baja). El hook nuevo resuelve la Persona directo por `Paquete.recipient_phone`
    (`session.query(Persona).filter(Persona.telefono == paquete.recipient_phone).one_or_none()`,
    mismo patrón que ya usa `notificacion_service.resolver_destino_notificable`) — funciona porque
    la baja administrativa NUNCA cambia el teléfono (a diferencia de la anonimización). Si esa
    Persona tiene `baja_administrativa_en` seteado, se llama a `reactivar_persona`.
- **Gate de notificación** en `notificacion_service.resolver_destino_notificable` (el único punto
  de decisión de "a quién se le notifica un evento de paquete", ya usado exclusivamente por
  `preparar_notificacion` — un solo caller, un solo lugar que tocar): el candidato Destinatario
  (resuelto por `recipient_phone`) se descarta si `destinatario.baja_administrativa_en is not
  None`, cayendo al fallback existente hacia el Anunciante (mismo camino que ya usa un destinatario
  inalcanzable/anonimizado) — el Anunciante candidato TAMBIÉN se filtra por `baja_administrativa_en
  is None`, además del filtro de `eliminado_en` que ya tenía.
- **Aviso discreto al anunciar**: en los componentes que ya muestran el pill "Auto"
  (`components/_persona_resuelta.html`, `components/_botones_anunciar_recibir.html`, usados por
  `/announce`), agregar un pill/aviso adicional ("Sin notificar — de baja") cuando la Persona
  identificada tiene `baja_administrativa_en` seteado. No bloquea el flujo, solo informa.
- **Badge ámbar "De baja"** en `customers_manage/detail.html` (título + badges, mismo lugar que
  "Eliminado"/"Auto"/"Principal") y `customers_manage/_resultados.html` (lista + búsqueda, mismo
  patrón que el badge "Eliminado" agregado hoy) — mismo estilo `rounded-full` que los demás badges
  de estas vistas, color ámbar (ya usado en el sistema para Torre/Apto) en vez del rojo reservado
  para "Eliminado".
  - A diferencia de "Eliminado", el listado POR DEFECTO de `/residentes`
    (`_listar_todos_los_residentes`/`_listar_principales`) NO debe excluir a quienes están de
    baja administrativa — solo `eliminado_en` filtra esas consultas; `baja_administrativa_en` no
    se toca ahí.
- **Botón "Reactivar"** en `customers_manage/detail.html`, mismo lugar/patrón visual que "Eliminar
  residente" hoy (ícono + `modal_confirmacion`), visible solo cuando `persona.
  baja_administrativa_en` está seteado. El botón "dar de baja administrativa" (inverso) vive ahí
  mismo, visible cuando NO está de baja ni eliminada.
- **No se toca `/paquetes`** — ningún cambio en `packages.py` ni en `_resultados.html` para este
  estado (decisión explícita del cliente).
- **Sin autoservicio del cliente** — a diferencia del derecho al olvido, esta baja NO tiene ruta en
  `/mis-datos`. Si el cliente la solicita, lo hace por otro canal y el staff la ejecuta.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la ruta HTTP, qué queda en la fila de
`Persona`/`Ocupante` después, qué mensaje HTML aparece) — nunca aserciones sobre el código interno.

- **Seam principal 1 — rutas HTTP de `customers_manage.py`** (`tests/web/test_customers_manage.py`,
  prior art directo: `test_admin_elimina_desvincula_al_principal_activo_de_su_unidad`,
  `test_admin_elimina_anonimiza_al_cliente`, `test_operador_no_puede_eliminar` de hoy mismo):
  - Dar de baja desvincula el Ocupante activo (y promueve sucesor si hay), NO toca datos
    personales, cualquier rol de staff puede hacerlo (a diferencia de `/eliminar`, que sigue
    exclusivo de ADMIN).
  - Reactivar manualmente limpia el estado, sin reconectar ningún Ocupante.
  - Badge "De baja" aparece en la ficha y en el listado/búsqueda; NO aparece para un residente
    activo; sigue apareciendo un residente de baja en el listado por defecto (a diferencia de
    "Eliminado").
- **Seam principal 2 — `paquete_lifecycle.receive()`** (dondequiera que vivan hoy los tests de esa
  máquina de estados -- prior art: los tests que ya cubren `promover_al_recibir` desde `receive()`):
  reactivación automática al recibir un paquete a nombre de alguien de baja; NO se dispara para
  alguien que no estaba de baja (no-op); NO reconecta ningún Ocupante como side-effect.
- **Seam 3 — `notificacion_service.resolver_destino_notificable`/`preparar_notificacion`**
  (`tests/data_model/test_notificacion_service.py`, prior art: los tests existentes que ya cubren
  el fallback a Anunciante para un destinatario anonimizado/inalcanzable): un destinatario de baja
  no es candidato notificable, cae al Anunciante; un Anunciante de baja tampoco es candidato.
- **Seam 4 — plantillas** (`tests/web/test_customers_manage.py` para el badge, ya cubierto arriba;
  `tests/web/test_announce_new.py` para el aviso "Sin notificar — de baja" en el flujo de
  identificar unidad/contacto, prior art: los tests de hoy que cubren el pill "Auto").

## Out of Scope

- Autoservicio del cliente para pedir su propia baja administrativa (a diferencia del derecho al
  olvido) — el cliente la solicita por otro canal, el staff la ejecuta.
- Cualquier indicador visual en `/paquetes` para el estado de baja administrativa.
- Reconexión automática del Ocupante al reactivarse (ni automática ni manual) — queda como acción
  manual aparte del staff si corresponde.
- Un enum de estados más amplio en `Persona` (se usa un timestamp nullable, mismo patrón que
  `eliminado_en`) — si en el futuro aparece un tercer estado real, ahí se evalúa migrar.
- Notificación por WhatsApp/otros canales — hoy `resolver_destino_notificable` es el único punto de
  decisión de notificación (SMS, el único canal con envío real implementado); si se agrega otro
  canal más adelante, deberá respetar el mismo gate.

## Further Notes

- Este spec es la segunda mitad de una conversación de diseño que empezó junto con el derecho al
  olvido (`.scratch/derecho-al-olvido/spec.md`, ya implementado y desplegado en localhost) — el
  cliente pidió explícitamente separarlas en dos mecanismos independientes y priorizar el derecho
  al olvido primero. Este spec cubre la pieza que quedó pendiente.
- La reactivación automática vía Recibido fue una decisión explícita del cliente, confirmada tras
  explicarle el costo (acopla `paquete_lifecycle.receive()` con el estado de `Persona`, algo que
  hoy esos dos módulos no comparten) — decidió que el acoplamiento vale la pena porque es
  exactamente el comportamiento que quiere. El cliente también aclaró que esta reactivación
  automática queda legalmente cubierta por los términos y condiciones que el cliente acepta al
  solicitar la baja (por el canal que sea) — no se requiere ningún consentimiento nuevo en el
  momento de la reactivación en sí.

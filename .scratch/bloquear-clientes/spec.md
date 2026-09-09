Status: ready-for-agent
Feature: bloquear-clientes
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, módulo 4 de 5) ·
`.scratch/baja-administrativa/spec.md` (precedente de diseño para un estado reversible en
`Persona`) · CONTEXT.md (glosario)

---

## Problem Statement

Hoy no existe ninguna forma de sancionar a un residente que incumple los términos del servicio —
el staff no puede impedirle que se le sigan recibiendo paquetes, ni impedirle iniciar sesión, sin
recurrir a algo tan drástico como el derecho al olvido (que borra sus datos personales, algo que no
aplica acá: el residente sigue siendo el mismo cliente, solo tiene que dejar de recibir servicio
temporalmente). Tampoco hay ningún mecanismo para que ese residente vuelva a tener acceso de forma
controlada, reconociendo explícitamente los términos del servicio antes de que se le vuelva a
prestar.

## Solution

Un nuevo estado de 3 fases en `Persona`, gestionado por cualquier miembro del staff:

1. **Bloqueado** — staff lo activa en cualquier momento, con un motivo obligatorio elegido de un
   catálogo predefinido y administrable (mismo patrón que los motivos de cancelación de un
   paquete). Mientras dure: no se le puede anunciar ningún paquete NUEVO (como destinatario), ni
   puede pedir un código OTP para loguearse. Los paquetes ya anunciados o recibidos antes del
   bloqueo no se ven afectados — es una restricción hacia adelante, nunca retroactiva.
2. **Desbloqueo autorizado** — staff marca que esa persona puede reintentar: se habilita de nuevo el
   OTP, pero los paquetes nuevos siguen bloqueados. Al loguearse, su sesión queda restringida
   únicamente a la pantalla de aceptar términos — no puede usar el resto de su portal todavía.
3. **Aceptación real** — una pantalla que expone el texto real de los términos del servicio y exige
   una confirmación explícita e informada (no un checkbox decorativo). Al aceptar, queda
   completamente activo de nuevo, sin que ningún staff tenga que intervenir en este último paso.

El bloqueo se extiende automáticamente a los residentes del mismo apartamento que **no tienen
Persona propia** (sin teléfono/identidad independiente) — ya que el sistema, al resolver a quién
avisarle de un paquete para ellos, siempre cae en el teléfono del Principal de su unidad; bloquear
al Principal bloquea, de forma natural, a quien depende de él. Un co-residente con su propio
teléfono registrado tiene identidad propia y no se ve afectado por el bloqueo de otra persona.

## User Stories

1. Como miembro del staff, quiero poder bloquear a un residente en cualquier momento, para
   sancionar un incumplimiento de los términos del servicio.
2. Como miembro del staff, al bloquear, quiero que el sistema me exija elegir un motivo de una lista
   predefinida, para que quede un registro de por qué se bloqueó.
3. Como admin, quiero poder crear y eliminar motivos de esa lista, con el mismo patrón que ya uso
   para los motivos de cancelación de un paquete (sin campo "activo", borrado directo).
4. Como sistema, mientras un residente está bloqueado, quiero rechazar cualquier solicitud de OTP a
   su teléfono, para que no pueda iniciar sesión en su portal.
5. Como sistema, mientras un residente está bloqueado, quiero rechazar que se le anuncie un paquete
   NUEVO como destinatario, sin importar quién lo anuncie ni por qué vía.
6. Como sistema, NO quiero que el bloqueo afecte ningún paquete ya anunciado, recibido o entregado
   antes de que el bloqueo empezara — es una restricción hacia adelante, nunca retroactiva.
7. Como sistema, quiero que el bloqueo de un residente Principal se extienda automáticamente a los
   Ocupantes de su mismo apartamento que no tienen Persona propia, reusando el mismo mecanismo que
   ya resuelve su teléfono de notificación (cae al del Principal cuando no tienen uno propio) — sin
   ninguna consulta nueva de "quién depende de quién".
8. Como sistema, NO quiero que el bloqueo afecte a un co-residente del mismo apartamento que sí
   tiene su propia Persona/teléfono registrado — solo se ve afectado si él mismo está bloqueado.
9. Como miembro del staff, quiero poder marcar que un residente bloqueado ya puede reintentar
   (autorizar desbloqueo), para habilitar de nuevo su OTP sin todavía restaurar el servicio de
   paquetes.
10. Como sistema, mientras un residente está en "desbloqueo autorizado" (puede loguearse pero
    todavía no aceptó términos), quiero seguir rechazando que se le anuncien paquetes nuevos, hasta
    que complete la aceptación.
11. Como residente en "desbloqueo autorizado", al loguearme con mi OTP, quiero que mi sesión me
    lleve directo a la pantalla de aceptar términos, sin poder ver el resto de mi portal
    (`/mis-paquetes`, el resto de `/mis-datos`) todavía.
12. Como residente, en esa pantalla, quiero ver el texto real de los términos del servicio y tener
    que confirmar explícitamente que los entiendo y los acepto — no un checkbox genérico ya
    marcado.
13. Como sistema, al aceptar los términos, quiero registrar cuándo se aceptaron y quitar el estado
    de bloqueo por completo — el residente queda activo de nuevo sin que ningún staff tenga que
    intervenir en este último paso.
14. Como miembro del staff (cualquier rol, no exclusivo de admin), quiero poder bloquear y autorizar
    el desbloqueo, porque es una acción reversible que forma parte del día a día de portería/
    recepción, igual que ya pasa con la baja administrativa.
15. Como miembro del staff, quiero que bloquear/autorizar desbloqueo viva junto a las acciones que
    ya existen sobre un residente (dar de baja, reactivar, eliminar), para no tener que buscar en
    otro lugar.
16. Como sistema, NO quiero que exista ninguna forma de corregir o revertir manualmente el registro
    de qué motivo se usó para bloquear a alguien, una vez creado — mismo criterio de auditoría que
    ya existe para otros catálogos de motivos del sistema.
17. Como residente que fue bloqueado por error o cuya situación ya se resolvió, quiero que mi
    bloqueo sea completamente reversible (nunca toca mis datos personales), a diferencia del
    derecho al olvido.

## Implementation Decisions

- **Nuevas columnas en `Persona`** (mismo patrón que `baja_administrativa_en`/`eliminado_en`):
  `bloqueado_en` (DateTime nullable), `desbloqueo_autorizado_en` (DateTime nullable),
  `terminos_aceptados_en` (DateTime nullable, se sobreescribe en cada aceptación real, no solo la
  primera).
- **Nueva entidad `MotivoBloqueo`** (`id`, `etiqueta` única, sin campo `activo`, borrado directo) —
  mismo molde que `MotivoCancelacion`. `Persona` guarda el `motivo_bloqueo_id` usado en el bloqueo
  vigente (se limpia junto con `bloqueado_en` al completar la aceptación).
- **Guard único en `announce()`** (`paquete_service.py`): justo después de resolverse
  `recipient_phone` (ya centralizado ahí para las 4 formas de `Destinatario` — `YO_MISMO`,
  `PERSONA_REGISTRADA`, `SOLO_NOMBRE`, `OCUPANTE`, y el caso `DECLARADO_POR_CLIENTE` con auto-match
  de roster), se busca la `Persona` dueña de ese teléfono; si tiene `bloqueado_en` seteado, se
  rechaza el anuncio completo con un error de dominio dedicado (ej. `ClienteBloqueadoError`). Este
  único punto ya cubre la cascada a Ocupantes sin Persona propia, porque
  `telefono_notificacion_ocupante`/`telefono_notificacion_de_persona` (ya existentes, construidos
  para el issue 163) ya resuelven el teléfono del Principal como fallback cuando el destinatario no
  tiene uno propio — no hace falta ninguna consulta nueva de "quién depende de quién".
  - `SOLO_NOMBRE` (nombre bajo el Anunciante, sin Persona detrás) queda fuera de este guard — no hay
    ninguna Persona que consultar ahí, por diseño (ver glosario, "Nombre sin teléfono").
- **Guard en `otp_service.elegible_para_otp`/`preparar_otp`**: rechaza (sin enviar OTP) si
  `bloqueado_en` está seteado y `desbloqueo_autorizado_en` NO lo está. Si `desbloqueo_autorizado_en`
  sí está seteado (aunque `bloqueado_en` siga activo), el OTP se envía con normalidad.
- **Nueva dependencia que envuelve `current_customer`** (`security.py`), usada por las rutas
  normales del portal (`/mis-paquetes`, el resto de `/mis-datos`): si `bloqueado_en` sigue seteado,
  redirige a la pantalla de aceptar términos en vez de servir el contenido pedido. La propia
  pantalla de aceptar términos sigue usando `current_customer` sin este envoltorio (para poder
  mostrarse a alguien todavía bloqueado).
- **Nueva pantalla de aceptación** (GET+POST, bajo `/mis-datos`): expone el texto real de
  `/terminos` (ya existe como página estática) con una confirmación explícita — al hacer POST,
  registra `terminos_aceptados_en` y limpia `bloqueado_en`/`desbloqueo_autorizado_en`/
  `motivo_bloqueo_id`.
- **Nuevas rutas de staff en `customers_manage.py`** (mismo patrón que `/residentes/{id}/baja-
  administrativa` y `/residentes/{id}/reactivar` — `current_staff`, NO `require_admin`):
  - `POST /residentes/{persona_id}/bloquear` — exige `motivo_bloqueo_id`, setea `bloqueado_en`.
  - `POST /residentes/{persona_id}/autorizar-desbloqueo` — setea `desbloqueo_autorizado_en` (exige
    que `bloqueado_en` ya esté seteado).
- **Sin cambios** en `deliver()`/`receive()`/`cancel()` (`paquete_lifecycle.py`) — el bloqueo nunca
  afecta un paquete que ya existe, solo la creación de uno nuevo vía `announce()`.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la ruta/función, qué queda en
`Persona` después, qué HTML se renderiza) — nunca aserciones sobre el código interno.

- **Seam 1 — guard de `announce()`**: extensión de `tests/data_model/test_paquete_service.py` (o
  el archivo que ya cubra `announce`). Cubrir: anunciar con `PERSONA_REGISTRADA` a un teléfono
  bloqueado se rechaza; anunciar vía `Destinatario.ocupante(...)` a un Ocupante sin Persona propia
  cuyo Principal está bloqueado también se rechaza (cascada); un co-residente CON Persona propia en
  la misma unidad que el Principal bloqueado sigue pudiendo recibir paquetes con normalidad;
  bloquear no afecta ningún paquete ya existente para esa Persona.
- **Seam 2 — guard de OTP** (`tests/data_model/test_otp_service.py` o equivalente, prior art:
  tests existentes de `elegible_para_otp`): bloqueado sin autorización de desbloqueo rechaza el
  OTP; bloqueado CON autorización de desbloqueo permite el OTP con normalidad.
- **Seam 3 — dependencia del portal** (`tests/web/test_customer_paquetes.py`/
  `tests/web/test_mis_datos.py` o equivalente): un residente en "desbloqueo autorizado" que accede a
  `/mis-paquetes` es redirigido a la pantalla de aceptar términos; puede acceder normalmente a esa
  pantalla puntual; tras aceptar, vuelve a acceder con normalidad a `/mis-paquetes`.
- **Seam 4 — acciones de staff** (`tests/web/test_customers_manage.py`, prior art directo:
  `test_admin_elimina_...`/tests de baja administrativa ya existentes): bloquear exige motivo
  (rechaza sin él); cualquier rol de staff puede bloquear/autorizar desbloqueo (no exclusivo de
  admin); autorizar desbloqueo sin que la persona esté bloqueada se rechaza.
- **Seam 5 — catálogo de motivos** (`tests/web/test_admin_notificaciones.py` como prior art de
  estilo directo, mismo molde que `MotivoCancelacion`): crear/eliminar exclusivo de admin.

## Out of Scope

- Bloquear el rol de "anunciante" (que ese teléfono no pueda avisar un paquete para otra persona) —
  el bloqueo acordado es únicamente como destinatario.
- Cualquier corrección o reversión manual del motivo/timestamp de un bloqueo ya registrado.
- Notificar al residente bloqueado por WhatsApp/SMS del bloqueo en sí — no se pidió, y no hay canal
  automático disponible para alguien que quizás ni pueda loguearse todavía.
- Un límite de tiempo automático de bloqueo (expira solo) — el desbloqueo siempre es una acción
  explícita del staff.
- Cambios a `/paquetes` (vista de staff) para mostrar de forma distinta a un residente bloqueado más
  allá del detalle/timeline ya existente de cada paquete puntual.

## Further Notes

- Este bloqueo es un estado independiente de `baja_administrativa_en` y de `eliminado_en` — una
  `Persona` puede en principio tener cualquier combinación, aunque en la práctica bloquear a alguien
  ya eliminado (derecho al olvido) no tendría sentido operativo.
- La cascada a dependientes fue la pieza más delicada del diseño: el esquema actual no tiene ningún
  concepto de "depende de" explícito entre Ocupantes de una misma unidad — se resolvió reusando el
  fallback de teléfono de notificación que ya existe (issue 163) en vez de construir una relación
  nueva, evitando duplicar el concepto de "a quién le avisamos por este Ocupante" en dos lugares
  distintos del sistema.

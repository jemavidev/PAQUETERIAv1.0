# `/mis-datos` — sistema de Ocupantes (segundo contacto) + gate de "cliente"

Fase de vistas AUTENTICADAS (las públicas quedaron cerradas en
`.scratch/pendientes-cliente/`, tickets 01-34). Este spec nace de un
`/grilling` completo (2026-08-03) sobre el rediseño de "segundo contacto" —
ya no son preguntas abiertas, son decisiones acordadas con el cliente. Falta
`/to-tickets` (el cliente lo invoca cuando quiera desglosar esto en tickets
verticales) para pasar a implementación.

## 0. Qué hace HOY `/mis-datos` (grounding, sin cambios en esta sección)

Protegida por sesión de cliente (verificada por OTP); sin sesión, redirige a
`/otp`. Un solo `<form>` con tres tarjetas:

- **Datos personales** — `nombre`, `email`, `segundo_contacto` (texto libre,
  ver §6 — queda retirado). Actualización parcial; único campo validado es
  `email`; si falla, rollback total ("todo o nada").
- **Notificaciones** — matriz Canal × Evento (SMS/Email/Llamada/WhatsApp ×
  Anunciado/Recibido/Entregado/Cancelado), 16 checkboxes. Ya satisface la
  nota vieja de "editar preferencias actuales o futuras" — sin cambios acá
  salvo lo de §5 (segundo contacto sin teléfono no tiene fila propia).
- **Mi apartamento** — Torre y Apartamento editables; Conjunto de solo
  lectura (lo asigna el staff). Declarar acá hoy SOLO toca
  `Persona.apartamento_actual_id` — ver §1, esto cambia.

`/otp/verificar` ya redirige directo a `/mis-datos` (la nota vieja que decía
que esto no pasaba está desactualizada). `/otp/perfil` sigue existiendo como
código huérfano de pruebas — candidato a limpieza, bajo impacto.

Modelo ya existente y REUTILIZADO tal cual (sin cambios de esquema):
`Ocupante` (`apartamento_id`, `persona_id` NULLABLE, `nombre`,
`es_principal` con índice único parcial por apartamento) y
`ocupante_service.promover_a_principal` (ya exige teléfono en el promovido,
ya degrada al anterior en la misma transacción) — hoy sin ninguna ruta que
lo dispare.

## 1. Declarar apartamento (principal) — ahora también crea `Ocupante`

Cuando el cliente se auto-declara un apartamento desde `/mis-datos`, además
de seguir marcando `Persona.apartamento_actual_id`, debe crear/asegurar su
propio `Ocupante` como principal de ese apartamento (reusar
`ocupante_service.agregar_ocupante`, que YA exige teléfono para el primer
Ocupante y lo marca `es_principal` automáticamente). Esto alimenta el mismo
roster que hoy solo alimentaba `/announce` (staff).

## 2. Un teléfono = un apartamento activo a la vez

Una Persona (por teléfono) solo puede ser `Ocupante` ACTIVO de un
apartamento a la vez. Para unirse a otro, primero debe darse de baja del
actual (§3).

## 3. Dar de baja — marcado histórico, nunca borrado

"Dar de baja" a un `Ocupante` (self-service o por el principal) es un
**marcado** (ej. `activo: bool` o `desvinculado_en: datetime` nuevo en
`Ocupante`), nunca un DELETE — los datos del apartamento anterior quedan
visibles pero de **solo consulta**, nunca se vuelven a actualizar. Mismo
espíritu que `anonimizar_persona`/ADR-0001: nunca reescribir/borrar
historia real.

**El PRINCIPAL no puede autodarse de baja directamente.** Solo puede
hacerlo si, antes:
- **(a)** promueve a otro `Ocupante` con teléfono como nuevo principal
  (`promover_a_principal`, ya existe), y LUEGO se da de baja él mismo (ya
  como Ocupante no-principal); o
- **(b)** da de baja a TODOS los demás Ocupantes de ese apartamento
  primero, y una vez solo, se da de baja él también — el apartamento queda
  sin ningún Ocupante activo.

Un segundo contacto CON teléfono (su propio login) puede autodarse de baja
sin restricciones (es información que le pertenece solo a él).

## 4. Gestión de segundos contactos (por el PRINCIPAL)

El contacto principal, desde `/mis-datos`, puede sobre los `Ocupante` de SU
apartamento:
- **Crear** uno nuevo: nombre + teléfono opcional (`agregar_ocupante`).
  Máximo **5 segundos contactos activos por apartamento** (límite duro,
  arbitrario a propósito — sin caso real que pida más).
- **Asociar teléfono** a un Ocupante ya existente sin teléfono (**función
  NUEVA** — hoy `agregar_ocupante` solo define el teléfono al crear; hace
  falta algo como `asociar_telefono_a_ocupante(session, ocupante, telefono)`
  que resuelva/cree la Persona vía `get_or_create_persona` y fije
  `ocupante.persona_id`).
- **Desvincular el teléfono** de un Ocupante (queda como Ocupante liviano
  de nuevo, sin teléfono) — **función NUEVA**, no existe hoy.
- **Desvincular TODA la información** de un segundo contacto para ese
  apartamento específico (dar de baja completo, ver §3) — **función
  NUEVA**.

El STAFF puede hacer cualquiera de estas mismas acciones, sin restricción
(mismo patrón ya usado en `/residentes/{id}` y `/announce`) — probablemente
extendiendo `/residentes/{id}` (hoy solo LISTA Ocupantes de solo lectura via
`customers_manage.listar_ocupantes`) para que también pueda editarlos.

## 5. Preferencias de notificación — quién ve/edita qué

- El **principal** puede modificar sus propias preferencias Y las de
  cualquier segundo contacto inscrito (que ya tenga su propia fila, ver
  abajo).
- Un **segundo contacto sin teléfono** NO tiene preferencias propias — sus
  notificaciones usan las preferencias YA configuradas del PRINCIPAL (les
  llegan al teléfono del principal de todos modos). Nace su propia fila
  `PersonaPreferenciaNotificacion` recién cuando consigue su propio
  teléfono (nace su propia `Persona` vía `get_or_create_persona`).
- Un **segundo contacto CON teléfono** (su propio login) solo puede
  modificar SUS PROPIAS preferencias — puede VER (no modificar) las de los
  demás Ocupantes del apartamento (principal u otros segundos contactos),
  incluyendo su nombre y teléfono (ver §7 — sin restricción de
  visibilidad dentro del mismo apartamento).

## 6. `Persona.segundo_contacto` (texto libre) — RETIRADO

Se retira del formulario de `/mis-datos` (ya no se muestra ni se escribe).
La columna se queda en la base como dato histórico neutral, sin migración
destructiva — mismo patrón ya usado con `documento`/`tipo_documento`. Sin
intento de migrar el texto libre viejo a Ocupantes estructurados (no hay
forma confiable de parsearlo).

## 7. Sesión de un segundo contacto CON teléfono

Al loguearse por OTP, un segundo contacto con teléfono entra a `/mis-datos`
(misma ruta que el principal, renderizado distinto según su rol) y ve:
- Sus propios datos personales y preferencias — **editables**.
- Apartamento (Conjunto/Torre/Apartamento) — de solo lectura (no lo
  declaró él).
- El resto del roster del apartamento (principal + otros segundos
  contactos) — **visible por completo** (nombre Y teléfono de cada uno),
  pero **de solo lectura** — no puede modificar nada que no sea suyo.
- Puede autodarse de baja de este apartamento (§3).

## 8. Anunciar un paquete a nombre de un segundo contacto

**`/anunciar` (público) NO cambia** — sigue siendo teléfono + nombre en
texto libre, SIN mostrar ninguna lista de residentes (privacidad: es una
vista pública, no debe filtrar quién vive dónde).

La resolución es enteramente privada/server-side, en el momento de
anunciar:
- Se busca la Persona por el teléfono escrito. Si existe y tiene un
  Ocupante activo (apartamento), se compara el nombre escrito contra
  **todo el roster de Ocupantes activos de ESE apartamento** (no solo el
  nombre propio del dueño del teléfono) — esto permite que el PRINCIPAL
  anuncie para sí mismo o para cualquier segundo contacto ya conocido de
  su unidad, sin fricción.
- **Coincide exactamente** con algún Ocupante del roster → el anuncio
  queda hecho automáticamente, dirigido a ese Ocupante.
- **No coincide con nadie** del roster (o el teléfono no tiene apartamento
  resuelto) → cae al comportamiento de hoy (`declarado_por_cliente`,
  self-announce bajo el propio teléfono) — la ambigüedad la resuelve
  DESPUÉS el staff vía "Corregir destinatario" (§9), nunca en el momento
  público de anunciar.

Al resolverse (automático o corregido por staff) a un Ocupante concreto, el
teléfono de notificación que se congela en el Paquete (ADR-0001, snapshot
inmutable) es: el teléfono PROPIO del Ocupante si lo tiene EN ESE MOMENTO;
si no, el teléfono del PRINCIPAL activo de ese apartamento EN ESE MOMENTO.
Nunca se re-resuelve después (si el Ocupante consigue teléfono más tarde,
o cambia el principal, los paquetes YA anunciados no cambian).

## 9. "Corregir destinatario" (staff, `/paquetes`) — nueva opción

Hoy (`paquete_correccion_service.candidatos_correccion` +
`packages/list.html`), cuando hay candidatos (Ocupantes del apartamento +
el anunciante), el staff está OBLIGADO a elegir de la lista — no hay
escape a texto libre. Hace falta agregar una opción nueva en ese mismo
`<select>`: **"Es un nuevo ocupante de este apartamento"**, que revela un
campo nombre (+ teléfono opcional) y crea un `Ocupante` nuevo para ese
apartamento (vía `agregar_ocupante`) en vez de seleccionar uno ya
existente.

## 10. Promoción / degradación de principal

`ocupante_service.promover_a_principal` ya existe y ya implementa la regla
completa (exige teléfono en el promovido, degrada al anterior en la misma
transacción) — falta SOLO la superficie: un botón "Promover a principal"
junto a cada segundo contacto CON teléfono, visible en la gestión del
propio principal (`/mis-datos`) y en la vista de staff. Ningún cambio de
lógica de dominio, solo wiring de ruta/UI.

## 11. "Cliente" — gate real de acceso a `/mis-datos` (no un badge)

Una Persona nace con nombre+teléfono (vía `/anunciar` o `/otp`) y puede
recibir paquetes, anunciar, etc. desde el primer momento — PERO no puede
VER NI EDITAR `/mis-datos` hasta que se le haya recibido físicamente al
menos un paquete a su nombre. Esto es control anti-abuso: `/anunciar` no
verifica nada hoy (cualquiera crea una Persona con un teléfono+nombre
inventado); sin este gate, alguien podría usar `/otp` para entrar a
`/mis-datos` con un teléfono nunca verificado por un humano y empezar a
declarar apartamentos/segundos contactos falsos.

- **Cálculo**: función nueva, ej. `es_cliente_verificado(session, persona)`
  — existe algún `Paquete` cuyo destinatario resuelto (misma lógica que
  `notificacion_service.resolver_destino`: `recipient_phone`, o si no
  tiene, `announced_by_phone`) sea el teléfono de esta Persona, Y que ese
  Paquete haya llegado a `RECIBIDO` en algún momento (`received_at is not
  None` — aunque después pase a Entregado/Cancelado, sigue contando).
  **Calculado al vuelo, NO un campo guardado.**
- **Dónde se verifica**: SOLO en la ruta `/mis-datos` (GET y POST), como
  chequeo adicional junto a `current_customer`. **NUNCA en `/otp/solicitar`
  ni `/otp/verificar`** — bloquear ahí permitiría enumerar por mensaje de
  error qué teléfonos son clientes reales y cuáles no. Cualquiera puede
  seguir pidiendo/verificando su OTP con normalidad.
- **Qué ve alguien sin el gate**: en vez del formulario, una pantalla
  simple ("tu cuenta se activa por completo cuando te recibamos tu primer
  paquete — mientras tanto podés seguir anunciando normalmente"), sin
  exponer ni permitir editar nada.

## 12. Autorización automática de recepción (nuevo, en Datos personales)

Un toggle sí/no en la sección "Datos personales" de `/mis-datos` (booleano
nuevo en `Persona`, ej. `autoriza_recepcion_automatica`, default `False`)
— disponible para cualquiera que llegue a ver `/mis-datos` (principal o
segundo contacto con teléfono; ambos tienen teléfono por construcción, ya
que loguearse ahí requiere OTP).

Es **puramente informativo/visible para el staff** (ej. en
`/residentes/{id}`) — indica que esa persona ya autorizó de antemano que
el staff anuncie/reciba paquetes a su nombre sin necesidad de llamarla
primero para pedir permiso verbal. **NO es un gate técnico**: el staff YA
puede anunciar/recibir para cualquiera sin restricción alguna hoy
(`/announce`), y esto no cambia — es solo una señal para su proceso
humano/manual, no una condición que el código deba hacer cumplir.

## Fuera de alcance de este spec

- Proveedores reales de Email/Llamada/WhatsApp (siguen sin conectar).
- Migrar el texto libre viejo de `segundo_contacto` a Ocupantes.
- `/otp/perfil` — limpieza de código huérfano, se puede hacer aparte,
  bajo impacto, no bloquea nada de esto.

## Índice de tickets (`.scratch/mis-datos/issues/`)

Publicados vía `/to-tickets` (2026-08-03), en orden de dependencia — los
números 11 y 12 no dependen del sistema de Ocupantes y pueden hacerse en
cualquier momento/en paralelo.

- `01` — Auto-declarar apartamento en `/mis-datos` también crea el Ocupante principal — **done**
- `02` — Fundamento: marcado de baja en Ocupante + un teléfono = un apartamento activo a la vez — **done**
- `03` — El principal gestiona sus Ocupantes desde `/mis-datos` — **done**
- `04` — Promover a un Ocupante-con-teléfono como nuevo principal — **done**
- `05` — Sesión de un Ocupante-con-teléfono (no principal) en `/mis-datos` — **done**
- `06` — Preferencias de notificación: heredadas vs propias — **done**
- `07` — Retirar el campo viejo `segundo_contacto` de `/mis-datos` — **done**
- `08` — `/anunciar`: auto-match contra el roster del apartamento + congelar el teléfono correcto — **done**
- `09` — "Corregir destinatario" (staff): opción "Es un nuevo ocupante de este apartamento" — **done**
- `10` — Staff gestiona Ocupantes sin restricción desde `/residentes/{id}` — **done**
- `11` — Gate "cliente verificado" en `/mis-datos` — **done**
- `12` — Toggle "autorización automática de recepción" en Datos personales — **done**

## Comments

- 2026-08-03 — `/grilling` completo con el cliente, 13 decisiones
  acordadas (ver secciones 1-12 arriba, más el retiro del campo viejo en
  §6). Reemplaza las "preguntas abiertas" de la versión anterior de este
  documento — todas quedaron resueltas.
- 2026-08-03 — `/to-tickets` completo: 12 tickets publicados bajo
  `issues/`, aprobados por el cliente. Siguiente paso: implementarlos en
  orden de la frontera (bloqueadores primero), empezando por `01`.
- 2026-08-03 — Los 12 tickets implementados localmente (código + tests +
  Tailwind recompilado, `?v=25`). Suite completa: 526 passed. Pendiente:
  desplegar a `test.papyrus.com.co` y verificar en vivo antes de pasar
  cada ticket de `done` a `verificado`.

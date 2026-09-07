# Derecho al olvido (Ley 1581 de 2012) + fix del gap de "eliminar residente"

**Origen:** el 2026-09-07 el cliente eliminó a un residente real ("JESUS VILLALOBOS") desde
`/residentes` y pidió analizar qué se reflejaba en el sistema. El análisis encontró un bug real
(ver issue 01) y llevó a una conversación de diseño más amplia: el cliente pidió separar el
"eliminar residente" de hoy (que es en realidad el mecanismo de **derecho al olvido**, Ley 1581 de
2012 / Habeas Data) de un mecanismo DISTINTO que también quiere construir a futuro -- una **"baja
administrativa"** reversible, que NO borra datos personales (solo desvincula al residente de los
flujos activos del sistema hasta que se reactive). Esa segunda pieza quedó **fuera de alcance de
esta ronda** -- el cliente pidió explícitamente implementar primero lo del derecho al olvido
("implementa lo pertinente a la ley derecho al olvido, también ayuda a poder hacerlo desde el lado
del staff y permite que funcione de la mejor manera").

Ver `docs/adr/0005-eliminar-persona-es-anonimizacion.md` (ya documentaba el mecanismo de
anonimización antes de esta ronda) y los issues abajo para el detalle de lo que se agregó/corrigió.

## Issue 01 -- Ocupante fantasma tras "eliminar residente"

**Bug real encontrado, no una decisión de diseño.** `anonimizar_persona()` (el mecanismo de
`/residentes/{id}/eliminar`, único ADMIN) limpia los datos personales de la `Persona` pero nunca
tocaba su `Ocupante` -- si la Persona era Principal ACTIVO de una unidad, ese Ocupante quedaba vivo
indefinidamente: nombre congelado (ej. "JESUS VILLALOBOS"), visible como residente activo en el
buscador de unidad de `/announce`, en "Asignar apartamento", en la ficha de la unidad -- y
bloqueando el cupo de Principal de esa unidad para siempre (constraint `uq_ocupantes_principal_
por_apartamento`, máximo 1 Principal activo).

Confirmado en la base de datos de dev local: el caso real de "JESUS VILLALOBOS" (Torre 1 / 302)
tenía exactamente este problema -- dado de baja manualmente como primer paso de esta sesión
(`dar_de_baja_ocupante`, promoviendo a MARIANA como sucesora, mismo criterio que ya usa el staff).

### Fix

- **`ocupante_service.py`** (nuevas funciones):
  - `_promover_sucesor_si_hace_falta(session, ocupante)`: extraída de la lógica que ya tenía
    `customers_manage_ocupante_dar_de_baja` (issue 259/260) -- si `ocupante` es Principal, promueve
    al Ocupante activo más antiguo con Teléfono/WhatsApp propio del mismo Apartamento.
  - `dar_de_baja_ocupante_como_staff(session, ocupante)`: refactor de esa misma ruta -- usa el
    helper de arriba, y levanta `ValueError` (mismo mensaje de siempre) si es Principal, quedan
    otros Ocupantes activos, y ninguno tiene contacto propio para sucederlo.
  - `desvincular_ocupante_activo_de_persona(session, persona)`: NUEVA, para el flujo de derecho al
    olvido -- da de baja el Ocupante activo de `persona` (si tiene uno), intentando promover un
    sucesor, pero **nunca bloquea** (a diferencia de la de arriba): el derecho al olvido no puede
    quedar condicionado a que la unidad tenga o no otro residente con contacto propio.
- **`customers_manage.py`**: `customers_manage_ocupante_dar_de_baja` ahora llama al helper de
  staff (elimina duplicación de la consulta candidato/promoción). `customers_manage_delete`
  (`/residentes/{id}/eliminar`) llama a `desvincular_ocupante_activo_de_persona` ANTES de
  `anonimizar_persona`.
- **Tests**: `test_admin_elimina_desvincula_al_principal_activo_de_su_unidad` (`test_customers_
  manage.py`) -- reproduce el caso real (Principal + sucesor con contacto propio), confirma que
  queda desvinculado Y que el sucesor queda promovido.

## Issue 02 -- Autoservicio del cliente (`/mis-datos/eliminar-cuenta`)

Nueva ruta, exclusiva del portal OTP del cliente (`current_customer`, ya autenticado -- prueba que
controla el teléfono real). El cliente ejecuta su propia anonimización sin intervención de staff,
con confirmación explícita (checkbox, mismo patrón que "Quitar mi Teléfono").

### Impedimento: paquete en curso

**Decisión de diseño tomada por Claude, delegada explícitamente por el cliente** ("permite que
funcione de la mejor manera"): el autoservicio se **rechaza** (sin ejecutar nada) si la Persona
tiene algún Paquete propio en estado ANUNCIADO o RECIBIDO (`paquete_service.tiene_paquete_en_
curso`, reusa la misma regla "exacta" que ya usa `contar_paquetes_de_persona`) -- un paquete físico
en custodia no puede quedar huérfano de destinatario contactable (su teléfono se vuelve sintético e
inenrutable al anonimizar). El mensaje dirige a contactar administración.

El staff, en cambio, **no tiene este guard** (`/residentes/{id}/eliminar` sigue sin él) -- puede
procesar la baja manualmente aunque haya algo en curso, si administración decide documentar la
excepción (ej. la persona insiste por otro canal). Esto no fue pedido explícitamente por el
cliente pero se dejó así a propósito: el staff tiene contexto que el sistema no puede inferir solo.

**Nota (no soy abogado):** los plazos y excepciones exactos de la Ley 1581 de 2012 (derecho de
supresión, Habeas Data) deben confirmarse con asesoría legal -- lo implementado es el mecanismo
técnico (autoservicio inmediato con un impedimento operativo automático), no una interpretación
legal de cuáles excepciones aplican o qué plazo de respuesta exige la ley para un reclamo formal.
Si el cliente necesita algo más formal (solicitud + cola de revisión de staff, plazos de respuesta
configurables, motivo de excepción documentado), es una ronda de diseño aparte -- no se construyó
acá por no haber sido pedido.

### Implementación

- **`paquete_service.py`**: `tiene_paquete_en_curso(session, persona) -> bool` (nueva).
- **`customer_verify.py`**: `POST /mis-datos/eliminar-cuenta` -- gate de verificación, checkbox de
  confirmación, guard de paquete en curso, `desvincular_ocupante_activo_de_persona` +
  `anonimizar_persona`, cierre de sesión inmediato (mismo patrón que `desvincular-telefono`).
- **`customer/verify.html`**: bloque "Eliminar mi cuenta" (danger zone), mismo componente
  `modal_confirmacion` que el resto de acciones destructivas de esta vista.
- **Tests** (`test_customer_verify.py`): sin confirmar (400), con paquete en curso (400, sesión
  sigue activa, datos intactos), éxito (anonimiza + cierra sesión), y que desvincula al Ocupante
  Principal activo (mismo bug que issue 01, ahora cubierto también en este camino).

## Issue 03 -- Indicador visual "cliente eliminado" en `/paquetes`

Pedido explícito del cliente (mid-conversación): que un destinatario cuya Persona fue anonimizada
se muestre en rojo en las listas, igual que ya se hace para "el destinatario se mudó" (issue 307).

Reusa exactamente ese mecanismo (`text-red-600`, sin link) en `packages.py`/`_resultados.html`,
agregando `p.destinatario_eliminado` junto a `p.destinatario_se_mudo`.

**Limitación conocida, documentada en el código:** el destinatario de un Paquete no tiene un FK
propio en el esquema actual (`recipient_name`/`recipient_phone` son texto snapshot, no
`recipient_persona_id`) -- la única identidad que SÍ tiene un FK estable (nunca cambia, ni con la
anonimización) es el anunciante (`announced_by_persona_id`). Por eso `destinatario_eliminado` solo
se activa en el caso "yo mismo" (`recipient_phone == announced_by_phone`, el anunciante ES el
destinatario) -- que es además el caso real que motivó todo esto. Un paquete anunciado por UN
tercero para un destinatario que luego se anonimiza a sí mismo no se puede detectar hoy sin agregar
una columna nueva -- no se hizo en esta ronda por no haber sido parte del pedido ni del caso real.

### Implementación

- **`packages.py`**: `p.destinatario_eliminado` (batch, mismo loop que `destinatario_se_mudo`).
- **`_resultados.html`**: 3 lugares -- título del modal "Ver", Torre/Apto dentro del modal, y la
  celda de Torre/Apto de la fila en la lista -- todos con el mismo criterio que ya usaba "se mudó"
  (rojo, sin link), priorizado ANTES de esa rama (son mutuamente excluyentes en la práctica, pero
  por si acaso coincidieran, "eliminado" es el caso más fuerte).
- **Test** (`test_packages.py`): `test_direccion_en_rojo_y_sin_link_si_destinatario_fue_eliminado`.

## Issue 04 -- Mismo indicador extendido a `/residentes`

Seguimiento pedido explícito del cliente tras ver el rojo en `/paquetes`: "de qué forma puedes
aplicar esto a las vistas donde aparezca el cliente eliminado y se pueda distinguir".

Auditoría de dónde MÁS puede aparecer una Persona anonimizada:

- **`/residentes` (listado por defecto)**: NO aparece -- `_listar_todos_los_residentes`/`_listar_
  principales` ya filtran `Persona.eliminado_en.is_(None)` desde issue 67. Sin cambios necesarios.
- **`/residentes` (con búsqueda, `?q=`)**: SÍ puede aparecer -- `_buscar_residentes` **nunca
  filtró** `eliminado_en` (gap pre-existente, no introducido por este trabajo). Si el staff busca
  por un término que calce con el nombre anonimizado ("Cliente eliminado") o similar, la fila
  aparecía sin ninguna distinción visual -- se veía como un residente activo cualquiera.
- **`/residentes/{id}` (ficha propia)**: alcanzable con la URL directa aunque no esté en ningún
  listado (`_get_persona_o_404` no filtra `eliminado_en`) -- tampoco tenía ningún indicador, más
  allá del nombre "Cliente eliminado" en el propio texto.
- **Roster de "Residentes de la unidad" (`customers_manage/detail.html`, `listar_ocupantes`)**: NO
  puede aparecer -- ese roster ya es solo-activos (`incluir_baja=False`), y el fix de issue 01
  (`desvincular_ocupante_activo_de_persona`) garantiza que una Persona anonimizada ya no tiene
  ningún Ocupante activo. Sin cambios necesarios.

### Implementación

- **`customers_manage/detail.html`**: nombre del título en rojo (`text-red-600`) + badge
  "Eliminado" (mismo rojo/blanco que "Auto"), primero entre los badges, cuando `persona.
  eliminado_en`.
- **`customers_manage/_resultados.html`**: mismo badge "Eliminado" en los 2 layouts (mobile/
  desktop) de la lista/búsqueda principal, más el nombre en rojo en los 3 links a `/residentes/
  {id}` de este archivo (lista principal x2, sub-lista "sin apartamento asignado" x1). El `{% if
  %}` que decide si renderizar el contenedor de badges ahora también se dispara solo por `p.
  eliminado_en` (antes solo por Auto/Principal/Torre-Apto/paquetes).
- **Tests** (`test_customers_manage.py`): ficha muestra el badge tras eliminar / no lo muestra para
  un residente activo / una búsqueda por texto SÍ puede encontrar y marcar a un eliminado.
- **No se tocó** el gap de `_buscar_residentes` en sí (que un eliminado sea *encontrable* por
  búsqueda) -- el pedido era "distinguirlo", no ocultarlo; de hecho poder encontrarlo así es
  consistente con "consultar la data histórica" que motivó todo esto. Si el cliente prefiriera que
  la búsqueda tampoco lo encuentre nunca, es un cambio de una línea (agregar el mismo filtro que ya
  usa el listado por defecto) -- no se asumió sin que lo pida.

## Pendiente (fuera de alcance de esta ronda, a diseñar cuando el cliente lo pida)

- **"Baja administrativa" reversible** -- el mecanismo que el cliente describió primero (desvincula
  de los flujos activos, bloquea notificaciones, NO toca datos personales, se reactiva solo al
  llegar un paquete a RECIBIDO). Requiere una columna de estado nueva en `Persona` (distinta de
  `eliminado_en`, que queda reservada para derecho al olvido) y decidir si la reactivación
  automática vía side-effect de `Paquete` → RECIBIDO es realmente lo que se quiere, o si conviene
  una confirmación explícita del staff en ese momento (más auditable). Grilling en curso, pausado
  cuando el cliente priorizó implementar primero lo de este documento.
- Autoservicio más formal (solicitud + cola de revisión, plazos configurables) si el cliente decide
  que el autoservicio inmediato de este documento no es suficiente para cumplimiento legal.
- El gap de `_buscar_residentes` (no filtra `eliminado_en`) queda documentado en issue 04 como
  comportamiento aceptado, no un pendiente -- solo se convierte en pendiente si el cliente pide
  explícitamente que la búsqueda tampoco encuentre eliminados.

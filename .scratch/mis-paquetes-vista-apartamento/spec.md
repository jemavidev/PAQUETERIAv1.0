Status: ready-for-agent

Origen: `.scratch/pendientes-cliente/issues/47-mis-paquetes-mejoras-visuales.md`, punto 3.

## Tickets

Desglosado vía `/to-tickets` — ver `issues/`:

1. `issues/01-alcance-ampliado-apartamento-completo.md` — sin bloqueos
2. `issues/02-avatar-color-por-ocupante.md` — bloqueado por 01

# `/mis-paquetes`: ver los paquetes de todo el Apartamento, con identificación visual por Ocupante

## Problem Statement

Hoy `/mis-paquetes` solo muestra los Paquetes ligados al Teléfono de la sesión activa (como
Anunciante o Destinatario). Si un residente vive con otros Ocupantes del mismo Apartamento (pareja,
hijos, un segundo contacto con Teléfono propio), cada uno solo ve SU PROPIA porción de la historia
— nadie tiene una vista completa de qué está llegando o ya llegó para su unidad. Cuando esa vista
compartida exista, además hace falta poder distinguir de un vistazo qué paquete es de cuál
Ocupante, sin tener que leer el nombre de cada tarjeta una por una.

## Solution

`/mis-paquetes` pasa de mostrar solo los Paquetes del Teléfono de la sesión a mostrar los Paquetes
de TODOS los Ocupantes activos del mismo Apartamento (incluida la propia sesión). Cada tarjeta de
Paquete gana un avatar de color junto al nombre, identificando a cuál Ocupante pertenece — mismo
color siempre para el mismo Ocupante, distinto color para cada uno de los demás Ocupantes de esa
unidad, así que con solo mirar los colores se puede diferenciar "esto es de mamá, esto es del hijo,
esto es mío" sin leer texto. Una sesión sin Apartamento asignado sigue viendo exactamente lo mismo
que hoy (solo sus propios Paquetes) — el cambio de alcance solo aplica cuando hay una unidad real
de la cual formar parte.

## User Stories

1. Como residente que vive con otros Ocupantes de mi Apartamento, quiero ver en `/mis-paquetes` los Paquetes de todos nosotros juntos, para tener una vista completa de qué está pasando con la paquetería de mi hogar sin tener que preguntarle a cada quien.
2. Como residente, quiero que los Paquetes que YO anuncié o recibí sigan apareciendo igual que hoy, para no perder nada de lo que ya podía ver.
3. Como residente sin Apartamento asignado (o Ocupante de ninguna unidad), quiero que `/mis-paquetes` siga mostrando solo mis propios Paquetes, para que el cambio no me afecte si no vivo acompañado en el sistema.
4. Como residente viendo la lista combinada, quiero que cada tarjeta tenga un color/avatar que identifique a qué Ocupante pertenece, para diferenciar los paquetes de cada persona sin leer cada nombre.
5. Como residente, quiero que el mismo Ocupante tenga siempre el mismo color dentro de mi Apartamento, para poder reconocerlo de un vistazo cada vez que entro a la vista.
6. Como residente, quiero que dos Ocupantes distintos de mi misma unidad nunca compartan color, para que la diferenciación visual sea confiable.
7. Como residente, quiero que las pestañas por estado (Anunciados/Recibidos/Entregados/Cancelados) sigan funcionando igual, ahora filtrando sobre el conjunto ampliado de Paquetes del Apartamento.
8. Como residente, quiero que el conteo que muestra cada pestaña refleje el total del Apartamento (todos los Ocupantes), no solo el mío, para que sea consistente con lo que la lista realmente muestra.
9. Como residente, quiero poder expandir el detalle (timeline, fotos, código de acceso) de un Paquete de OTRO Ocupante de mi unidad exactamente igual que puedo con los míos, para tener el mismo nivel de información sin importar quién lo anunció o recibió.
10. Como residente, si un Paquete tiene un Destinatario "nombre sin teléfono" (no es una Persona real, ver glosario `CONTEXT.md`) que no corresponde a ningún Ocupante conocido, quiero ver un avatar neutro en vez de uno de color, para no sugerir una identidad que no está confirmada.
11. Como residente, si el Destinatario de un Paquete no matchea ningún Ocupante pero el Anunciante sí, quiero que el avatar identifique al Anunciante, para que el paquete igual quede visualmente asociado a alguien real de mi unidad en vez de quedar neutro sin necesidad.
12. Como desarrollador, quiero que la resolución de "qué Ocupantes son parte de mi Apartamento" sea una función de dominio reutilizable, para no duplicar la lógica de roster en la ruta web.
13. Como desarrollador, quiero que la asignación de color reutilice el orden ya establecido de `listar_ocupantes` (principal primero) y el límite ya existente de `MAX_OCUPANTES_ACTIVOS`, para no inventar un esquema de color nuevo sin relación con las reglas de Ocupante ya vigentes.
14. Como dueño del producto, quiero que un Ocupante dado de baja (histórico) NO cuente para el roster de colores ni aparezca implícitamente en la vista ampliada, para que la vista siga reflejando solo la composición ACTUAL del Apartamento.
15. Como dueño del producto, quiero que este cambio de alcance sea explícito y documentado (no un efecto secundario silencioso), dado que implica que un Ocupante vea Paquetes que otro Ocupante anunció o recibió — decisión de producto ya confirmada por el cliente, no una filtración accidental de datos.
16. Como residente, quiero que si mi Apartamento cambia de composición (alguien nuevo se une, alguien se da de baja) mientras uso la app, la próxima vez que cargue `/mis-paquetes` refleje la composición actual, para no ver datos de gente que ya no vive ahí ni perderme a alguien nuevo.
17. Como desarrollador, quiero que el cambio de filtro en `customer_paquetes.py` sea la única ruta que cambia de alcance — `/consultar` (vista pública) y el resto de la app no se ven afectados por este spec.

## Implementation Decisions

- **Nueva función `ocupante_service.telefonos_activos_del_apartamento_de(session, persona) ->
  list[str]`.** Si `persona.apartamento_actual_id` es `None`, devuelve `[persona.telefono]`
  (el comportamiento actual, sin cambios). Si tiene Apartamento, resuelve `listar_ocupantes` de
  ese Apartamento (activos, principal primero — orden ya existente, no se reinventa) y devuelve
  los Teléfonos de los que tienen `persona_id` (los Ocupantes sin Teléfono no pueden haber
  anunciado/recibido nada bajo su propia identidad, así que no aportan Teléfonos a la lista).

- **`customer_paquetes.py`** cambia el filtro de `Paquete.announced_by_phone == persona.telefono
  OR Paquete.recipient_phone == persona.telefono` a `Paquete.announced_by_phone.in_(telefonos) OR
  Paquete.recipient_phone.in_(telefonos)`, usando la lista del punto anterior. Los `conteos` por
  pestaña se calculan sobre este conjunto ampliado (ya es automático, cuentan sobre `paquetes`
  resultante del filtro).

- **Paleta de color fija de 5 posiciones**, una por cada posición posible del roster de
  `listar_ocupantes` (0=principal, 1..4=siguientes por antigüedad) — coherente con
  `MAX_OCUPANTES_ACTIVOS = 5` ya existente en `ocupante_service.py`. Reutiliza tonos ya
  establecidos en `docs/design-system/tokens.md` donde sea posible (los 4 roles semánticos +
  un quinto tono neutro-pero-distinguible), evitando los colores ya reservados para estado
  (ámbar/azul/verde/rojo de Anunciado/Recibido/Entregado/Cancelado) para que el avatar de
  Ocupante nunca se confunda visualmente con el badge de estado de la misma tarjeta.

- **Resolución de a qué Ocupante pertenece un Paquete** (para elegir el color): primero intenta
  matchear `recipient_phone` contra la lista de Teléfonos de Ocupantes del Apartamento; si no
  matchea (`recipient_phone` es `None` o pertenece a alguien fuera de la unidad), intenta
  `announced_by_phone`; si ninguno matchea, avatar neutro (gris, mismo tono que el fallback de
  Badges).

- **Ocupantes dados de baja (`desvinculado_en` no nulo) quedan fuera** del roster de colores y de
  la lista de Teléfonos que amplía el filtro — `listar_ocupantes` ya excluye histórico por
  defecto, se reutiliza tal cual.

- **Sin gate de privacidad ni opt-out** — el cliente confirmó explícitamente que la visibilidad
  compartida dentro del mismo Apartamento es el comportamiento deseado, no un descuido.

- **`/consultar` (vista pública) no cambia** — este spec es exclusivamente el alcance de
  `/mis-paquetes`.

## Testing Decisions

- Los tests verifican comportamiento observable (qué Paquetes aparecen, qué color se asigna a
  cada tarjeta vía su clase/atributo visible), nunca el orden interno de construcción de la
  consulta SQL.

- **`telefonos_activos_del_apartamento_de`**: tests de integración en `tests/data_model/`, mismo
  arnés que `tests/data_model/test_ocupante_service.py` (fixture `db_session`, marker
  `pytest.mark.integration`). Casos: Persona sin Apartamento (devuelve solo su propio Teléfono),
  Persona con Apartamento y varios Ocupantes activos (devuelve todos los Teléfonos), Ocupante
  dado de baja (no aparece), Ocupante sin Teléfono (no aporta nada a la lista, tampoco rompe).

- **`customer_paquetes.py` — alcance ampliado**: extender `tests/web/test_mis_paquetes.py`
  (arnés y helpers ya existentes, `_login_cliente`, `announce`). Casos: dos Ocupantes del mismo
  Apartamento ven ambos conjuntos de Paquetes combinados; una sesión sin Apartamento sigue viendo
  solo lo propio (regresión del comportamiento actual); un Ocupante dado de baja no contamina la
  vista de los demás.

- **Avatar de color por Ocupante**: extender el mismo archivo de tests web — Paquete cuyo
  Destinatario matchea un Ocupante conocido muestra su color; Destinatario "nombre sin teléfono"
  sin match muestra el avatar neutro; dos Ocupantes de la misma unidad nunca comparten color en
  la misma respuesta.

## Out of Scope

- Cualquier mecanismo de opt-out o control de privacidad por Ocupante — decisión de producto ya
  tomada explícitamente por el cliente (visibilidad compartida total dentro del Apartamento).
- Actualización en vivo (websocket/polling) si la composición del Apartamento cambia mientras la
  página ya está cargada — el alcance se resuelve en cada `GET /mis-paquetes`, no hace falta más.
- Persistencia del color asignado a un Ocupante a través del tiempo si el roster cambia de orden
  (alguien se da de baja, alguien nuevo se une) — el color se deriva de la posición actual en cada
  carga, puede cambiar si la composición cambia; no se requiere un color "fijo para siempre" por
  Persona.
- Cualquier cambio a `/consultar`, `/residentes`, `/announce` u otra ruta — exclusivamente
  `/mis-paquetes`.
- La asociación retroactiva de Paquetes huérfanos (`.scratch/asociacion-retroactiva-apartamento/`)
  es un spec aparte y no es requisito de este — una vez esos tickets se implementen, sus Paquetes
  corregidos aparecerán naturalmente en esta vista ampliada también, sin trabajo adicional acá.

## Further Notes

- Relación con `.scratch/asociacion-retroactiva-apartamento/`: temáticamente conectado (ambos
  giran en torno a "el Teléfono está bien vinculado a su Apartamento"), pero son independientes —
  este spec no bloquea ni depende de que esos tickets estén implementados primero.
- El límite `MAX_OCUPANTES_ACTIVOS = 5` ya existente es lo que hace segura la paleta fija de 5
  colores — si ese límite cambiara en el futuro, la paleta debe revisarse en el mismo cambio.

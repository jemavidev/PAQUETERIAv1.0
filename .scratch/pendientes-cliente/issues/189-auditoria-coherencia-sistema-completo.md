# 189 — Auditoría de coherencia de todo el sistema (paquetes ↔ residentes)

**Pedido original:** tras [[188]], el cliente siguió probando (FANTASMA 2, FANTASMA 3) y reportó el
mismo síntoma: "listo voy a probar lo que estas diciendo, pero necesito que antes analices todo el
sistema (vistas, modales, formularios, tabs...) y demas para confirmar que todo el sistema este
intercoinectado entre si, necesito que este unificado y se pueda hablar entre si."

**Status:** implementado

## Diagnóstico

Antes de esta auditoría se verificó en la base local que NINGUNO de los 4 paquetes de prueba del
cliente (FANTASMA 1/2/3, ESTE ES UN CLIENTE FANTASMA) tenía `recipient_name` realmente corregido --
seguía siendo el texto fantasma original, aunque el cliente creía haber completado el paso de elegir
un candidato. Confirmado por curl que el mecanismo de corrección en sí funciona perfecto server-side
-- el problema no era ahí.

Causa raíz real: `Paquete.corrected_at` es un timestamp COMPARTIDO entre `corregir_apartamento`
(solo asigna Torre/Apto) y `corregir_destinatario` (resuelve quién es el destinatario real) -- ver
ADR-0001 ("el esquema no distingue cuál de las dos correcciones ocurrió"). El ícono de advertencia
persistente (`_nombre_no_coincide`, ver más abajo) usaba `corrected_at is not None` como señal de
"ya resuelto" -- así que asignar SOLO la unidad (sin nunca resolver a nadie real) apagaba esa
advertencia PARA SIEMPRE. El toast de [[188]] solo se ve UNA VEZ justo después del redirect; sin la
advertencia persistente, no quedaba ninguna otra pista de que el paso seguía pendiente.

Se lanzó una auditoría (agente en background, mismo contexto de sesión) sobre TODAS las vistas,
modales, formularios y tabs que tocan la relación Paquete↔Ocupante↔Persona, buscando más instancias
de la misma clase de bug ("dos cosas se ven vinculadas sin estarlo de verdad"). 4 hallazgos
confirmados:

1. **`corrected_at` compartido** (ya diagnosticado arriba).
2. **Caja "Residentes de la unidad" ignoraba el estado de resolución.** En la misma tarjeta del
   modal "Ver", el link del título Torre/Apto SÍ estaba bien gateado (`persona_destino_id`, desde
   issue 100) -- pero la caja de abajo mostraba los residentes reales de la unidad
   INCONDICIONALMENTE (`p.residentes_unidad` no vacío), sin importar si el destinatario estaba
   realmente vinculado a alguno de ellos. Mecanismo independiente del de (1) -- el hallazgo clave:
   arreglar SOLO (1) no habría sido suficiente, (2) reproducía el mismo síntoma por su cuenta.
3. **Asimetría de capacidad entre las 3 entradas que resuelven destinatario.** "Recibir" y "Corregir
   destinatario" permiten elegir un candidato YA existente con un clic (`candidato_idx`). "Asignar
   apartamento" NO -- deliberado (comentario propio en el código, issue 149): ese modal se abre
   ANTES de elegir la unidad, así que no hay candidatos que pre-declarar sin fetch dinámico.
4. **`Ocupante.nombre` nunca se resincroniza tras editar `Persona.nombre`.** `agregar_ocupante`
   congela `Ocupante.nombre` una sola vez al crear (a propósito). Editar el nombre de un residente
   desde `/residentes` → tab Datos actualiza `Persona.nombre` pero ningún camino de código
   propagaba eso a `Ocupante.nombre` -- el picker de "Corregir destinatario" y la búsqueda seguían
   ofreciendo el nombre viejo, y elegirlo dejaba `recipient_name` sin coincidir con la Persona real
   (mismo síntoma, tercera vía independiente).

**Ronda 2 (mismo hilo, verificación en vivo):** al probar en localhost contra los propios paquetes
del cliente (FANTASMA 1/2/3), el ícono seguía sin aparecer. Causa: los 4 paquetes se anunciaron
"para mí mismo" (`Destinatario.yo_mismo()`) -- `candidatos_correccion` SIEMPRE incluye al Anunciante
como candidato válido (comodín para no bloquear Recibir/Asignar), así que `recipient_name` coincidía
trivialmente consigo mismo desde el principio, sin importar que Torre 2 · 302 (la unidad asignada
DESPUÉS) fuera de gente real (Angélica, Daniela, Rafael) con quienes esa persona no tenía ninguna
relación. Confirmado con el cliente (pregunta directa): una vez que hay unidad resuelta, "para mí
mismo" YA NO debe alcanzar por sí solo -- el destinatario debe coincidir con un Ocupante REAL de esa
unidad específica.

**Ronda 3 (mismo hilo, el cliente probó de nuevo con "FANTASMA 4"):** con el fix de ronda 2 ya
aplicado, el cliente reportó que el nombre y la Torre/Apto (dentro del modal "Ver") seguían siendo
clickeables -- llevaban a la ficha REAL de FANTASMA 4 (`persona_destino_id` sí resuelve, porque esa
Persona existe de verdad, creada al anunciar), pero esa ficha no tenía ningún apartamento asignado,
mientras `/paquetes` seguía mostrando "Torre 2 · Apt 302" en la misma fila -- y esa unidad, al
entrar a la ficha de Angélica (su Principal real), tampoco incluía a FANTASMA 4. Causa: los 2 links
(nombre y Torre/Apto, issues 100/101) solo comprobaban `persona_destino_id` (¿existe una Persona con
ese nombre/teléfono?) -- nunca si esa Persona es REALMENTE Ocupante de la unidad del snapshot, el
mismo criterio que ya se había corregido para la caja "Residentes de la unidad" (hallazgo 2) pero
que no se había extendido a estos 2 links, aunque comparten exactamente el mismo problema.

**Ronda 4 (el cliente probó de nuevo con "FANTASMA 4", vía `/diagnosing-bugs`):** las rondas 1-3
solo evitaban que la UI MINTIERA sobre un destinatario sin confirmar -- pero nada impedía que ese
estado incoherente se creara. El cliente lo señaló explícitamente: "pienzas que solo por esconder el
problema solucionaria la problematica... estas muy equivocado". Causa raíz de fondo: "Recibir" (el
paso de declarar unidad DENTRO del mismo modal) y "Asignar apartamento" trataban "asignar la unidad"
y "confirmar quién la recibe" como dos sub-pasos INDEPENDIENTES y opcionales -- decisión de diseño
original (`.scratch/ocupante-principal-escenarios` ticket 05), nunca cuestionada hasta ahora. Fix
real: la recepción física (`receive()`) ya NO se completa cuando la unidad tiene residentes reales y
el destinatario no coincide con ninguno -- se bloquea ANTES de `receive()`, no después. La unidad
asignada SÍ se conserva (información real y útil); guía/tipo/condición/fotos del intento bloqueado
se descartan a propósito. El modal "Recibir" se reabre con la unidad YA puesta, así que
`candidatos_correccion` ya trae a los residentes reales -- un segundo envío que elige uno completa
la recepción de verdad, sin segundo modal ni segunda visita. Alcance acotado deliberadamente: una
unidad GENUINAMENTE vacía (nadie vivió ahí todavía) sigue sin bloquear -- no hay nadie real con quien
el destinatario pudiera confundirse ahí, exigir "+ Nuevo residente" para el primer paquete de una
unidad nueva sería fricción sin ningún problema real que evitar.

**Ronda 5 (pedido explícito, flujo /announce "anunciar + recibir"):** el bloqueo de la ronda 4 es
correcto pero incompleto -- para el caso más común (alguien anuncia "para mí mismo" y el staff lo
recibe asignándole una unidad, con o sin residentes previos), el sistema YA tiene su identidad real
(nombre + teléfono/whatsapp, capturados al anunciar) y aun así obligaba a un segundo paso manual
re-tecleando esos mismos datos en "+ Nuevo residente". Ahora se autocompleta: "para mí mismo" sin
resolución explícita se resuelve solo, usando esos datos ya conocidos -- tanto en unidades vacías
(antes tampoco dejaba ningún Ocupante real ahí) como en unidades pobladas (antes bloqueaba). El
bloqueo de la ronda 4 se conserva intacto para el caso genuinamente ambiguo: un destinatario
declarado como un TERCERO que no coincide con el Anunciante, donde no hay ninguna identidad propia
con la que autocompletar.

## Cambio

- `packages.py`: `_nombre_no_coincide` (dependía de `corrected_at`) reemplazada por
  `_destinatario_sin_confirmar` -- mientras el paquete siga en `ESTADOS_CORREGIBLES`, compara
  `recipient_name` contra los candidatos REALES (`candidatos_correccion`: Ocupantes de la unidad ya
  resuelta, o el Anunciante) en cada lectura, ignorando `corrected_at` por completo. SIN unidad
  resuelta, cualquier candidato vale (incluido el Anunciante, comportamiento de siempre). CON unidad
  resuelta (ronda 2), el Anunciante YA NO alcanza por sí solo -- debe coincidir específicamente con
  un candidato que sea Ocupante REAL de esa unidad (`estado_ocupante` puesto, señal ya existente en
  `_construir_candidatos`). En estados terminales (ENTREGADO/CANCELADO, ya no accionable) conserva
  el criterio original más simple (aviso histórico contra el nombre del Anunciante) -- ahí sí sigue
  siendo válido, las dos correcciones solo pueden haber ocurrido mientras el paquete aún era
  corregible.
- `_resultados.html`: la caja "Residentes de la unidad" ahora exige también `not
  p.advertencia_nombre` -- se alinea con el link de Torre/Apto, que ya usaba la señal correcta.
  Textos de los 3 íconos de advertencia actualizados (ya no dicen literalmente "el nombre anunciado
  no coincide con el registrado", ahora cubren también el caso de unidad resuelta sin destinatario
  confirmado).
- `_resultados.html` (modal "Asignar apartamento"): agregado un texto explicando que, para vincular
  a alguien YA residente, hay que dejar "+ Nuevo residente" vacío y usar el redirect a "Corregir
  destinatario" que seguirá abriéndose después de guardar (issues 186/188) -- no se duplicó la
  capacidad de candidatos de un clic ahí (exigiría fetch dinámico, fuera de alcance dado que el
  camino de 2 pasos ya funciona y ahora es visible de forma persistente).
- `persona_service.py` (`update_datos_personales`): al cambiar `nombre`, ahora sincroniza también
  `Ocupante.nombre` de todos los Ocupantes ACTIVOS (`desvinculado_en IS NULL`) de esa Persona --
  update en bloque, `synchronize_session=False` (mismo patrón que
  `configuracion_conjunto_service.py`). Los Ocupantes históricos (dados de baja) se dejan intactos a
  propósito, mismo criterio que el resto del código (issue 166).
- `_resultados.html` (ronda 3): los 2 links que dependían solo de `p.persona_destino_id` -- el
  nombre del título del modal "Ver" (issue 100) y la Torre/Apto debajo (issue 100/issue 101) --
  ahora exigen también `not p.advertencia_nombre`, la MISMA señal que ya gatea la caja "Residentes
  de la unidad" (hallazgo 2). Sin confirmar, ambos quedan como texto plano en vez de enlazar a una
  ficha real pero vacía. El ícono de WhatsApp (`_persona_para_notificar`) y el ícono de "cambio
  reciente de apartamento" NO se tocaron -- ambos siguen usando `persona_destino_id` sin este guard
  a propósito (poder contactar a la persona real no depende de que esté confirmada como residente;
  el ícono de cambio reciente ya solo aparece si hay historial real de mudanza, no hay nada que
  ocultar ahí).
- `packages.py` (ronda 4 -- el fix de fondo): nueva `_destinatario_coincide_con_candidato_real`,
  extraída de `_destinatario_sin_confirmar` para compartir EXACTAMENTE el mismo criterio entre la
  advertencia (se puede ignorar) y este bloqueo real (no se puede ignorar) -- nunca dos versiones
  que puedan divergir. Estricto solo cuando la unidad resuelta YA tiene al menos un Ocupante real
  (`hay_ocupantes_reales`); laxo (Anunciante alcanza) sin unidad o con unidad genuinamente vacía.
  `receive_action`: justo antes de `receive()`, si la unidad (recién declarada en este envío, o ya
  puesta de antes) tiene residentes reales y el destinatario no coincide con ninguno, NO se llama a
  `receive()` -- se comitea solo la asignación de unidad y se redirige a reabrir el mismo modal
  "Recibir" (`?recibir=<id>&aviso=recepcion_pendiente`, nuevo `_AVISO_RECEPCION_PENDIENTE`) en vez
  de a "Corregir destinatario". El viejo redirect post-`receive()` de [[187]] quedó retirado -- ya
  es inalcanzable (si el destinatario no estuviera confirmado, ya se habría bloqueado antes).
  `assign_apartment_action`: mismo criterio aplicado por consistencia -- ya no reabre "Corregir"
  cuando la unidad recién asignada está vacía o el Anunciante ya coincide (sería redundante).
- `packages.py` (ronda 5): nueva `_autocompletar_nuevo_residente_yo_mismo` -- si el destinatario es
  "para mí mismo" y todavía NO es Ocupante real de la unidad ya resuelta, devuelve `(nombre,
  contacto)` del propio Anunciante; `None, None` si no aplica (no es yo-mismo, sin contacto propio,
  o ya es Ocupante real ahí -- nada que hacer). Reusada por `receive_action` (antes de la resolución
  explícita) y `assign_apartment_action` (antes de `if nombre_nuevo_v`) -- ambas tratan el resultado
  EXACTAMENTE igual que si "+ Nuevo residente" se hubiera llenado a mano, mismas protecciones
  (`_resolver_desde_candidato`, `permitir_mover=True` sin `mover_de_otra_unidad`): si esa Persona ya
  es Ocupante activo de OTRA unidad, el autocompletado no la muda en silencio -- cae al mismo rechazo
  de siempre (`mensaje_ya_ocupante_activo`, 400, "Mover acá"), la unidad queda igual asignada (mismo
  comportamiento que la entrada manual con el mismo conflicto) pero el destinatario sigue sin
  confirmar -- el ícono persistente de las rondas 1-4 sigue avisando.

## Verificación

- Test que fallaba tras el primer intento de arreglar (1) sin (4)/(2) considerados --
  `test_advertencia_no_es_clickeable_en_cancelado` -- corregido separando el criterio por estado
  (corregible vs. terminal) en vez de romper el aviso histórico ya acordado con el cliente.
- 2 tests actualizados (`test_modal_ver_muestra_residentes_de_la_unidad`,
  `test_modal_ver_residentes_icono_de_email_solo_si_existe`) -- registran al Anunciante también como
  Ocupante real de la unidad, para seguir probando lo que probaban antes (contenido de la caja, ícono
  de email) bajo la regla nueva.
- 1 test nuevo: `test_asignar_apartamento_a_persona_que_no_vive_ahi_sigue_con_advertencia` --
  reproduce el caso real FANTASMA 2 (anuncia para sí mismo sin unidad, staff asigna una unidad real
  ajena sin resolver residente): confirma que la advertencia se prende y la caja de residentes queda
  oculta.
- 2 tests nuevos en `test_persona_service.py`: sincroniza Ocupante activo / no toca Ocupante
  desvinculado.
- 1 test actualizado (`test_modal_ver_torre_apto_enlaza_a_tab_residentes`) + 1 test nuevo
  (`test_modal_ver_links_no_aparecen_si_destinatario_no_es_ocupante_de_la_unidad`, reproduce el caso
  real FANTASMA 4 con `/asignar-apartamento` real) para la ronda 3.
- Suite completa `tests/web/` + `tests/data_model/`: **1111 passed** (ronda 2), reverificada tras
  ronda 3 (ver resultado en la conversación).
- Verificado en vivo en `localhost:8010` contra el paquete real "FANTASMA 4" (5WUB) que motivó la
  ronda 3: el nombre y la Torre/Apto ya NO son clickeables dentro del modal "Ver" -- quedan como
  texto plano, mientras "Torre 2 · Apt 302" se sigue mostrando (la dirección asignada sigue siendo
  visible, solo deja de implicar una ficha resuelta). También reverificado FANTASMA 1/2/ESTE ES UN
  CLIENTE FANTASMA de la ronda 2, siguen mostrando el ícono naranja persistente. FANTASMA 3 (MHAF)
  quedó resuelto durante la verificación de la ronda 2 (se corrigió a ANGELICA ARRAZOLA, candidata
  real de Torre 2 · 302) -- dato de prueba del cliente, corrección real y válida, no revertida.

**Ronda 4 (`/diagnosing-bugs`, fix de fondo):**
- Auditoría de impacto sobre los 22 usos de `POST /recibir` en la suite ANTES de tocar código --
  20 no se ven afectados (sin unidad involucrada, o resolución ya en el mismo envío); solo 1
  necesitaba reescritura real.
- `test_recibir_declara_apartamento_sin_residente_no_completa_la_recepcion` (reemplaza el test de
  [[187]]): reproduce el caso real -- ahora confirma que la recepción NO se completa (queda
  ANUNCIADO, sin guía), la unidad SÍ queda asignada, y reabre "Recibir" (no "Corregir") con
  candidatos reales.
- `test_recibir_declara_apartamento_en_unidad_vacia_sigue_completando` (guard nuevo): una unidad
  genuinamente vacía sigue completando la recepción como siempre.
- `test_recibir_bloqueado_se_completa_al_elegir_el_candidato_real_despues` (nuevo): cierra el ciclo
  completo -- tras el bloqueo, un segundo envío que elige al candidato real sí termina de recibir.
- Suite completa `tests/web/` + `tests/data_model/` tras ronda 4: **1114 passed**.
- Reproducción en vivo del escenario EXACTO reportado por el cliente (paquete nuevo "FANTASMA 5",
  anunciado sin unidad, "Recibir" con Torre 2 · 302 sin resolver residente) contra `localhost:8010`:
  el POST bloqueó la recepción (quedó ANUNCIADO, sin guía), redirigió a `?recibir=<id>&aviso=
  recepcion_pendiente`, el modal "Recibir" reabierto mostró a ANGELICA ARRAZOLA como candidata real.
  Un segundo POST eligiéndola completó la recepción de verdad (`RECIBIDO`, `recipient_name=
  "ANGELICA ARRAZOLA"`, guía capturada). Confirmado en `/paquetes` que el nombre y la Torre/Apto ya
  enlazan a la ficha real de Angélica -- coherente de punta a punta, no solo "no miente".

**Ronda 5 (pedido explícito, flujo /announce "anunciar + recibir"):**
- 6 tests de rondas 2/4 rotos por el nuevo autocompletado (todos eran "para mí mismo" contra una
  unidad ya resuelta -- exactamente el caso que ahora se autocompleta en vez de bloquear/advertir) --
  reescritos para probar el autocompletado, con guards nuevos para el caso NO-yo-mismo (que sigue
  bloqueando/advirtiendo igual que antes) y para el caso "ya es Ocupante de otra unidad" (no muda en
  silencio).
- Tests nuevos: `test_recibir_declara_apartamento_autocompleta_al_anunciante_como_residente`,
  `test_recibir_declara_apartamento_en_unidad_vacia_autocompleta_tambien`,
  `test_recibir_declara_apartamento_sin_ser_yo_mismo_sigue_bloqueando`,
  `test_asignar_apartamento_a_si_mismo_autocompleta_como_residente`,
  `test_asignar_apartamento_sin_ser_yo_mismo_sigue_con_advertencia`,
  `test_asignar_apartamento_sin_nuevo_residente_autocompleta_al_anunciante`,
  `test_asignar_apartamento_sin_ser_yo_mismo_no_crea_ocupante`,
  `test_asignar_apartamento_ya_ocupante_de_otra_unidad_no_autocompleta_en_silencio`.
- Suite completa `tests/web/` + `tests/data_model/` tras ronda 5: ver resultado en la conversación.
- Verificado en vivo en `localhost:8010`, reproduciendo el flujo /announce completo con un paquete
  nuevo ("FANTASMA 6"): anunciado sin unidad, recibido con Torre 2 · 302 (unidad de Angélica, con
  Rafael y Daniela también) SIN elegir a nadie -- la recepción se completó en un solo paso
  (`RECIBIDO`, guía capturada, sin bloqueo), y FANTASMA 6 quedó registrado como Ocupante REAL de esa
  unidad (`apartamento_actual_id` sincronizado). Confirmado en `/residentes/<id-de-Angélica>?tab=
  residentes` que FANTASMA 6 aparece listado como residente de la unidad -- el hueco que el cliente
  reportó ("esto no está pasando en este momento") queda cerrado.

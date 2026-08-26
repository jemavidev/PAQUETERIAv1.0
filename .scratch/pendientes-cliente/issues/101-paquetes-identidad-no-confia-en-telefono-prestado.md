# 101 — `/paquetes` modal "Ver": el link de identidad no debe confiar en un teléfono prestado

**Pedido original (cliente):**
"veo algo tipo bug para la vista /paquetes, para el paquete con codigo
"J2PY" veo que esta anunciado a nombre de "JESUS VILLALOBOS" con "Torre 2
· Apt 302" y veo que este mismo usuario al parecer esta en 2 apartamentos
registrado, no entiendo si es un cambio de estado que no actualice,
analiza y dime que ves y como se interpreta, no se si otros usuarios
presenten algun problema"

**Status:** implementado

## Diagnóstico

No es un residente en 2 apartamentos a la vez -- la BD tiene una
restricción única (`uq_ocupantes_persona_activo`) que lo impide. Es un
bug real de identidad cruzada:

- Jesús Villalobos no tiene teléfono propio registrado (solo WhatsApp). Se
  auto-anunció el paquete J2PY (`Destinatario.yo_mismo()`) mientras vivía
  como Ocupante (no Principal) de Torre 2 · Apt 302.
- Issue 163 (`.scratch/pendientes-cliente`) llena `recipient_phone` con el
  teléfono del Principal de la unidad cuando el destinatario no tiene uno
  propio -- a propósito, para que SIEMPRE haya a quién notificar. En ese
  momento el Principal de Torre 2 · 302 era Angélica Arrazola.
- `packages.py` (`_listar`) usaba ESE `recipient_phone` para resolver
  `persona_destino_id` -- la Persona a cuya ficha de `/residentes` enlaza
  el título del modal (y, desde issue 100, el link de Torre/Apto). Como el
  teléfono es de Angélica, el link "JESUS VILLALOBOS" apuntaba a la ficha
  de Angélica, en su apartamento (Torre 2) -- pareciendo que Jesús "vivía"
  ahí, cuando su unidad actual real es Torre 1 · Apt 302.
- Confirmado que NO es un caso aislado: query contra toda la tabla
  `paquetes` (recipient_phone → Persona con nombre distinto de
  recipient_name) encontró un segundo caso el mismo día (`NME3`, "LAIS
  HERNANDEZ" con el teléfono de su co-residente/anunciante "RAFAEL
  TORRES") -- mismo mecanismo, cualquier residente sin teléfono propio que
  reciba un paquete lo puede disparar.
- El aviso existente "nombre no coincide" no lo atrapa: compara contra el
  Anunciante (no contra el dueño del teléfono resuelto), y se apaga para
  siempre en cuanto el paquete pasa por cualquier corrección.

## Implementación

- `packages.py` (`_listar`): se separó la resolución en dos --
  `persona_destino_contacto` (contacto "prestado", lo que `recipient_
  phone` trae congelado tal cual -- issue 163) y `persona_destino` (para
  `persona_destino_id`, el link de identidad): el match por teléfono solo
  se acepta si el nombre de esa Persona coincide con `recipient_name`; si
  no coincide (o no hubo match), cae al fallback por nombre ya existente
  (`_personas_por_nombre`, antes limitado a paquetes sin ningún teléfono,
  ahora corre para todos).
- Sin ningún match confiable, `persona_destino_id` queda `None` -- el
  nombre se queda como texto plano, más seguro que enlazar a la persona
  equivocada (mismo criterio que el caso ya existente "nombre no
  coincide").

### Seguimiento el mismo día: ícono de WhatsApp

Pregunta del cliente en vivo: "¿cómo se comporta si el destinatario SÍ
tiene usuario de WhatsApp (pero no teléfono)?" -- antes del seguimiento,
el ícono de WhatsApp de la fila (`whatsapp_url_destinatario`) seguía
usando SIEMPRE `persona_destino_contacto` (el contacto prestado), incluso
cuando el destinatario identificado SÍ tenía su propio WhatsApp -- Jesús
le escribía a Angélica en vez de a él mismo. Corregido con la finalidad
explícita del cliente: "que se tenga siempre un lugar donde se pueda
notificar, ya sea whatsapp/teléfono propio o del residente principal".

- Nueva función `_persona_para_notificar(persona_identidad, persona_
  prestada)` (`packages.py`): prioridad explícita -- 1) canal propio del
  destinatario identificado (WhatsApp o teléfono, cualquiera de los dos),
  2) si no tiene ninguno, el contacto prestado de issue 163. Reemplaza el
  parche en línea del primer intento.
- `p.whatsapp_url_destinatario` ahora se calcula sobre el resultado de esa
  función, no directo sobre `persona_destino_contacto`.

### Segundo seguimiento el mismo día: "Residentes de la unidad" seguía confundiendo

El cliente, ya con el link de identidad corregido, seguía viendo el mismo
tipo de confusión: en el modal de J2PY, debajo de "JESUS VILLALOBOS" y
"Torre 2 · Apt 302" aparecía "Residentes de la unidad: ANGELICA ARRAZOLA ·
Principal, DANIELA ARRAZOLA" -- se leía como si fueran compañeros de
unidad de Jesús. Confirmado bidireccional con dos ejemplos más del
cliente: los paquetes de Angélica (`UKT7`) y Daniela (`VQV3`), anunciados
cuando las tres personas vivían juntas en Torre 2 · 302, ahora muestran
"Residentes de la unidad: JESUS VILLALOBOS · Principal" -- el espejo
exacto, porque Jesús se quedó ahí como Principal después de que ellas se
mudaran (o él se mudó y quedó otro Principal -- de cualquier forma, el
snapshot de esos paquetes viejos sigue apuntando a la unidad que
compartían).

Diagnóstico: "Residentes de la unidad" (`packages.py`, `p.residentes_
unidad`) es un mecanismo DISTINTO al link de identidad -- lista quien vive
HOY en la dirección CONGELADA del snapshot (`apto`, resuelto por
`snapshot_torre`/`snapshot_apartamento`), no quien vive con el
destinatario. Es dato correcto en sí (nunca fue el bug de identidad), pero
sin ninguna aclaración, tres o cuatro personas que alguna vez compartieron
una unidad terminan viéndose "vinculadas" entre sí en cada paquete viejo,
indefinidamente.

Primer intento (descartado): un aviso de texto arriba del listado --
"Dirección de este paquete -- {{ p.recipient_name }} ya no vive aquí." --
manteniendo el listado visible siempre que el paquete estuviera CERRADO
(ENTREGADO/CANCELADO), como referencia histórica. El cliente lo rechazó en
la vuelta siguiente (ejemplo real: UKT7, de Angélica, ya Entregado, seguía
mostrando "JESUS VILLALOBOS · Principal"): "en caso que no viva allí NO
DEBE APARECER" -- sin excepción por estado, ni siquiera en paquetes ya
cerrados, porque esas personas "no tienen relación alguna con los
paquetes actuales, solo tuvieron algo de relación entre sí" (fueron
co-residentes en el pasado, nada más).

Segundo intento (también descartado): ocultar `residentes_unidad` por
completo cuando el destinatario ya no vive en la unidad del snapshot, sin
excepción por estado. El cliente lo rechazó de inmediato con el mismo
ejemplo (UKT7): "veo que Angélica y Daniela no aparecen... estas SÍ están
asociadas directamente y deberían aparecer" -- Angélica y Daniela viven
juntas HOY (en Torre 2 · 302, una unidad DISTINTA a la del snapshot de
este paquete viejo), esa relación actual es real y debía seguir visible.
Ocultar todo perdía esa información genuina junto con la falsa (Jesús).

Fix final (tercer intento): "Residentes de la unidad" ya no sigue la
unidad del SNAPSHOT -- sigue la unidad ACTUAL del destinatario ya
identificado. `packages.py`, `_listar`: nuevo atributo transitorio por
paquete `p._apartamento_id_residentes` = `persona_destino.apartamento_
actual_id` si el destinatario tiene una unidad propia conocida, si no la
del snapshot (`apto.id`) como antes. Como esa unidad puede no ser el
snapshot de NINGÚN paquete de la página (la unidad nueva de alguien que
se mudó), se agregó un batch adicional (mismo patrón ya usado por
`cambios_recientes_de_apartamento`, issue 165: un segundo loop porque el
set completo de ids no se conoce hasta que termina el loop principal) que
completa `ocupantes_por_apartamento` con los ids faltantes antes de armar
la lista final. `apartamento_actual_id is None` sigue sin contar como
mudanza -- cae al snapshot como siempre (mismo bug real evitado que en el
segundo intento, atrapado por `test_modal_ver_muestra_residentes_de_la_
unidad`, ya existente).

Resultado en los 3 paquetes reales: J2PY (Jesús) ahora muestra su unidad
ACTUAL (Torre 1 · 302, solo él); UKT7 (Angélica) y VQV3 (Daniela) ahora
muestran su unidad ACTUAL compartida (Torre 2 · 302, las dos juntas) --
ninguno de los tres vuelve a mezclar a Jesús con Angélica/Daniela.

## Verificación (segundo seguimiento, versión final)

- `tests/web/test_packages.py`:
  `test_modal_ver_residentes_de_la_unidad_sigue_al_destinatario_que_se_
  mudo` -- reproduce el caso real completo (Angélica anuncia un paquete
  viviendo en Torre 1 · 302, luego se muda a Torre 2 · 302 donde Daniela
  ya vive, paquete ENTREGADO) y confirma que "Residentes de la unidad"
  muestra a Angélica + Daniela (unidad actual), sin excepción por estado.
  `test_modal_ver_sin_aviso_si_el_destinatario_sigue_en_la_unidad` --
  contraparte: sin mudanza, comportamiento sin cambios (caso normal, la
  inmensa mayoría de los paquetes). `test_modal_ver_muestra_residentes_
  de_la_unidad` (ya existente): destinatario sin unidad propia conocida
  (Anunciante con `apartamento=` explícito) -- cae al snapshot como
  siempre, sigue pasando. Suite completa de `test_packages.py`: 182
  tests, todos pasan. Suite completa del proyecto (`pytest` sin filtro):
  1083 tests, todos pasan.
- Verificado en vivo contra el ambiente local (localhost:8010) con curl
  autenticado, en los 3 paquetes reales que el cliente señaló: J2PY
  (Jesús solo, su unidad actual), UKT7 y VQV3 (Angélica + Daniela juntas,
  su unidad actual compartida) -- confirmado que ninguno de los tres
  mezcla a Jesús con ellas.
- Pendiente: deploy a test.papyrus.com.co (junto con el resto de este
  issue y el 100 -- ninguno de los cambios de hoy está desplegado
  todavía, solo local).

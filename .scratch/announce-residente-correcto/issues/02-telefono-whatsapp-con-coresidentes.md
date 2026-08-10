# 02 — Teléfono/WhatsApp con co-residentes: elegir el destinatario correcto

**What to build:** al identificar en `/announce` por Teléfono o WhatsApp, si la Persona encontrada es Ocupante activo de una unidad con **más de un residente activo**, el sistema deja de saltar directo a la tarjeta Anunciar/Recibir -- en su lugar muestra la unidad y su lista completa de residentes (reusando la misma pantalla que ya usa hoy el camino Torre+Apartamento: lista de residentes, Principal primero, + "Nueva persona"), para que el staff elija a nombre de quién va el paquete. La Persona identificada por Teléfono/WhatsApp aparece marcada con un badge **"Anunciante"** en esa lista (mismo patrón visual que el badge "Principal" ya existente).

Sin importar a qué residente de la lista se le anuncie (incluyendo si se da de alta uno nuevo), el **Anunciante registrado en el Paquete es siempre la Persona identificada por el Teléfono/WhatsApp tecleado** -- nunca se resuelve a partir del residente elegido como destinatario (`paquete_service.announce()` ya soporta esto vía sus parámetros `anunciante_telefono`/`anunciante_whatsapp`, independientes de la resolución del `Destinatario` -- no requiere cambios de firma). El camino Torre+Apartamento existente NO cambia: sigue resolviendo el Anunciante vía `anunciante_para_ocupante` sin cambios, porque ahí nunca se conoce con certeza quién está llamando.

Si la Persona identificada por Teléfono/WhatsApp NO tiene co-residentes (vive sola, o no tiene apartamento asociado), el comportamiento de hoy se mantiene exactamente igual: tarjeta directa, un clic, sin pantalla intermedia. El botón "Recibir" (ticket 06 de `announce-rapido`) sigue funcionando igual desde este nuevo camino.

**Blocked by:** None técnicamente (funciona con cualquier `Ocupante` ya existente, sin importar cómo se haya creado) — conviene desplegarse después del 01 para que el padrón de Ocupantes esté completo desde el arranque, pero no lo requiere para funcionar correctamente.

**Status:** implementado

## Hallazgos de code-review (corregidos antes de desplegar)

- **Comentario incorrecto (Standards):** el docstring nuevo de `_anunciar_para` afirmaba "mismo criterio que el camino 1 (preferir Teléfono si por algún motivo llegaran los dos)" -- falso, el camino 1 en el mismo archivo RECHAZA explícitamente ese caso ("Identifica a la persona antes de anunciar."), no prefiere ninguno en silencio. Corregido: el comentario ahora explica por qué son dos guards distintos a propósito (uno reacciona a lo que el staff tecleó, el otro a un hidden field que la propia app generó y que la UI nunca deja llegar con ambos a la vez).
- **Test reforzado (Spec):** `test_elegir_a_quien_llama_funciona_como_yo_mismo` solo verificaba nombre/`announced_by_persona_id` -- se agregaron los asserts de `announced_by_phone`/`recipient_phone` para confirmar que el resultado es realmente equivalente a "yo mismo", no solo parecido.

- [x] Identificar por Teléfono a una Persona Ocupante de una unidad con 2+ residentes activos muestra la lista de esa unidad (Principal primero) + "Nueva persona", en vez de la tarjeta directa.
- [x] La Persona identificada por Teléfono aparece en esa lista marcada con el badge "Anunciante".
- [x] Mismo comportamiento para WhatsApp.
- [x] Elegir un residente de la lista (distinto de quien identificó) y anunciar deja el Paquete con `announced_by_persona_id` = la Persona del Teléfono/WhatsApp tecleado, y `recipient_name`/destinatario = el residente elegido.
- [x] Elegir a la propia Persona identificada (que también aparece en su propia lista de residentes) y anunciar funciona igual que "yo mismo" hoy.
- [x] Dar de alta un residente nuevo desde esta pantalla y anunciarle funciona igual que el camino equivalente de Torre+Apartamento, con el Anunciante = quien identificó por Teléfono/WhatsApp.
- [x] Identificar por Teléfono/WhatsApp a una Persona sin co-residentes (vive sola, o sin apartamento) mantiene el atajo directo de hoy sin cambios -- test de regresión.
- [x] El camino Torre+Apartamento existente no cambia ningún comportamiento -- tests de regresión de `announce-rapido` siguen pasando sin modificarse.
- [x] "Recibir" funciona desde este nuevo camino igual que en los demás caminos de `/announce`.
- [x] Verificación manual en navegador real (contra el ambiente local persistente, `scripts/paquetex_dev_up.sh` + Playwright): tecleado el teléfono de "Mamá" (Principal, con "Hijo" como co-residente sin contacto propio) -- aparece la lista de la unidad con "Mamá" marcada Principal + Anunciante; elegido "Hijo" y Anunciado -- toast confirma "Anunciado para HIJO...", y en base de datos el Paquete queda con `announced_by_persona_id`/`announced_by_phone` = los de Mamá y `recipient_name` = "HIJO...". Sin errores de consola.

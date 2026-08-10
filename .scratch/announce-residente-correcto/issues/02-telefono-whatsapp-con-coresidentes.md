# 02 — Teléfono/WhatsApp con co-residentes: elegir el destinatario correcto

**What to build:** al identificar en `/announce` por Teléfono o WhatsApp, si la Persona encontrada es Ocupante activo de una unidad con **más de un residente activo**, el sistema deja de saltar directo a la tarjeta Anunciar/Recibir -- en su lugar muestra la unidad y su lista completa de residentes (reusando la misma pantalla que ya usa hoy el camino Torre+Apartamento: lista de residentes, Principal primero, + "Nueva persona"), para que el staff elija a nombre de quién va el paquete. La Persona identificada por Teléfono/WhatsApp aparece marcada con un badge **"Anunciante"** en esa lista (mismo patrón visual que el badge "Principal" ya existente).

Sin importar a qué residente de la lista se le anuncie (incluyendo si se da de alta uno nuevo), el **Anunciante registrado en el Paquete es siempre la Persona identificada por el Teléfono/WhatsApp tecleado** -- nunca se resuelve a partir del residente elegido como destinatario (`paquete_service.announce()` ya soporta esto vía sus parámetros `anunciante_telefono`/`anunciante_whatsapp`, independientes de la resolución del `Destinatario` -- no requiere cambios de firma). El camino Torre+Apartamento existente NO cambia: sigue resolviendo el Anunciante vía `anunciante_para_ocupante` sin cambios, porque ahí nunca se conoce con certeza quién está llamando.

Si la Persona identificada por Teléfono/WhatsApp NO tiene co-residentes (vive sola, o no tiene apartamento asociado), el comportamiento de hoy se mantiene exactamente igual: tarjeta directa, un clic, sin pantalla intermedia. El botón "Recibir" (ticket 06 de `announce-rapido`) sigue funcionando igual desde este nuevo camino.

**Blocked by:** None técnicamente (funciona con cualquier `Ocupante` ya existente, sin importar cómo se haya creado) — conviene desplegarse después del 01 para que el padrón de Ocupantes esté completo desde el arranque, pero no lo requiere para funcionar correctamente.

**Status:** ready-for-agent

- [ ] Identificar por Teléfono a una Persona Ocupante de una unidad con 2+ residentes activos muestra la lista de esa unidad (Principal primero) + "Nueva persona", en vez de la tarjeta directa.
- [ ] La Persona identificada por Teléfono aparece en esa lista marcada con el badge "Anunciante".
- [ ] Mismo comportamiento para WhatsApp.
- [ ] Elegir un residente de la lista (distinto de quien identificó) y anunciar deja el Paquete con `announced_by_persona_id` = la Persona del Teléfono/WhatsApp tecleado, y `recipient_name`/destinatario = el residente elegido.
- [ ] Elegir a la propia Persona identificada (que también aparece en su propia lista de residentes) y anunciar funciona igual que "yo mismo" hoy.
- [ ] Dar de alta un residente nuevo desde esta pantalla y anunciarle funciona igual que el camino equivalente de Torre+Apartamento, con el Anunciante = quien identificó por Teléfono/WhatsApp.
- [ ] Identificar por Teléfono/WhatsApp a una Persona sin co-residentes (vive sola, o sin apartamento) mantiene el atajo directo de hoy sin cambios -- test de regresión.
- [ ] El camino Torre+Apartamento existente no cambia ningún comportamiento -- tests de regresión de `announce-rapido` siguen pasando sin modificarse.
- [ ] "Recibir" funciona desde este nuevo camino igual que en los demás caminos de `/announce`.
- [ ] Verificación manual en navegador real (skill `run`): flujo completo de Teléfono con co-residentes, elegir un residente distinto, confirmar el Anunciante correcto en el Paquete resultante, sin errores de consola.

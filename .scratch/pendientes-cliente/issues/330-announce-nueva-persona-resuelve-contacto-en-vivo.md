# 330 — `/announce`: "+ Nueva persona" resuelve el Teléfono/WhatsApp EN VIVO

**Pedido original (cliente):** "Para el formulario de 'Nueva persona' sería bueno que tenga el
mismo comportamiento que la vista de /anunciar, la diferencia es que en esta ocasión se podrá
ingresar el usuario de whatsapp o el número de teléfono y como estamos logueados como staff podría
ser posible que solo con ese dato se traigan los datos de este residente si existe, con el fin de
saber dónde vive y si existe, en caso que no exista, se debe habilitar un campo para colocar el
nombre."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Decisiones de alcance (mini-diseño, confirmadas con el cliente antes de implementar)

1. Contacto ya Ocupante activo de OTRA unidad: se oculta Nombre, aviso con la unidad de origen, y
   el checkbox `mover_de_otra_unidad` queda PRE-MARCADO (el staff lo puede desmarcar si fue un
   error de tipeo).
2. Contacto ya Ocupante activo de ESTA MISMA unidad: aviso + formulario deshabilitado (Anunciar y
   Recibir), evita crear un duplicado -- el staff usa la fila de esa persona en la lista de arriba.
3. Contacto que ya es una Persona CONOCIDA por el sistema pero SIN Ocupante activo en ningún lado
   (ej. anunció un paquete `yo_mismo` alguna vez): mismo trato que "encontrado" -- se oculta
   Nombre, se usa su nombre real, sin nota de mudanza (no hay de dónde moverla).

## Diseño

Mismo espíritu que el campo único de `/announce`: como el staff ya está autenticado, no hace falta
volver a preguntar un nombre que el sistema ya conoce. Reusa `buscar_persona_por_telefono`/
`buscar_persona_por_whatsapp` y `_clasificar` (mismas funciones del campo principal) más
`ocupante_activo_de_persona` para distinguir los 4 estados.

El campo "Teléfono o WhatsApp" se reordenó ARRIBA del área reactiva (antes iba después de Nombre) --
mismo patrón que el campo único principal (`#announce-q` → `#announce-resultado`).

## Implementación

- `app/domain/notificacion_service.py`/`app/domain/ocupante_service.py`: sin cambios -- toda la
  lógica de resolución reusa funciones ya existentes.
- `app/web/routes/announce_new.py`:
  - `GET /announce/identificar-contacto` (nuevo) -- 4 estados: `nuevo` (default, pide Nombre),
    `misma_unidad` (bloquea), `otra_unidad` (checkbox pre-marcado), `conocido_sin_unidad` (nombre
    real, sin checkbox). Siempre devuelve un fragmento completo y válido, nunca vacío.
  - `POST /announce` (camino 3, "Nueva persona"): el chequeo de `nombre` requerido se movió a
    DESPUÉS de resolver si el contacto ya es una Persona conocida -- antes exigía `nombre` siempre,
    aunque `agregar_ocupante`/`mover_ocupante` fueran a ignorarlo (bug real que este mismo pedido
    hizo evidente: el campo Nombre ahora se oculta client-side quando no hace falta, así que el
    servidor no puede seguir exigiéndolo).
- `app/web/templates/components/_nueva_persona_datos.html` (nuevo, macro `datos_nueva_persona`):
  contenido reactivo de la zona Nombre -- compartido por el render inicial
  (`_identificar_unidad.html`, estado `nuevo`) y por la respuesta del nuevo endpoint, para que
  nunca diverjan.
- `app/web/templates/announce_new/_identificar_contacto.html` (nuevo): plantilla delgada que solo
  invoca el macro de arriba -- la respuesta HTTP de `GET /announce/identificar-contacto`.
- `app/web/templates/announce_new/_identificar_unidad.html`: campo `contacto` reordenado antes del
  `<div id="nueva-persona-datos">`; el checkbox `mover_de_otra_unidad` estático (con el texto fijo
  de [[327]]) se retiró de acá -- ahora vive DENTRO del macro, visible solo en el estado
  `otra_unidad`.
- `app/web/templates/announce_new/form.html`: nuevo listener `input` (debounced, delegado sobre
  `#announce-resultado`) que llama al endpoint y reemplaza `#nueva-persona-datos` -- con una guarda
  extra (compara el HTML recibido contra el último pintado) para no pisar lo que el staff ya haya
  tecleado en Nombre mientras el contacto sigue sin calzar con nadie. También activa/desactiva los
  botones Anunciar/Recibir de ese mismo form según `[data-bloqueo-envio]` esté presente.

## Verificación

- 6 tests nuevos para `GET /announce/identificar-contacto` (los 4 estados + sesión + valor vacío).
- 2 tests nuevos para el fix de `POST /announce` (nombre vacío ya no falla cuando el contacto
  resuelve a una Persona conocida, tanto mudando como sin unidad).
- Suite completa `tests/web/test_announce_new.py`: 91/91 en verde.
- Regresión: `tests/web/test_announce.py` + `tests/data_model/test_ocupante_service.py` +
  `tests/data_model/test_announce_paquete.py`: 188/188 en verde.
- No se pudo verificar visualmente en navegador en esta sesión (sin Chrome conectado) -- el
  comportamiento del JS (debounce, guarda anti-pisado, deshabilitar botones) queda pendiente de
  confirmación visual del cliente en test.papyrus.com.co.

## Comments

**Corrección tras `code-review` (mismo día, pedido explícito: "analiza todo lo que hicimos hoy...
con el fin de saber que todo esté bien"):** el eje Spec del review encontró que el formulario "+
Nueva persona" tenía su PROPIO par Anunciar/Recibir incondicional (`_identificar_unidad.html`),
sin el gate de `autoriza_recepcion_automatica` que [[326]] ya le había puesto a la tarjeta de
residente existente -- un residente nuevo, o uno que esta misma resolución en vivo encuentra como
Persona conocida con la bandera en `False`, podía presionar Recibir y saltarse por completo el
paso de pedir autorización. Confirmado leyendo el código, no solo el reporte del sub-agente.

Corregido:
- Los botones Anunciar/Recibir/WhatsApp se extrajeron a un macro compartido
  (`components/_botones_anunciar_recibir.html`), usado tanto por `_persona_resuelta.html` (326)
  como por `_nueva_persona_datos.html` (330) -- ya no pueden divergir entre sí.
- `GET /announce/identificar-contacto` ahora calcula `_info_autorizacion` sobre la Persona
  resuelta (mismos 2 estados que ya la tenían, `otra_unidad`/`conocido_sin_unidad`) y la propaga.
- El estado `misma_unidad` se simplificó: ya no renderiza NINGÚN botón (antes los deshabilitaba
  por JS vía `[data-bloqueo-envio]`) -- más simple y sin depender de JS para bloquear el envío.
  Ese mecanismo (`[data-bloqueo-envio]` + el paso de `form.html` que deshabilitaba botones) se
  retiró por completo, ya no hace falta.
- 3 tests viejos (de la tarjeta preseleccionada de co-residentes, tickets previos a hoy) fallaron
  tras el fix porque asumían -- sin saberlo -- el bug ya corregido (contaban un `>Recibir<`/
  `name="accion"` que en realidad venía del par incondicional de "+ Nueva persona"); se
  actualizaron para reflejar el conteo real. 5 tests nuevos para las combinaciones bandera
  ON/OFF de `otra_unidad`/`conocido_sin_unidad`/`nuevo`.
- Suite completa `tests/web/test_announce_new.py`: 94/94 en verde tras la corrección.

# Pendientes del cliente — correcciones puntuales

No es una feature: es el registro de cada pedido suelto que el cliente hace
en vivo (retroalimentación sobre una vista ya desplegada, un ajuste chico de
texto/estilo/comportamiento) — el tipo de pedido demasiado pequeño para
justificar un spec formal vía `/to-spec`, pero que igual necesita quedar
escrito en algún lado para no depender de la memoria de la conversación.

Origen: el 2026-08-01 se descubrió que un pedido sobre `/anunciar`
(confirmación) — nombre y teléfono en mayúsculas y negrilla — nunca quedó
implementado ni registrado en ningún archivo del repo. No había manera de
saber que existía salvo que el cliente lo repitiera.

## Regla

Cada pedido del cliente, sin importar el tamaño, se registra ACÁ como un
issue (`issues/NN-<slug>.md`) ANTES de tocar código — mismo formato que usa
`to-tickets` en el resto del repo (ver `docs/agents/issue-tracker.md`), para
que sea compatible si más adelante se quiere correr `/triage` o `/to-tickets`
sobre esto.

`Status:` en cada issue:

- `pendiente` — registrado, todavía no implementado
- `implementado` — el código cambió, pero no se ha verificado en vivo
- `verificado` — confirmado en test.papyrus.com.co (o donde aplique) después
  del deploy; solo acá se considera realmente cerrado

Para trabajo grande (una vista nueva, un refactor) esto NO aplica — eso sigue
yendo por `/to-spec` → `/to-tickets`, que el cliente invoca directamente.

## Índice

- `01` — `/anunciar` confirmación: nombre y teléfono en mayúsculas y negrilla — **verificado**
- `02` — `/anunciar` confirmación: Apartamento con el mismo destacado — **verificado**
- `03` — `/anunciar` confirmación: subtítulo ampliado + nota de contacto bajo el código — **verificado**
- `04` — Autofocus en el primer campo de cada formulario al cargar la vista — **verificado**
- `05` — Unificar "Buscar" → "Consultar" en todo lo relacionado a paquetes — **verificado**
- `06` — `/anunciar` confirmación: espaciado de la nota, texto nuevo, y abreviar Torre/Apto — **verificado**
- `07` — `/consultar` resultado: ancho alineado con el formulario + campos distinguibles — **verificado**
- `08` — `/consultar` timeline: cada campo en su propia fila — **verificado**
- `09` — `/consultar`: verbo contextual, fecha resaltada, letra más grande, días desde recibido, sección superior separada, hora 12h — **verificado**
- `10` — `/consultar`: "Días desde recibido" como pill destacado, sin etiqueta — **verificado**
- `11` — `/consultar`: solo la línea de tiempo en mayúsculas (alcance corregido a mitad de tarea) — **verificado**
- `12` — `/consultar`: fotos dentro de "Recibido" + visor con zoom y navegación — **verificado**
- `13` — `/entrar`: indicador de pestaña activa — **verificado**
- `14` — Flujo OTP completo: restricción, latencia, casillas, redirects — **verificado**
- `15` — Recuperar contraseña de staff (correo) — **verificado**
- `16` — `/staff/olvide-password`: enlace de regreso tras enviar el correo — **verificado**
- `17` — `/entrar`: logo de Papyrus arriba del formulario — **verificado**
- `18` — `/entrar`: "Iniciar sesión" dentro de la tarjeta — **verificado**
- `19` — `/entrar`: pestaña "Soy del staff" → "Papyrus" — **verificado**
- `20` — `/entrar`: alineación vertical con /anunciar y /consultar — **verificado**
- `21` — `/staff/olvide-password` (+flujo): logo y alineación — **verificado**
- `22` — Logo + alineación en el resto de vistas públicas sin sesión — **verificado**
- `23` — Toast: texto de la notificación más grande — **verificado**
- `24` — `/ayuda`: contenido actualizado + ícono de producción — **verificado**
- `25` — `/ayuda`: rediseño de look and feel + enlaces reales — **verificado**
- `26` — `/privacy` + `/cookies` nuevas, más color en `/ayuda`, fix íconos Anunciar/WhatsApp — **verificado**
- `27` — `/ayuda`: réplica idéntica de producción — **verificado**
- `28` — `/terms`, `/privacy`, `/cookies`: réplica idéntica de producción — **verificado**
- `29` — Títulos de pestaña de las 3 vistas legales — **verificado**
- `30` — Rutas de las vistas legales en español (/terminos, /privacidad) — **verificado**
- `31` — Validación visible por campo en los 9 formularios de la app — **verificado**
- `32` — Mayúsculas consistentes en nombres/guías (guardar/modificar/buscar) + backfill — **verificado**
- `33` — Ícono de WhatsApp recortado en el footer (mobile y desktop) — **verificado**
- `34` — `/entrar`: redondear bordes superiores de las pestañas — **verificado**
- `35` — `/mis-datos`: teléfono editable en cualquier contacto — **verificado**
- `36` — `/mis-datos`: desactivar canales Llamada y WhatsApp — **verificado**
- `37` — Eliminar regionalismos (voseo) del texto de la app — **verificado**
- `38` — `/mis-datos`: error de "dar de baja" aparece al intentar otro cambio — **verificado**
- `39` — `/mis-datos`: reorganizar en pestañas (variante A del prototipo) — **verificado**
- `40` — `/mis-datos`: 9 ajustes de texto/copy — **verificado**
- `41` — `/announce` (staff) duplica Ocupantes si se reenvía — **verificado**
- `42` — `/mis-paquetes`: pestañas por estado + detalle expandible + código de acceso — **verificado**
- `43` — `/mis-paquetes`: quitar tab "Todos", color por estado, precio de entregados (bloqueado — falta que el cliente aclare el dato), alternativas de tarjeta — **pendiente**
- `44` — `/anunciar`: paquetes quedan "Sin apartamento" cuando el teléfono nunca fue vinculado, aunque el nombre coincida con un ocupante conocido (32TE, 64E3) — **formalizado en `.scratch/asociacion-retroactiva-apartamento/spec.md`**
- `45` — `tailwind.config.js` no escaneaba `src/app/web/templates/` (todo el rebuild sin compilar hace tiempo) — **implementado**
- `46` — `/mis-paquetes`: el código de acceso redirige a `/consultar?q=` en vez de copiar al portapapeles — **verificado**
- `47` — `/mis-paquetes`: color de tabs (ya en vivo), ubicación más natural (alternativas), identificar ocupante (bloqueado — alcance de datos) — **en diseño**
- `48` — `/mis-datos`: Torre/Apartamento de solo lectura, asignación exclusiva del staff desde `/residentes/{id}`, rediseño visual (edificio + marcador) — **implementado**
- `49` — `/entrar`: redirigir si ya hay sesión (otp→/mis-datos, staff→/paquetes); foco condicional (sin autofocus si hay error) aplicado a las 13 vistas del app que lo usaban — **implementado**
- `50` — `/anunciar`: límite de 10 anuncios activos por teléfono, con pantalla de confirmación desde el primero, sin mostrar códigos de acceso ajenos — **implementado**
- `51` — Failover de SMS/OTP: AWS SNS pasa al frente de la cadena (antes LIWA→Twilio→SNS, ahora SNS→LIWA→Twilio) por problemas puntuales con Twilio — **implementado**
- `52` — `/consultar`: foco condicional tras buscar (no reactiva teclado) + gestos táctiles reales (pinch zoom, pan, swipe, doble tap) en el visor de fotos — **implementado**
- `53` — `/consultar`: quitar las flechas del visor de fotos, navegación solo por swipe (+ teclado en escritorio) — **implementado**
- `54` — `/mis-datos`: quitar encabezado con avatar, tabs en grid 2x2 mobile, Notificaciones en tarjetas mobile, fix overflow del teléfono en Residentes — **implementado**

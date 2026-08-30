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
- `54` — `/mis-datos`: quitar encabezado con avatar, tabs en grid 2x2 mobile, Notificaciones en tarjetas mobile, fix overflow del teléfono en Residentes — **verificado**
- `55` — `/mis-datos` y `/mis-paquetes`: tabs mobile más grandes, mismo grid 2x2 en las 2 vistas — **verificado**
- `56` — `/mis-datos` y `/mis-paquetes`: resaltar cada tab en mobile con fondo + borde (solo mobile, desktop intacto) — **implementado** (desktop se rompió por cache de CSS, ver [[57]])
- `57` — Fix: tabs/Notificaciones "dañados" en desktop (CSS nunca recompilado en el deploy, no un bug de lógica) + Notificaciones a ancho completo en mobile — **verificado**
- `58` — `/mis-datos` y `/mis-paquetes`: tabs desktop más grandes y resaltados, misma posición — **implementado**
- `59` — Header: "Mis paquetes"/"Mis datos" en el menú de cuenta (mobile+desktop) + 4ta opción en el nav de escritorio — **verificado**
- `60` — `/mis-datos` y `/mis-paquetes`: unificar ancho/alineación del contenedor (mismas clases) — **verificado**
- `61` — Footer móvil de cliente logueado: Anunciar/Mis paquetes/Mis datos/Whatsapp (reemplaza Consultar/Ayuda) — **implementado**
- `62` — Menú de cuenta: agregar Consultar y Ayuda (debajo de Mis paquetes/Mis datos, arriba de Cerrar sesión) — **implementado**
- `63` — Índices faltantes en `paquetes`/`paquete_fotos` (auditoría de base de datos) — **implementado**
- `64` — Correo de recuperación de contraseña de staff: HTML profesional + remitente con nombre — **verificado**
- `65` — Correo de recuperación: ajustar remitente ("PaqueteX - Papyrus") y asunto ("...de PaqueteX") — **implementado** (cierra la sección de login)
- `66` — `/residentes`: tabla con todos los campos al cargar (paginada) + campo nuevo "Usuario de WhatsApp" — **implementado**
- `67` — `/residentes`: tabla simplificada (4 columnas + íconos WhatsApp/llamada) + ficha con tabs (Datos/Notificaciones/Apartamento y Residentes) — **implementado**
- `68` — `/residentes`: batch de 14 correcciones (picker Torre/Piso/Apto, tab Dirección, badges principal/auto-recepción, íconos a Acciones, etc.) — **implementado**
- `69` — `/residentes`: revisión punto por punto de [[68]] tras probar en vivo (fondo Secundario, aviso de reasignación bloqueada, Zona de peligro en un solo lugar, íconos en Acciones, bug de whatsapp_usuario que no se podía borrar, etc.) — **implementado, punto 14 pendiente**
- `70` — `/residentes`: quitar "Zona de peligro" de la ficha por completo (ya existe en la lista) + formato compacto "T 05 - APT 105"/"No Asignado" en la columna Torre y Apartamento de la lista — **implementado** (aviso de reasignación queda abierto, ver [[69]])
- `71` — `/residentes`: reemplazar el fondo rojizo completo de Residente Secundario por un acento de borde a la izquierda, más sutil (elegido entre 4 alternativas presentadas) — **implementado**
- `72` — `/paquetes`: quitar la línea "nombre · anunciar · sesión" del header (redundante con el menú de cuenta) — **implementado**
- `73` — `/paquetes`: tarjeta de filtros con look de producción — ancho completo, padding responsivo, íconos de Estado más vivos (círculo sólido + glifo en vez de pastel vacío) — **implementado**
- `74` — `/paquetes`: íconos de Estado no seleccionados se opacan cuando hay uno activo + esquinas cuadradas en vez de círculo — **implementado**
- `75` — `/paquetes`: botón "Agregar" (enlace a `/announce`) a la izquierda del grupo de íconos de Estado, mismo look and feel — **implementado**
- `76` — Ambiente local de desarrollo (`scripts/paquetex_dev_up.sh`/`_reset.sh`) para testing manual rápido + deploy a test.papyrus.com.co solo cuando se pida — **implementado**
- `77` — `/paquetes` y `/mis-paquetes` se sentían pesados al navegar: N+1 de consultas SQL por paquete, corregido con batch-resolución — **verificado**
- `78` — `/paquetes`: tabla en vez de tarjetas (5 alternativas evaluadas en vivo, ganó "Grid denso") — **implementado**
- `79` — `/paquetes`: renombrar columnas (Cliente/Dirección/Fecha) + columna Acciones ampliada a 8 íconos (Whatsapp/Teléfono/Email/Ver/Modificar/Acción/Cancelar/Eliminar) — **implementado**, ver [[78]]
- `80` — `/paquetes`: pulido del modal "Ver" (campos clicables/ocultos, sin etiquetas), Dirección en mayúsculas, ícono nuevo "Asignar apartamento" (solo Anunciado sin unidad), ícono "Ver" quitado de Acciones (redundante con columna Cliente) — **implementado**, ver [[79]]
- `81` — `/paquetes`: bug del ícono Email en Acciones (quedaba siempre apagado) corregido + código de acceso visible para staff (columna Cliente + modal Ver, confirmado explícitamente con el cliente que revierte una regla de privacidad previa) — **implementado**, ver [[80]]
- `82` — `/paquetes`: chip de código atenuado (2 rondas, amber-400→300→200), botón de estado en el modal "Ver" al doble de tamaño, e historial completo del paquete (todos los hitos, no solo el último) en ese mismo modal — **implementado**, ver [[81]]
- `83` — `/paquetes` modal "Ver": quita la sección "Anunciado por" (redundante con el Historial de [[82]]) + ícono de Email en "Residentes de la unidad" (solo si aplica, mismo criterio que WhatsApp/Teléfono) — **implementado**, ver [[82]]
- `84` — `/paquetes`: campo "Anuncio" en Destinatario (dónde llega la notificación), scroll de modales sin barra visible, advertencia de nombre clickeable (abre Corregir destinatario), `/anunciar` solo permite anunciar para co-residentes de la misma unidad, candidatos de corrección como tarjetas de un clic (3 variantes prototipadas en vivo) — **implementado**, ver [[83]]
- `85` — `/paquetes`: ícono "Nuevo residente" en Corregir destinatario + "Asignar apartamento" como campo de búsqueda de un clic (3 variantes prototipadas en vivo, ganó la búsqueda) — **implementado**, ver [[84]]
- `86` — `/paquetes` "Asignar apartamento": cada resultado de búsqueda muestra si la unidad está libre o ya tiene residentes (chip verde/naranja), para no asociar por error a la familia equivocada — **implementado**, ver [[85]]
- `87` — `/paquetes` "Asignar apartamento": bug de búsqueda (se vaciaba al escribir el número de apartamento tras la Torre) corregido con match por tokens + ahora también busca por nombre de residente, con la lista completa visible — **implementado**, ver [[86]]
- `88` — `/paquetes` "Asignar apartamento": el campo de búsqueda libre se reemplaza por un flujo guiado de 3 pasos (Apartamento → Torre → residentes/Libre + confirmar), tras 2 rondas fallidas del enfoque anterior — verificado con Playwright contra el navegador real antes de reportar; ajuste posterior: residentes como lista, no texto corrido — **implementado**, ver [[87]]
- `89` — `/paquetes` columna Acciones: ícono de Acción gris para Entregados (revierte, solo para ese estado, el "siempre colores" de [[79]]) — **implementado**, ver [[88]]
- `90` — `/paquetes` "Corregir destinatario": bug encontrado en prueba de humo — clickear el primer candidato fallaba (script anti doble-envío deshabilitaba el submitter antes de que el navegador armara el envío) — **implementado**, ver [[84]]
- `91` — `/paquetes` modal "Ver": título compuesto "Nombre - Código" (el chip de código ya no vive aparte) + botón de siguiente estado de 72px a 56px, para compactar la parte superior — **implementado**, ver [[90]]
- `92` — `clasificar_contacto` (campo único de `/announce`, contacto de residente nuevo en `/paquetes`/`/residentes`/verificación OTP) ahora acepta `"+57..."` y cualquier otro país con indicativo E.164, delegando en `normalizar_telefono` en vez de reimplementar la regla — **verificado**
- `93` — "Corregir destinatario" (advertencia de nombre no coincide) ampliado de solo ANUNCIADO a también RECIBIDO y ENTREGADO (`ESTADOS_CORREGIBLES`, ADR-0001 actualizada); CANCELADO sigue bloqueado — **verificado**
- `94` — Modal "Ver": teléfono de contacto movido a una línea justo debajo del título, se retira la sección "Destinatario" completa (redundante, Nombre ya está en el título) — **verificado**, ver [[91]]
- `95` — Modal "Ver": botón de siguiente estado de 56px a 48px, para compactar aún más el header — **verificado**, ver [[94]]
- `96` — Modal "Ver": botón "Corregir" al lado del de estado (solo si hay advertencia de nombre), se abre encima de Ver y al terminar regresa a reabrir Ver — **verificado**, ver [[95]]
- `97` — "+ Nuevo residente" respeta el nombre de una identidad ya registrada (enforcement en `agregar_ocupante`, cubre los 4 lugares que la llaman) + vista previa en vivo en Corregir destinatario — **verificado**
- `98` — "+ Nuevo residente": "Mudar residente a `<Torre/Apto>`" condicional al match (antes siempre visible), aviso + link a `/residentes` si es Principal, textos "Nombre correcto"/"Guardar" simplificados; bug de paso: `hidden`+`flex` nunca ocultaba de verdad (issue 97 incluido) — **implementado**
- `99` — "+ Nuevo residente": campo Nombre oculto hasta teclear el contacto (Contacto ahora va primero) -- aparece relleno/solo-lectura si existe, vacío/editable si no — **implementado**
- `100` — "+ Nuevo residente" se oculta (o hace swap a Asignar apartamento) si el paquete no tiene apartamento propio + aviso de Principal acortado con link directo a la tab Residentes (`?tab=`) + vista previa "Ya existe como X" simplificada — **implementado**
- `101` — "Promover a otro residente" sin salir de "Corregir destinatario" (modal encima, redirect con `?corregir=&recontactar=`) + `clasificar_contacto` acepta WhatsApp con o sin `@` inicial (mismo hueco que `+57` de issue 92) — **implementado**
- `102` — La advertencia de nombre se apaga con cualquier corrección explícita (antes solo si coincidía con el Anunciante) — **implementado**
- `103` — Ícono de WhatsApp en columna Acciones de `/paquetes` prioriza el username registrado sobre el teléfono (revisados todos los demás usos de link WhatsApp, ya estaban bien) — **implementado**
- `104` — Ícono de WhatsApp: fallback por nombre exacto cuando el destinatario no tiene teléfono en el snapshot (solo-WhatsApp, ejemplo real "CAMILA OSPINA") — **implementado**, ver [[103]]
- `105` — "Corregir destinatario" retira ENTREGADO de `ESTADOS_CORREGIBLES` (reversión parcial de issue 93, mismo día: el botón ya no debe verse en paquetes Entregados) — **implementado**
- `106` — Modal "Ver": teléfono+Torre/Apto en una sola línea con separador, chip de días transcurridos junto al badge de Estado (calendario, cuenta en curso si sigue abierto), sufijo "• Actual" quitado del historial — **implementado**
- `107` — Columna Cliente: código de acceso cliqueable → `/consultar?q=` (mismo patrón de [[46]]) + el chip de duración de [[106]] pasa de días-calendario a días+horas reales ("3 días y 4 horas") — **implementado**
- `108` — Chip de duración toma el color del badge de Estado de al lado (mismo rol/paleta, opción A entre 2 presentadas) — **implementado**
- `109` — Código de acceso de la columna Cliente (tabla) también con fondo redondeado y color por Estado (mismo tratamiento de [[108]], `estado_colores` compartido) — **implementado**
- `110` — Fuente Roboto en `/paquetes` (Google Fonts, solo esta vista, header/footer compartidos sin cambios) — **implementado**
- `111` — Modal "Cancelar": motivos en lista vertical, botón "Confirmar cancelación" → "Cancelar", se quita "Volver" (solo este modal, `modal_confirmacion` gana `mostrar_volver`), "Otro" revela input de texto libre — **implementado**
- `112` — Fuente definitiva de /paquetes: Nunito Sans (reemplaza Roboto de [[110]], elegida tras comparar 7 opciones en galería) — **implementado**
- `113` — Bug: íconos de Teléfono/WhatsApp en Acciones apagados sin fallback al anunciante cuando el destinatario no tiene contacto propio (ejemplo real "6Y5U") — **implementado**
- `114` — Picker de Apartamento (número→Torre) unificado entre "Asignar apartamento" y "Recibir" (nuevo macro compartido `picker_apartamento`, JS delegado en vez de repetido por fila) — **implementado**
- `115` — Modal "Recibir": quita el párrafo de apartamento y la etiqueta de Fotos, etiquetas "Apartamento"/"Guía" pasan a placeholder, cámara móvil habilitada para fotos, botón "Confirmar recibo" → "Recibir" — **implementado**
- `116` — "¿A nombre de quién es?" en Recibir solo se ofrece si el paquete ya tiene apartamento resuelto (elimina riesgo real de índice desalineado con el picker de Apartamento) — **implementado**
- `117` — "¿A nombre de quién es?" en Recibir: sin etiqueta, `<select>` reemplazado por tarjetas de un clic (2 por fila), badge "Actual" informativo sin pre-marcar radio (evita reactivar corregir_destinatario sin cambios reales) — **implementado**
- `118` — Tarjetas de candidato en Recibir: se quita el teléfono, "Actual" pasa de badge de texto a fondo de color (slate, distinto del azul de selección activa) — **implementado**
- `119` — Auditoría de unificación de /paquetes: botones "Entregar"/"Guardar" (verbo solo), "Confirmar guía" (sin "(opcional)"), fondo "Actual" también en Corregir destinatario, ícono de persona retirado ahí (Recibir manda la dirección "menos") — **implementado**
- `120` — Lista de /paquetes ordenada por último cambio de estado (no por fecha de anuncio) — el más reciente siempre primero — **verificado**
- `121` — Candidatos de Recibir/Corregir destinatario con badge Principal/Confirmado/Pendiente, mismo look de /residentes — **verificado**
- `122` — "+ Nuevo residente" de Recibir permite mover (mismo mecanismo de Corregir destinatario, checkbox mínimo) — **verificado**
- `123` — "+ Nuevo residente" de Recibir: vista previa en vivo completa portada de Corregir destinatario (bloqueo de nombre, "Mudar residente", "Degradarlo" con modal Promover ahora compartido) — **verificado**
- `124` — `/consultar`: botón "Entregar" visible solo para staff logueado, redirect de vuelta a `/consultar?q=`, reescaneo/confirmación de guía (mismo mecanismo que `/paquetes`), sin revelar la guía real cuando no coincide — **verificado**
- `125` — Modal "Recibir paquete": quita el badge de estado de ocupante de las tarjetas de candidato (solo Recibir, Corregir destinatario lo conserva) — **verificado**
- `126` — `/paquetes`: badges de conteo (Anunciado/Recibido) superpuestos en los íconos de filtro, rojos — **verificado**
- `127` — Recibir: aviso (no bloqueante) si la unidad declarada ya tiene residentes y el nombre no calza — **verificado**
- `128` — Recibir: lista de residentes de [[127]] como chips compactos (solo nombre), no oración con comas — **verificado**
- `129` — `/paquetes`: quitar la columna "Estado" de la tabla (el estado sigue visible vía el chip de código de acceso) — **verificado**
- `130` — Recibir: quitar el aviso ámbar "no está entre los residentes" de [[127]] — se queda solo la lista de chips — **verificado**
- `131` — `/announce`: quitar badges "Principal"/"Anunciante" de la lista de residentes (mismo criterio que [[125]]) — **verificado**
- `132` — `/announce`: fuente Nunito Sans (mismo que [[110]]/[[112]]) + código de acceso clickeable en el toast de éxito — **verificado**
- `133` — Recibir: capturar varias fotos con la cámara reemplazaba en vez de sumar (bug real, `capture="environment"` + `change` que reemplazaba en vez de acumular) — **implementado**
- `134` — `/consultar`: quitar el sufijo " • Actual" del badge de cada paso del timeline (mismo criterio ya aplicado en [[106]] al modal Ver) — **implementado**
- `135` — "Corregir destinatario": permitir asignar apartamento también en RECIBIDO (antes solo Anunciado), emoji 🏢/🏢❌ en la columna Dirección — **implementado**
- `136` — `/paquetes`: unificar tamaño de los íconos de Acciones (36×36px) con los de la barra de filtros — **implementado**
- `137` — Colores más intensos (mismo tono, un paso más oscuro) en íconos de Acciones de `/paquetes` y de Estado en la barra de filtros — **implementado**
- `138` — Reemplazar el literal "None" por "N/D" cuando un campo no tiene dato (solo front) — bug real encontrado en `/residentes`: teléfono en texto plano y enlace "Llamar" roto (`tel:None`) para Personas solo-WhatsApp — **implementado**
- `139` — Paginación: sticky arriba (desktop) + píldora flotante abajo (mobile) en `/paquetes` y `/residentes`, 6 bugs reales encontrados y corregidos en el camino — **implementado**
- `140` — `/paquetes`: 20 por página (revierte la decisión del 2026-08-13 que lo bajó a 10) — **implementado**
- `141` — Barra de búsqueda/filtros: título inline en desktop, sombra retirada, espacios optimizados, filtros redistribuidos en mobile — **implementado**
- `142` — `/paquetes`: búsqueda por email + teléfono parcial (últimos 4+ dígitos) — **implementado**
- `143` — Alinear ancho del contenido con el header en `/paquetes`, `/residentes`, `/administracion/personal` — **implementado**
- `144` — Letras grises más oscuras en todo el sistema (un escalón, contraste) — **implementado**
- `145` — `/residentes`: modales de confirmación (`modal_confirmacion`) en vez de `confirm()` nativo en "Rechazar/Eliminar" y "Convertir en principal", alineado con `/paquetes` — **implementado**
- `146` — Terminología "Clientes" → "Residentes" en `/residentes` y su nav (revierte rename explícito de Grupo 10/Ronda 2) — **implementado**
- `147` — `/residentes` tab Dirección: mismo picker de Apartamento (Apto→Torre, informativo no bloqueante) que `/paquetes`/`/announce`, elimina `apartamentos_ocupados()` — **implementado**
- `148` — "Recibir": declarar unidad nueva + registrar residente (¿A nombre de quién es?) en un solo envío, antes requería una segunda visita a "Corregir destinatario" — **implementado**
- `149` — "Asignar apartamento" (el otro punto de entrada, sin cubrir por [[148]]): también registra "+ Nuevo residente" opcional en el mismo envío — **implementado**
- `150` — Desactivar un staff corta su sesión ya abierta en el siguiente request, no solo su próximo login (`current_staff` releía `.activo`, faltaba) — **implementado**
- `151` — `/paquetes`: 🏢❌ → 🏠 apagado (`grayscale`+`opacity-50`) para "sin apartamento, no editable" — **verificado**
- `152` — `/consultar`: "Torre TORRE 10" duplicaba la palabra "Torre" (`snapshot_torre` ya trae el prefijo del catálogo) — mismo bug corregido en 4 lugares más, filtro `torre_sin_prefijo` centraliza el saneo (reusa [[79]]) — **verificado**
- `153` — `/paquetes` modal "Ver": nombre → `/residentes/<id>`, código → `/consultar?q=`, cada uno con su propio link — **verificado**
- `151` — `/paquetes`: 🏠 apagado (gris, `grayscale`+`opacity-50`) en vez del emoji compuesto "🏢❌" para "sin apartamento, no editable" — bug real en el camino: `text-slate-300` no apaga un emoji a color (solo un SVG con `fill="currentColor"`) — **implementado**
- `153` — `/paquetes` modal "Ver": nombre del título enlaza a `/residentes/<id>` (solo si hay Persona resuelta) y el código de acceso a `/consultar?q=`, cada uno como link independiente — **implementado**
- `154` — `/residentes` tab Residentes: "+ Agregar un nuevo Residente" gana la misma vista previa en vivo que ya tenía "+ Nuevo residente" en `/paquetes` (autocompleta/bloquea Nombre si el contacto ya existe, avisa conflicto de otra unidad) — lógica compartida extraída a `identificar_contacto_para_unidad` (`ocupante_service`) — **implementado**
- `155` — `/residentes`: espaciado de la tabla de resultados más compacto que en `/paquetes` — celdas `px-3 py-2` → `px-4 py-2.5` (mismo padding que `/paquetes`) — **implementado**
- `156` — `/residentes` columna Acciones: ícono 👫 (solo el emoji, sin texto/número) si el Residente comparte apartamento con al menos otro Ocupante activo — **implementado**
- `157` — `/residentes`: no era obvio cómo sumar un Residente ya existente a una unidad ocupada — mensaje "Ya tiene residentes" (tab Dirección) ahora enlaza directo a la ficha de quien ya vive ahí, + aviso en "+ Agregar un nuevo Residente" de que el campo Teléfono/WhatsApp también sirve para sumar a alguien con ficha propia — **implementado**
- `158` — `/residentes` tab Dirección: staff con control total — asignar/mover a un Residente a una unidad YA ocupada ya no se bloquea (revierte el ticket 13 de `.scratch/ocupante-principal-escenarios`); autoservicio del residente (`/mis-datos`) queda sin cambios, verificado que sigue intacto — **implementado**
- `159` — Mover a un Residente PRINCIPAL ya no se bloquea en seco (revierte el ticket 11 de `.scratch/ocupante-principal-escenarios`) — se degrada automáticamente a otro Residente de su unidad (el más antiguo con contacto propio) antes de moverlo, o se mueve directo si está solo; aplicado en los 4 puntos de entrada (tab Dirección/Residentes, /paquetes, /announce) — **implementado**
- `160` — `/residentes` columna Acciones: el ícono 👫 de [[156]] ahora enlaza a la tab Residentes de la ficha de ese Residente — **implementado**
- `161` — `/residentes` tab Dirección: asignar a una unidad vacía sigue confirmando y promoviendo a Principal automático; asignar a una unidad YA ocupada ahora queda PENDING (ya no se auto-confirma solo por ser staff) — el Principal (o cualquier staff) lo confirma después, o gana el primero en recibir un paquete si la unidad no tiene Principal (`promover_al_recibir`, ya existente) — **implementado**
- `162` — Usuario de WhatsApp se normaliza a minúscula (Meta no distingue mayúsculas de minúsculas) — 3 write/lookup sites en `persona_service.py` + backfill de datos existentes (migración `0029_whatsapp_usuario_minuscula`) — **verificado**
- `163` — `recipient_phone` de todo Paquete ahora siempre intenta "propio del destinatario, o si no el del Principal de su unidad" en los 4 caminos de `announce()` que no lo aplicaban (antes solo uno lo hacía) — **verificado**
- `164` — `/announce`: al identificar a un residente con paquetes ANUNCIADO/RECIBIDO ya en curso, se listan en viñetas con su código de acceso y un link para continuar el flujo (Recibir/Entregar) sin ir a `/paquetes` — nuevo query param `?entregar=` en `/paquetes` (mismo patrón que `?ver=`/`?recibir=`/`?corregir=`) — **verificado**
- `165` — `/paquetes`: ícono 🔄 (lista + modal Ver) si el destinatario dejó OTRA unidad hace menos de 30 días — explica direcciones distintas entre paquetes de la misma persona. `/announce`: píldoras de código más grandes (`text-sm`, igual que el resto de la app) y ahora SON el link de Recibir/Entregar directo, sin enlace de texto aparte — **verificado**
- `166` — Bug real reportado en vivo: un residente movido a una unidad que YA tuvo Principal antes (pero está vacía) nunca quedaba promovido — `hay_principal` (en `confirmar_ocupante` y `promover_al_recibir`) y el índice único de BD no filtraban `desvinculado_en IS NULL`, así que un Principal viejo ya desvinculado bloqueaba para siempre. Corregido en las 2 consultas + migración `0030_ocupante_principal_activo` (recrea el índice) — **verificado**
- `167` — Bug real, efecto secundario directo de [[166]]: `promover_a_principal` tenía el mismo filtro faltante — con el índice ya corregido para permitir historial, una unidad con 2+ Principales históricos (uno activo + viejos desvinculados) reventaba con `MultipleResultsFound` (500) al mover/promover a alguien nuevo — **verificado**
- `168` — `/residentes`: quitado el acento rojo a la izquierda de la fila para "Secundario" (issue 71) — confundía sin explicación visible de qué significaba — **verificado**
- `169` — `/residentes` tab Datos: staff ahora puede activar/desactivar "Autoriza recepción automática" (antes exclusivo de `/mis-datos`, staff solo veía el badge de solo lectura sin ningún control) — **verificado**
- `170` — Eliminado el campo `segundo_contacto` (`Persona`, `/residentes` tab Datos) — no era requerido en ningún flujo crítico, solo un término extra de búsqueda — **verificado**
- `171` — `/consultar`: botón "Recibir" para staff (paquete ANUNCIADO), mismo criterio que "Entregar" (RECIBIDO) — reusa el modal compartido `modal_recibir`, nuevos parámetros opcionales `origen`/`q` en su macro y en `receive_action` para redirigir de vuelta a `/consultar?q=...` — **verificado**
- `100` — `/paquetes` modal "Ver": Torre/Apto (junto al teléfono/WhatsApp) enlaza a la tab "Residentes del apartamento" de `/residentes` (solo si hay Persona resuelta) — mismo patrón `?tab=residentes` que [[160]] — **implementado**
- `101` — Bug real reportado en vivo: el link de identidad de `/paquetes` (título + Torre/Apto de [[100]]) confiaba en `recipient_phone` para resolver a qué ficha enlazar, pero issue 163 llena ese campo con el teléfono de OTRA Persona (el Principal de la unidad) cuando el destinatario no tiene teléfono propio — enlazaba a la ficha equivocada. Ahora solo confía en el teléfono si el nombre coincide; si no, cae por nombre — **implementado**
- `172` — `/residentes`: barra de búsqueda unificada con `/paquetes` (mismo macro `busqueda_filtros`, `mostrar_estado=False`, sin búsqueda en vivo) — **implementado**
- `173` — `/residentes`: búsqueda en vivo (autocompletado) — tabla se actualiza sola al escribir, mismo mecanismo fetch/debounce que [[172]] dejó afuera a propósito, ahora activado — **implementado**
- `174` — `/residentes`: botones "Listar principales" / "Agrupar por apartamento" (tarjetas por unidad, trae a TODOS los residentes de la unidad aunque la búsqueda solo matcheó a uno) / "Limpiar filtros" — siempre visibles, inactivos+grises los que no aplican; íconos cuadrados estilo Estado de `/paquetes` — **implementado**
- `175` — Bug real, mismo patrón que [[166]]/[[167]] en una consulta que ese barrido no cubrió: `_buscar_residentes` no filtraba `desvinculado_en IS NULL` al buscar por nombre de Ocupante — traía al Principal de una unidad donde la persona buscada ya NO vive (solo historial) — **implementado** (superado por [[176]])
- `176` — Seguimiento a [[175]]: se quita por completo el frente "nombre de Ocupante → Principal de su unidad" de `_buscar_residentes` — ahora que existe "Agrupar por apartamento" ([[174]]) para ver relacionados, la búsqueda por texto trae solo a quien matchea directo (nombre/teléfono propio o torre/apartamento) — **implementado**
- `177` — `_buscar_residentes` ahora acepta teléfono PARCIAL (no solo completo/exacto) — un fragmento de dígitos hace match parcial contra el teléfono canónico guardado — **implementado**
- `178` — `_buscar_residentes`: apartamento ahora se busca con el esquema `aptNNN` (match exacto, cualquier torre — ya no matchea unidades como "1302" al buscar "302"); nuevos frentes por WhatsApp y email — **implementado**
- `179` — `/residentes`: padding vertical del contenedor raíz unificado con `/paquetes` (`pt-6 pb-16 md:pb-6` → `pt-4 pb-16 md:pb-4`, arrastrado de antes de [[172]]) — **implementado**
- `180` — `/paquetes`: quitada la tipografía propia (Nunito Sans) — ahora hereda la misma fuente por defecto que `/residentes`/`/consultar`/el resto de la app — **implementado**
- `181` — Header con ancho inestable según haya o no scrollbar vertical (`/paquetes` dispara scroll más seguido que `/residentes` por tener más contenido) — `html { overflow-y: scroll; scrollbar-gutter: stable; }` en `base.html`, reserva el espacio siempre — **implementado**
- `182` — Auditoría completa de fuentes en toda la app: `/announce` tenía el mismo problema que tenía `/paquetes` (Nunito Sans, mismo origen — issue 131 copió el tratamiento de [[110]]/[[112]]) — quitado, mismo patrón que [[180]]. Confirmado que ninguna otra vista tiene fuente propia — **implementado**
- `183` — Auditoría de mayúsculas entre `/paquetes` y `/residentes`: nombres ya unificados server-side (`normalizar_nombre`), encabezados y badges ya consistentes — única diferencia real: columna Torre/Apartamento no forzaba `uppercase` por CSS en `/residentes` (sí en `/paquetes`) — agregado, mismo criterio explícito en las dos — **implementado**
- `184` — `/residentes`: columna Nombre `font-semibold` → `font-medium` (quitar negrilla), mismo peso que la columna equivalente de `/paquetes` — **implementado**
- `185` — `/residentes`: texto del placeholder de búsqueda actualizado ("Nombre, Teléfono, WhatsApp, Email, APT302") — **implementado**
- `186` — Bug real: "Asignar apartamento" sin "+ Nuevo residente" dejaba el paquete mostrando una unidad sin ningún Ocupante vinculado de verdad, sin avisar — ahora redirige a reabrir "Corregir destinatario" (con candidatos reales de esa unidad) en vez de a la lista sola — **implementado**
- `187` — Mismo bug que [[186]] duplicado en `receive_action` (declarar unidad DENTRO de "Recibir", no cubierto por ese fix) — mismo criterio aplicado ahí también — **implementado**
- `188` — [[186]]/[[187]] arreglaban el bug pero reabrir el modal solo no bastaba de señal (cliente lo siguió reportando con casos nuevos: FANTASMA 1 A7MA) — agregado un toast naranja persistente (sin auto-cierre, `?aviso=residente_pendiente`) que acompaña al modal reabierto explicando qué falta y qué hacer — **implementado**
- `189` — Auditoría completa de coherencia paquetes↔residentes, 5 rondas (el cliente lo siguió reportando tras cada una, hasta señalar explícitamente que rondas 1-3 solo escondían el problema en vez de resolverlo): rondas 1-3 corrigieron `corrected_at` compartido, la caja "Residentes de la unidad" sin gatear, los links de nombre/Torre-Apto sin gatear, y `Ocupante.nombre` sin resincronizar — ronda 4 (vía `/diagnosing-bugs`) fue el fix de fondo: "Recibir"/"Asignar apartamento" ya NO completan la recepción/asignación cuando la unidad tiene residentes reales y el destinatario no coincide con ninguno — ronda 5 (pedido explícito, flujo /announce "anunciar + recibir"): "para mí mismo" sin resolución explícita se autocompleta como residente nuevo usando la identidad ya conocida del Anunciante, en vez de bloquear — **implementado**
- `190` — `/administracion/notificaciones` (plantillas multicanal, `.scratch/plantillas-notificacion-multicanal`) ya era alcanzable vía el menú de cuenta pero no como tab visible — agregado a `.site-nav` de staff, gateado por `es_admin` (mismo cálculo que ya usaba el menú de cuenta) — **implementado**
- `191` — Email del admin sembrado por `scripts/paquetex_dev_up.sh` reemplazado de `admin@local.test` a `info@papyrus.com.co` — dato del ambiente LOCAL únicamente, la app no tiene ruta para editar email de staff — **implementado**
- `192` — `/administracion/personal`: "Dar de alta staff" pasa de formulario siempre visible a un botón "Agregar usuario" que abre un modal (mismo componente que ya usan Editar/Resetear ahí mismo) — reabre automáticamente con los campos marcados si la creación falla — **implementado**
- `193` — Quitada la palabra "staff" de los 9 textos realmente visibles (títulos, mensajes de error, etiquetas de menú) — identificadores internos/rutas/comentarios quedaron intactos a propósito, fuera del alcance del pedido — **implementado**
- `194` — "Personal" → "Perfiles" en el título/H1 de `/administracion/personal` y el enlace del menú de cuenta que apunta ahí (no son personal, son usuarios del sistema) — la etiqueta de grupo del dropdown ("Personal" = rol de quien está logueado, no la lista de cuentas) se dejó igual a propósito — **implementado**
- `195` — Quitado "Mi sesión" del menú de cuenta del header — `/mi-sesion` en sí (ruta/plantilla) se dejó intacta a propósito, es fixture de 5 archivos de test (~15 aserciones), no una feature de usuario — **implementado**
- `196` — Seguimiento a [[195]]: un OPERADOR se quedó sin ninguna entrada al menú de cuenta. "Mi sesión" vuelve como "Mi perfil" (visible para TODO staff, no solo ADMIN) y gana autoservicio real de contraseña (`POST /mi-sesion`, reutiliza `set_password` ya existente) — **implementado**
- `197` — "Mi perfil" rediseñada para alinearse al resto del sistema: título de página afuera de la tarjeta (como Perfiles/Notificaciones), avatar+badge de rol con los mismos colores de `admin/staff.html`, tarjetas de formulario vía `formulario_flujo` — **implementado**
- `198` — Autoservicio: cualquier staff edita su propio nombre (`editar_mi_perfil`, sin parámetro `rol` — ni existe la posibilidad de pasarlo) — **implementado**
- `199` — Quitada la tarjeta de identidad (avatar/nombre/email/rol/Cerrar sesión) de "Mi perfil" — redundante con el dropdown del header, que ya tenía su propio Cerrar sesión — **implementado**
- `200` — `/administracion/notificaciones`: layout de acordeón (`<details>` nativo) — elegido tras prototipar 3 alternativas en vivo (`?variant=a/b/d`) sobre la ruta real; el cliente pidió explícitamente ver algo visual, no más texto — **implementado**
- `201` — Bug real (`/diagnosing-bugs`): guardar cualquier plantilla tiraba 500 — migración 0034 se editó in-place después de ya haber corrido contra el Postgres local, dejando la tabla física con `creado_en` mientras el código esperaba `created_at`. Corregido hacia adelante con migración 0035 (condicional, segura en ambos escenarios) — **implementado**
- `202` — Acordeón de `/administracion/notificaciones` ahora exclusivo (1 abierto a la vez, `<details name="notif-acordeon">` nativo) + "Anunciado · Staff" eliminado (una sola plantilla ANUNCIADO, sin distinguir quién anunció — pedido explícito del cliente) — **implementado**
- `203` — `/administracion/notificaciones`: cada fila abre en modal, no acordeón — **implementado**
- `204` — `/administracion/notificaciones`: quitar vista previa de Email — **implementado**
- `205` — `/otp/perfil`: redirigir a `/mis-datos` — **implementado**
- `206` — `/mis-paquetes`: timeline acordeón exclusivo — **implementado**
- `207` — `/mis-paquetes`: píldora de "Código de acceso" visible antes de expandir — **implementado**
- `208` — `/mis-paquetes`: búsqueda por código de acceso o nombre del residente — **implementado**
- `209` — `/mis-datos`: cambiar texto de autorización — **implementado**
- `210` — `/mis-datos`: agregar enlace a términos y condiciones — **implementado**
- `211` — `/mis-datos` tab Datos: gestionar el WhatsApp propio — **implementado**
- `212` — `/mis-datos`: no se ve cómo crear un residente/ocupante — investigado, el formulario existe y funciona; queda **pendiente** confirmación del cliente de si el tab "Residentes" era visible en su caso
- `213` — Ocupante: permitir Teléfono Y WhatsApp simultáneos (cliente + staff) — diagnosticado como bug real de dominio, resuelto por las funciones `agregar_telefono_a_persona_de_ocupante`/`agregar_whatsapp_a_persona_de_ocupante` de [[217]]/[[233]] — **implementado**
- `214` — `/mis-datos` tab Notificaciones: quitar texto de restricción SMS — **implementado**
- `215` — `/mis-datos` tab Residentes: acortar texto de encabezado — **implementado**
- `216` — `/mis-datos` tab Residentes: acciones de fila más claras (chips ícono+palabra) — **implementado**
- `217` — `/mis-datos` tab Residentes: sugerir agregar el canal que falta (Teléfono/WhatsApp) — **implementado**
- `218` — `/mis-datos` tab Residentes: mejor visibilidad de quién es el principal — **implementado**
- `219` — `/mis-datos` tab Residentes: quitar el 🗑️ del botón Eliminar/Rechazar — **implementado**
- `220` — `/mis-datos`: modal de "Convertir en principal" igual al de `/residentes` — **implementado**
- `221` — `/mis-datos` tab Notificaciones: activar columna WhatsApp, a la derecha de SMS — **implementado**
- `222` — `/paquetes`: mensaje pre-cargado del botón WhatsApp + gate por preferencia — **implementado**
- `223` — `/residentes` tab Notificaciones: igualar a `/mis-datos` (WhatsApp activo, orden de columnas) — **implementado**
- `224` — `/residentes` tab Residentes: igualar a `/mis-datos` + navegar entre fichas por nombre (`?tab=residentes`, mismo mecanismo que [[100]]/[[172]]) — **implementado**
- `225` — `/residentes`: ancho de tabs unificado con `/mis-datos` + renombrar "⭐ Principal" a "⭐ Promover" — **implementado**
- `226` — `/mis-datos` tab Residentes: editar nombre/email y notificaciones por residente — **implementado**
- `227` — `/mis-datos` tab Residentes: unificar edición (Nombre/Email/Teléfono/WhatsApp) en un solo panel — **implementado**
- `228` — `/mis-datos` tab Residentes: "Editar" con un solo botón + acordeón exclusivo con Notificaciones — **implementado**
- `229` — `/mis-datos` tab Residentes: Editar/Notificaciones como modal + bug real de canal doble encontrado en vivo (arreglado a fondo en [[233]]) — **implementado**
- `230` — `/mis-datos` tab Residentes: modal de Notificaciones menos compacto — **implementado**
- `231` — `/mis-datos` y `/residentes`: alineación del modal de Notificaciones + textos de placeholders/badge — **implementado**
- `232` — Mobile: modales tapados por el `site-footer-mobile` fijo (z-index) — **implementado**
- `233` — Revisión de código de dos ejes (Standards + Spec) sobre toda la sección Residentes: bug real corregido (colisión de canal doble con Persona huérfana en `editar_telefono_ocupante`/`editar_whatsapp_ocupante`), 17 tests nuevos cubriendo lo que solo se probaba a mano, y 2 refactors de Standards (`badge_ocupante()` con `texto` opcional, nuevo macro `chip_accion()`) — **implementado**
- `234` — `/mis-datos`: botón y confirmación de autodescarte "Salir de este apartamento" → "Mudarse de este apartamento" — **implementado**
- `235` — `/mis-paquetes`: el alcance de TODA la unidad ([[57]] de `mis-paquetes-vista-apartamento`) pasa a ser exclusivo del Ocupante Principal — un no-Principal vuelve a ver solo lo propio (lista y conteos por pestaña) — **implementado**
- `236` — `/mis-datos`: "Quitar mi Teléfono" pasa de `<details>` inline a modal (`modal_confirmacion`) + texto nuevo del aviso y del checkbox — **implementado**
- `237` — `/mis-datos`: "Mudarse de este apartamento" pasa de `confirm()` nativo a modal (`modal_confirmacion`) — el único `confirm()` que quedaba en toda la sección Residentes — **implementado**
- `238` — `/mis-paquetes`: bug real reportado en vivo tras [[235]] — un no-Principal que anunció un paquete PARA otro residente de su unidad seguía viéndolo (por `announced_by_phone`); ahora "lo propio" para un no-Principal es estrictamente `recipient_phone` — **implementado**
- `239` — `/mis-paquetes`: la barra de búsqueda también recalcula el `· N` de cada tab (por estado, entre las tarjetas que calzan el término) — **implementado**
- `240` — `/mis-datos`: el modal "Mudarse de este apartamento" ([[237]]) nombra la Torre/Apartamento que se está dejando — **implementado**
- `241` — Seguimiento a [[240]]: "TORRE" pasa a texto fijo (filtro `torre_sin_prefijo` para no duplicar la palabra) en vez de interpolar el valor completo con "el " — **implementado**
- `242` — Botón "Volver" → "Regresar" en `modal_confirmacion` (afecta todos los modales de confirmación de la app, no solo Residentes) — **implementado**
- `243` — `/mis-paquetes`: código de acceso movido al lado derecho de Torre/Apto (`ml-auto`), antes vivía junto al nombre — **implementado**
- `244` — `/residentes/{id}`: título con el nombre del residente — **implementado** (superado por [[247]])
- `245` — `/residentes/{id}`: badge "✓ Recepción automática" → "Auto", unificado con la tabla — **implementado**
- `246` — `/residentes/{id}`: texto del checkbox de recepción automática acortado a "Recibir paquetes sin autorización" — **implementado**
- `247` — Seguimiento a [[244]]: el título deja solo el nombre, sin el prefijo "Ficha de residente - " — **implementado**
- `248` — `/residentes/{id}`: badge Principal/Secundario junto a "Auto", ahora siempre visible (antes solo Principal, issue 69) — **implementado** (parcialmente revertido por [[249]])
- `249` — Seguimiento a [[248]]: no mostrar badge "Secundario" -- vuelve al criterio de issue 69 (solo Principal), texto corto "Principal" se queda — **implementado**
- `250` — `/residentes/{id}`: quitado el acento rojo (`border-l-4 border-red-400`, issue 71) de las 4 tabs -- el badge "Principal" en la cabecera ya alcanza como señal, variable `es_secundario` eliminada por quedar sin uso — **implementado**
- `251` — `/residentes/{id}` tab Residentes: modal "Editar" unificado para Teléfono/WhatsApp (mismo patrón que [[227]]-[[229]] de `/mis-datos`), reemplaza los botones sueltos ✕/+ Teléfono/WhatsApp/Actualizar -- luego ampliado con Nombre/Email y un link de Notificaciones a la ficha propia — **implementado**
- `252` — `/residentes/{id}` tab Residentes: tanda de 7 ajustes (tab dice "Residentes" siempre, badge Principal solo "⭐" ~15% más grande, Editar/Notificaciones también para el Principal -- reposicionados junto al badge tras feedback en vivo --, resaltado de la ficha actual (texto "(ficha actual)" retirado luego, se queda solo el `ring`), textos "Agregar Residente"/"Residentes TORRE N APT M", texto de ayuda de issue 157 retirado) — **implementado**
- `253` — `/residentes/{id}` tab Residentes: la fila de cada tarjeta desbordaba en mobile (issue 252 le sumó hasta 4 chips al bloque de acciones sin que el nombre pudiera encoger) -- pasa a apilarse (`flex-col`) por debajo de `lg:`, `min-w-0`+`truncate` en el nombre — **implementado** (el apilado se revirtió después, ver [[255]])
- `254` — `/residentes/{id}` tab Residentes: chips de acción pasan a ícono/emoji solo (nuevo macro `chip_icono`, más contraste que `chip_accion`), Eliminar gana ícono ❌, badge de estado (⭐/Confirmado/Pendiente) pasa a estar en línea junto al nombre — **implementado**
- `255` — Seguimiento a [[254]]: "⭐ Promover" se une al resto de íconos, la fila vuelve a ser una sola línea (`flex-wrap`, ya no apilada como [[253]]), Eliminar se reordena al final — **implementado**
- `256` — Seguimiento a [[254]]: el badge de Principal en el roster vuelve a decir "Principal" (texto), en vez de solo "⭐" — **implementado**
- `257` — `/residentes/{id}`: modal "Convertir en residente principal" pasa de `variant='warning'` (naranja) a la nueva `variant='info'` (azul) en `modal_confirmacion` — **implementado**
- `258` — `/residentes/{id}` tab Residentes: `mt-1` entre el renglón nombre+badge y el teléfono, antes pegados — **implementado**

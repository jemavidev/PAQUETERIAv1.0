# 97 — "+ Nuevo residente" respeta el nombre de una identidad ya registrada

**Pedido original (cliente):**
"Veo que en el modal de 'Modificar' al tratar de agregar un nuevo
resiente, si el numero de telefono de este existe, la idea es que se
proponga usar los datos existentes, y no renombrar a lo que yo quiera, de
esa forma si un usuario es creado y confirmado deberian usarse esos datos
y no los nuevos que se indiquen, esto con el fin de unificar la
informacion, lo que si podria pasar es que si se quiere agregar ese mismo
numero de telefono con otro nombre, es necesario eliminar o desvincular
este usuario de los residentes actuales y despues poder agregarlo como
nuevo con el nombre que se requiera" -- confirmado el diagnóstico exacto
(el caso "activo en otra unidad" ya se manejaba bien; el hueco real era
"Persona existente pero no activa en ningún lado ahora mismo") y elegido
el tratamiento de UI: vista previa en vivo (no solo aviso silencioso).

**Status:** verificado

## Implementación

Dos partes, backend como enforcement real y frontend como vista previa:

- **`domain/ocupante_service.py::agregar_ocupante`** (enforcement real,
  cubre los 4 lugares que llaman a esta función: Corregir destinatario,
  `/announce` "nueva persona", `/residentes`, verificación OTP de
  cliente): si el contacto (Teléfono o WhatsApp) YA resuelve a una Persona
  registrada ANTES de esta llamada, el nombre que queda en el Ocupante es
  el YA REGISTRADO (`persona.nombre`), no el recién tecleado -- mismo
  principio que `mover_ocupante` (ticket 11) ya aplicaba para el caso de
  reubicarse de unidad, generalizado acá a cualquier alta que reutilice un
  contacto conocido, esté o no activo en este momento. Detectado vía
  `buscar_persona_por_telefono`/`buscar_persona_por_whatsapp` (lectura,
  sin crear) ANTES de `get_or_create_persona*`.
- **`packages/_resultados.html` + nuevo endpoint `GET /paquetes/nuevo-
  residente/identificar`** (vista previa en vivo, elegida sobre el aviso
  silencioso): mientras el staff teclea el contacto en "+ Nuevo
  residente" (dentro de "Corregir destinatario"), un fetch debounced
  (150ms, mismo patrón que `/announce/identificar`) consulta si ya existe
  -- si sí, completa el campo "Nombre" con el registrado, lo pone
  `readonly`, y muestra una nota explicando por qué + cómo usar otro
  nombre (desvincular primero). El endpoint devuelve JSON (no HTML): acá
  el JS necesita setear `.value`/`.readOnly` de un input, no reemplazar un
  fragmento.

## Verificación

- `tests/data_model/test_ocupante_service.py`: 4 tests nuevos (usa el
  nombre registrado con teléfono, con WhatsApp, contraparte sin Persona
  previa usa el tecleado, y el escenario completo del pedido -- desvincular
  y volver a dar de alta en otra unidad sigue respetando el nombre real).
- `tests/web/test_packages.py`: 4 tests nuevos para el endpoint de
  identificación (match por teléfono, por WhatsApp, sin match, requiere
  sesión) + 1 test de extremo a extremo confirmando que el POST real
  ignora un nombre distinto aunque venga en el payload.
- Playwright contra el servidor local real: capturada la vista previa
  completando el campo Nombre + volviéndolo readonly, y confirmado que
  aunque se fuerce el campo por JS (bypaseando el `readonly`) el servidor
  igual guarda el nombre real -- el enforcement no depende del JS del
  cliente.
- Suite completa: 936 pasan antes de sumar los tests nuevos de este
  issue (sin regresiones en ningún otro flujo que usa `agregar_ocupante`);
  ver commit para el conteo final con los tests nuevos incluidos.
- Desplegado a test.papyrus.com.co (2026-08-17), confirmado en el contenedor real (`docker exec paquetex-app-1`).

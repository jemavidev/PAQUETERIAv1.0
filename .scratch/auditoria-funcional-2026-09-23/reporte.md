# Auditoría funcional de PaqueteX (rebuild `CODE/src/app`) — 2026-09-23

**Alcance:** las ~120 rutas del rebuild, agrupadas por funcionalidad: acceso de staff y clientes, anuncio, recepción,
entrega y cobro, consulta pública, residentes/ocupantes, notificaciones, fotos, administración, despliegue.
**Método:** lectura del flujo real en el código, 14 comprobaciones de coherencia sobre la BD de desarrollo, pruebas
desechables contra la app real (TestClient + Postgres efímero, borradas al terminar) y lectura (sin cambios) de la
configuración de arranque de staging. **No cubre:** el monolito legado, equipos físicos (F7), datos de staging (la
lectura de su BD quedó bloqueada por permisos), carga/rendimiento, proveedores SMS/email reales, accesibilidad.

Cada hallazgo dice **qué pasa**, **cómo pasa**, la **evidencia** y qué hacer. "Reproducido" = lo vi pasar;
"por código/configuración" = se deduce con certeza de lo que está escrito, sin haberlo ejecutado.

---

## Resumen

| # | Severidad | Hallazgo | Evidencia |
|---|---|---|---|
| 1 | Crítica | El commit actual tiene la cadena de migraciones rota (`0055` depende de `0054`, que no está en git) | Reproducido (`git ls-tree`) |
| 2 | Alta | La cuenta de un residente (`/mis-datos`) se puede tomar adivinando el OTP de 2 dígitos | Reproducido |
| 3 | Alta | `/anunciar` es público y sin límite: permite mandar SMS a cualquier número (costo y acoso) | Por código |
| 4 | Alta | En staging el límite de intentos es GLOBAL (no por persona): 10 consultas/min para todo el conjunto, staff incluido | Por configuración |
| 5 | Alta | `/consultar` sin sesión muestra nombre, teléfono completo, apartamento, fotos y nombres del staff | Reproducido |
| 6 | Media | El SMS de "Anunciado" no queda registrado (estadísticas de SMS subcontadas); al arreglarlo, "Eliminar" daría 500 | Reproducido |
| 7 | Media | Las fotos verticales tomadas con el celular quedan guardadas acostadas | Reproducido |
| 8 | Media | El contador "N días" sigue creciendo en paquetes ya Entregados (`/consultar`, `/mis-paquetes`) | Reproducido |
| 9 | Media | Las sesiones no se pueden revocar (14 días; cambiar la contraseña no cierra las demás) | Por código |
| 10 | Baja | La exportación CSV de contactos externos rompe las tildes al abrirse en Excel | Por código |
| 11 | Baja | `/anunciar` revela si un teléfono ya es cliente con entregas | Por código |
| 12 | Baja | Fotos: se aceptan archivos que no son imagen y URLs sin validar (solo staff) | Por código |
| 13 | Observación | El SMS de "Recibido" viene apagado por defecto; el único que sale es el de "Anunciado" | Por código |
| 14 | Observación | Lector F7: solo escribe con el teclado en pantalla abierto (issue 376, sin resolver) | Probado por Jesús |

---

## Lo que está bien

- **Control de acceso.** Las ~120 rutas tienen el rol correcto: `require_admin` en toda `/administracion/*`, en
  eliminar paquete, eliminar residente y autorizar desbloqueo; `current_staff` en el resto de vistas de staff;
  `current_customer` en `/mis-datos` y `/mis-paquetes`. Desactivar a un usuario corta su acceso en el siguiente clic
  (`security.py` relee `activo` en cada request). Las 9 rutas de ocupantes de `/mis-datos` validan que quien opera sea
  el Principal de ESA unidad (`_ocupante_gestionable_por`): no hay acceso cruzado entre unidades.
- **Coherencia de datos (BD dev, 1.621 paquetes).** Las 14 comprobaciones dieron 0 casos: estados con sus fechas y
  actores, un cobro por cada entrega y ninguno en otros estados, total = base + bodegaje, anulado siempre con motivo,
  un solo Principal por unidad y toda unidad con ocupantes tiene uno, ninguna persona en dos unidades,
  `apartamento_actual` coherente con el ocupante activo, ningún snapshot de paquete abierto sin unidad resoluble
  (tras la migración 0057), ninguna unidad con más de 5 activos.
- **Cobro y bodegaje.** `calcular_cobro` es correcto y puro: base según tipo, exenta en primera entrega; 48 h de
  gracia y luego bloques de 24 h que nunca se exoneran; el cobro se recalcula en el servidor al confirmar y queda
  como snapshot (cambiar tarifas no reescribe cobros viejos).
- **Recuperación de contraseña del staff.** Token de 32 bytes, guardado como hash, con expiración y de un solo uso;
  la respuesta no revela si el correo existe.
- **Recepción.** Guía: el Enter del lector no recibe el paquete, más de 50 caracteres se rechaza con mensaje,
  aviso de guía repetida. Sin apartamento nunca se bloquea (377), renombrar el conjunto ya no descuadra los paquetes
  (378), primera entrega funciona para clientes solo-WhatsApp (379).
- **Pruebas.** En verde: dominio 833, web 1.200, navegador 76, infra 10.

---

## Hallazgos

### 1. Crítica — cadena de migraciones rota en el commit actual

**Qué pasa.** Cualquier checkout limpio de `PaqueteXv.2` (CI, o una sincronización al repo de despliegue) no
puede migrar la base: `alembic upgrade head` falla con "Can't locate revision `0054_fuentes_contactos_externos`", y
en staging el contenedor corre esa migración antes de arrancar uvicorn, así que la app no arrancaría.
**Cómo pasa.** `0055_registro_sms` (commit `f8a663e`) declara `down_revision = "0054_fuentes_contactos_externos"`,
pero `0054` solo existe sin versionar en el working tree, junto con el trabajo de "fuentes de contactos externos"
de otra sesión, también sin commitear (`contacto_externo.py`, `contacto_externo_service.py`, `admin.py`...).
`git ls-tree HEAD` muestra `0053`, `0055` y `0056`, sin `0054`. Las `0057`/`0058` de hoy también están sin commitear.
**Qué hacer.** Antes de cualquier despliegue, commitear `0054` junto con su código de modelo y pruebas, y después
`0057`/`0058` con lo de hoy. Verificar con un checkout limpio (worktree) que `alembic upgrade head` corra.

### 2. Alta — toma de cuenta de residente por OTP de 2 dígitos

**Qué pasa.** Alguien que sabe el teléfono de un residente puede entrar a su `/mis-datos` sin tener su celular.
Desde ahí ve sus datos y los de su unidad, gestiona ocupantes si es Principal y puede **eliminar la cuenta**
(anonimización).
**Cómo pasa.** El código es de 2 dígitos (100 combinaciones, decisión documentada en `otp_service.py`), con 5 intentos
por código, pero cada `/otp/solicitar` crea un código nuevo con otros 5 intentos y no hay tope por teléfono: 5 % de
acierto por solicitud. El único freno es el límite de 5 solicitudes/min.
**Evidencia.** Prueba desechable, atacante que nunca ve el código: entró en 27, 16, 10, 3 y 22 solicitudes (5 de 5
intentos); unos 3 minutos al límite actual. La víctima recibió 78 SMS en total.
**Qué hacer.** Subir a 6 dígitos, o poner un tope de códigos por teléfono por hora (p. ej. 3) con bloqueo temporal.
Lo ideal son las dos.

### 3. Alta — `/anunciar` permite mandar SMS a cualquier número

**Qué pasa.** Cualquiera, sin sesión, escribe un teléfono y un nombre y el sistema le manda un SMS a ese número,
pagado por PaqueteX, y crea una Persona con ese nombre.
**Cómo pasa.** `POST /anunciar` no tiene límite de intentos ni captcha. El SMS de "Anunciado" está activo por defecto
(`_default_activo`). El único tope es 10 paquetes anunciados activos por teléfono
(`MAX_ANUNCIADOS_ACTIVOS_POR_TELEFONO`): con muchos teléfonos distintos no hay límite. Un script puede llenar la BD de
Personas falsas y generar SMS a terceros.
**Qué hacer.** Límite por IP en `POST /anunciar` (tras arreglar el hallazgo 4), tope diario de SMS por teléfono
destino, y valorar un captcha liviano. Opcional: no mandar el SMS de anuncio a un teléfono que nunca tuvo un paquete
recibido.

### 4. Alta — en staging el límite de intentos es global

**Qué pasa.** El límite "por IP" cuenta a todo el mundo junto: 10 consultas/min a `/consultar` para TODO el conjunto,
incluido el staff que la usa para recibir y entregar; 10 intentos de login/min para todo el staff; 5 solicitudes de
OTP/min para todos los residentes. En hora pico el staff puede ver "Demasiados intentos" sin haber hecho nada raro.
**Cómo pasa.** `rate_limit.py` usa `request.client.host`. En staging uvicorn corre detrás de Caddy **sin
`--proxy-headers`** (lo dice el propio `docker-compose.yml` del servidor), así que esa IP es siempre la de Caddy.
Además, `/consultar` aplica el límite también con sesión de staff.
**Qué hacer.** Arrancar uvicorn con `--proxy-headers --forwarded-allow-ips` apuntando a Caddy, y exceptuar al staff
autenticado del límite de `/consultar`. **Ojo:** al arreglarlo, el límite pasa a ser por IP de verdad, y los
hallazgos 2 y 3 dejan de tener el "freno" global accidental. Conviene arreglar 2 y 3 antes o a la vez.

### 5. Alta — `/consultar` expone datos personales sin sesión

**Qué pasa.** Con el código de acceso o el número de guía (impreso en la etiqueta, a la vista del transportador y de
cualquiera que vea la caja), un visitante sin sesión ve: nombre completo, **teléfono completo**, conjunto, torre y
apartamento, las fotos del paquete, el historial con los nombres del staff que recibió o entregó, la guía y el cobro.
**Cómo pasa.** `search/form.html` pinta esos datos sin mirar la sesión: solo las acciones de staff están protegidas.
El código de acceso son 4 caracteres de 31 posibles (~923.000 combinaciones) y se consultan todos los paquetes,
incluido el historial: con ~1.600 paquetes, 1 de cada ~580 códigos al azar acierta. Las fotos son de S3
`public-read`, con URL permanente.
**Evidencia.** Prueba desechable: el teléfono aparece completo en `/consultar` sin sesión.
**Qué hacer.** Sin sesión: enmascarar el teléfono (`300 *** 4567`), mostrar solo torre sin apartamento (o nada),
ocultar los nombres del staff, y decidir si las fotos se muestran. Valorar no mostrar paquetes Entregados o Cancelados
de hace más de N días al público.

### 6. Media — el SMS de "Anunciado" no queda registrado (y, al arreglarlo, "Eliminar" daría error 500)

**Corregido el 2026-09-23** (la primera versión decía que "Eliminar" ya daba 500; hoy no pasa, por la razón de abajo).
**Qué pasa.** El SMS de un paquete recién anunciado sale, pero su registro en `registros_sms` se pierde en silencio:
el tablero de estadísticas de SMS (cantidades y costo) no cuenta los avisos de "Anunciado", que son justo los únicos
activos por defecto. Pasa en `/anunciar` y en el anuncio del staff (`/announce`).
**Cómo pasa.** Con FastAPI 0.104.1, el commit de la sesión del request (`get_db`) corre DESPUÉS de las tareas en
segundo plano. La tarea que envía el SMS intenta registrar el envío apuntando a un paquete que todavía no está
guardado: la llave foránea `fk_registros_sms_paquete` lo rechaza y `registrar_envio` se traga el error
(`except Exception: pass`). Recibir no tiene el problema porque `receive_action` hace commit explícito antes.
**Evidencia.** Reproducido por HTTP: `/anunciar` con un proveedor simulado que confirma el envío; el SMS sale, el
INSERT falla por la FK y `registros_sms` queda vacío. Borrar después ese paquete devuelve 303 (no falla), justamente
porque no hay registro.
**Qué hacer.** Commit explícito antes de programar la tarea en las dos rutas de anuncio. Al hacerlo, el borrado de un
Anunciado con su SMS registrado SÍ fallaría (reproducido a nivel de BD), así que en el mismo cambio hay que poner
`ON DELETE SET NULL` en esa FK. Agregar pruebas HTTP de las dos cosas.

### 7. Media — fotos verticales guardadas acostadas

**Qué pasa.** Una foto tomada con el celular en vertical se ve girada 90° en el modal y en `/consultar`.
**Cómo pasa.** El `<input capture="environment">` sube la foto tal cual sale de la cámara, que viene "acostada" con
una marca EXIF de orientación. `comprimir_imagen` (`imagen_service.py`) la redimensiona y recomprime sin aplicar esa
marca (no usa `ImageOps.exif_transpose`) y la marca se pierde.
**Evidencia.** Imagen de prueba 400×300 con EXIF "rotar 90°" (se ve 300×400): después de `comprimir_imagen` queda
400×300 y sin EXIF. No lo verifiqué con fotos reales de S3.
**Qué hacer.** `ImageOps.exif_transpose(imagen)` antes de `convert`. Es una línea, más una prueba.

### 8. Media — "N días" en paquetes ya entregados

**Qué pasa.** Un paquete entregado hace un año muestra "365 días" en `/consultar` y en `/mis-paquetes`, como si
siguiera en portería acumulando bodegaje.
**Cómo pasa.** `dias_desde_recibido` cuenta desde `received_at` hasta ahora sin mirar el estado, y las plantillas lo
muestran siempre que exista (en `/mis-paquetes` hay dos lugares: uno sí filtra por Recibido y el otro no).
**Evidencia.** Prueba desechable: un Entregado recibido hace 40 días muestra "40 días".
**Qué hacer.** Mostrarlo solo en Recibido, o para Entregado mostrar "estuvo N días" (recibido → entregado).

### 9. Media — sesiones no revocables

**Qué pasa.** Si a un operador le roban o comparten la sesión, o cambia su contraseña por sospecha, las demás
sesiones abiertas siguen valiendo hasta 14 días. "Cerrar sesión" solo cierra la del navegador actual.
**Cómo pasa.** Sesión en cookie firmada sin estado en el servidor (`SessionMiddleware` con valores por defecto:
14 días, `https_only=False`, así que la cookie no lleva `Secure`). No hay versión de sesión que invalidar. Solo
desactivar al usuario corta todo.
**Qué hacer.** Un contador `sesion_version` en `Usuario`, guardado en la sesión y comparado en `current_staff`, que
suba al cambiar o restablecer la contraseña. `https_only=True` y un `max_age` más corto para el staff.

### 10. Baja — CSV de contactos externos con tildes rotas en Excel

**Qué pasa / cómo.** `/administracion/contactos-externos/exportar` devuelve UTF-8 sin BOM ni `charset`. Excel en
Windows lo abre como ANSI y "JOSÉ" se ve "JOSÃ‰". Tampoco neutraliza celdas que empiezan con `=`, `+`, `-` o `@`
(riesgo bajo: solo lo usa el admin, con datos que el propio admin importó). No lo verifiqué en Excel.
**Qué hacer.** Anteponer `﻿` y `charset=utf-8`. Prefijar con `'` las celdas que empiecen por esos caracteres.

### 11. Baja — `/anunciar` revela si un teléfono ya es cliente

**Qué pasa / cómo.** Para un teléfono con entregas previas el formulario no pide nombre; para uno nuevo, sí. Probando
teléfonos se sabe cuáles son residentes activos. Es menor comparado con el hallazgo 5.

### 12. Baja — fotos: tipo de archivo y URLs sin validar

**Qué pasa / cómo.** Si el archivo no es una imagen, `comprimir_imagen` lo devuelve tal cual y se sube a S3
`public-read` con el tipo que diga la extensión (un `.html` quedaría servido como página en el dominio del bucket).
`fotos_urls` del formulario de Recibir se guarda sin verificar que apunte al bucket. No hay tope de tamaño antes de
leer el archivo a memoria. Todo requiere sesión de staff: riesgo bajo.
**Qué hacer.** Rechazar lo que Pillow no abra, validar que la URL sea del bucket y poner un tope de tamaño.

### 13. Observación — qué SMS salen por defecto

Desde el 2026-08-10 (pedido del cliente, por costo), el único SMS activo por defecto es el de **Anunciado**.
Recibido, Entregado y Cancelado vienen apagados hasta que la persona los active. En la práctica el aviso más útil
("tu paquete llegó") no sale, y el que sí sale suele confirmarle al residente algo que él mismo acaba de hacer. Es
decisión de negocio, no un defecto; vale la pena revisarla con el cliente, sobre todo junto con el hallazgo 3.

Relacionado: cuando al recibir se registra un "Nuevo residente" sin apartamento con un teléfono que no es de ninguna
Persona (issue 377), el aviso cae al Anunciante, no a ese teléfono.

### 14. Observación — lector F7

Con el modo lector activo el campo queda enfocado, pero el gatillo del F7 no escribe hasta que se abre el teclado en
pantalla: el F7 inyecta el texto por la conexión del teclado. Abrirlo desde código (VirtualKeyboard API, issue 376)
no funcionó en el equipo. Queda por el lado del equipo: buscar un modo de salida "simular teclas" en Scanning
Settings, o la opción de Android "mostrar teclado virtual con el teclado físico". El código de ese intento sigue sin
commitear y conviene revertirlo.

Límite conocido de primera entrega (sin cambios, issue 314): un residente solo-WhatsApp cuyo paquete tomó el teléfono
del Principal de su unidad se juzga por el teléfono del Principal.

---

## Orden sugerido

1. **Antes de desplegar nada:** hallazgo 1 (commitear `0054` con su código; luego `0057`/`0058`).
2. **Seguridad de clientes, juntos:** 2 (OTP), 3 (`/anunciar`) y 4 (`--proxy-headers`), en ese orden o en un
   mismo despliegue.
3. **Privacidad:** 5 (`/consultar` público). Pide decisiones del cliente sobre qué se muestra.
4. **Defectos rápidos, una línea o poco más cada uno:** 7 (EXIF), 8 (días), 6 (commit antes del SMS + FK), 10 (BOM).
5. **Endurecimiento:** 9 (sesiones), 11, 12.
6. **Con el cliente:** 13 (SMS por defecto) y 14 (configuración del F7).

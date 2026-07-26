# Referencia funcional — PAQUETEX (PaqueteXv.2)

> Documento de trabajo, no la guía de usuario final. Describe **cada pantalla tal como existe hoy en el código** — campos, botones, validaciones, reglas — para servir de base a los ajustes que vamos a ir haciendo. Cada sección termina con un bloque **Notas de ajustes** para anotar lo que se decida cambiar ahí.
>
> Fuente: código en `CODE/src/app/domain/` y `CODE/src/app/web/` al 2026-07-26. Si el código cambia, este documento se desactualiza — no es autogenerado.

---

## Índice

0. [Aspectos transversales](#0-aspectos-transversales)
1. [Cliente — Anunciar paquete (`/anunciar`)](#1-cliente--anunciar-paquete-anunciar)
2. [Cliente — Consultar paquete (`/consultar`)](#2-cliente--consultar-paquete-consultar)
3. [Cliente — Verificación por teléfono (`/otp*`)](#3-cliente--verificación-por-teléfono-otp)
4. [Cliente — Mis datos (`/mis-datos`)](#4-cliente--mis-datos-mis-datos)
5. [Staff — Ingresar / sesión (`/ingresar`, `/salir`, `/mi-sesion`)](#5-staff--ingresar--sesión-ingresar-salir-mi-sesion)
6. [Staff — Paquetes (`/paquetes`)](#6-staff--paquetes-paquetes)
7. [Staff — Declarar unidad (`/announce`)](#7-staff--declarar-unidad-announce)
8. [Staff — Residentes (`/residentes`)](#8-staff--residentes-residentes)
9. [Staff — Administración de personal (`/administracion/personal`)](#9-staff--administración-de-personal-administracionpersonal)
10. [Notificaciones (transversal)](#10-notificaciones-transversal)
11. [Autenticación y sesiones (transversal)](#11-autenticación-y-sesiones-transversal)

---

## 0. Aspectos transversales

Cosas que aplican a **toda** la app, no a una pantalla en particular.

- **Sin navegación compartida.** `base.html` no tiene header, menú ni footer — cada pantalla es una isla. No hay forma de ir de `/paquetes` a `/residentes` sin escribir la URL a mano, salvo el único link "sesión" que hay en `/paquetes` hacia `/mi-sesion`. Ninguna otra pantalla de staff enlaza a otra.
- **Dos sesiones independientes en la misma cookie.** `usuario_id` (staff) y `persona_id` (cliente) conviven sin pisarse — cerrar una nunca cierra la otra (`session.pop`, nunca `session.clear`).
- **Teléfono, normalización canónica (Colombia por defecto).** Cualquier formato de entrada (`"300 123 4567"`, `"(300) 123-4567"`, `"+57 300 1234567"`, etc.) se reduce a solo dígitos y se guarda como `+57` + 10 dígitos. Un teléfono sin ningún dígito es un error de validación.
- **Auth siempre activa, también en lectura** — no hay pantallas de staff "públicas de solo ver".
- **Mensajes de error genéricos en login** (staff y cliente): nunca revelan si el email/teléfono existe o no.
- **Anti doble-envío repetido en cada formulario con JS**: al enviar, el botón se deshabilita y se rehabilita a los 5000ms pase lo que pase (`try/finally`) — patrón idéntico en `/anunciar` (no, ese no tiene JS), `/otp` (ambos pasos), `/mis-datos`, `/announce`, y los 3 modales de `/paquetes`. **Nota:** el timeout es fijo en 5s independientemente de si la respuesta ya volvió antes — no vuelve a habilitar el botón al recibir respuesta, solo por el timer.
- **Rate limiting — solo 2 rutas lo tienen:** login de staff (`/ingresar`, 10 intentos/60s) y solicitud de OTP (`/otp/solicitar`, 5 intentos/60s), ambos por IP. El resto de rutas (`/anunciar`, `/consultar`, `/mis-datos`, búsqueda en `/residentes`, etc.) **no tiene ningún límite**. El limitador es en memoria del proceso (`app.state`): se resetea al reiniciar el servidor, y si algún día se corre con más de un worker, cada worker cuenta aparte (subestima el total real). Es *fail-open*: si el limitador falla internamente, deja pasar la solicitud.
- **`/health`** — sin auth, devuelve `{"status": "ok"}`. Solo confirma que el proceso responde, no valida la conexión a la base de datos.

### Notas de ajustes
- Teléfono, normalización canónica: No me confirmaste si admite cualquier otro telefono que no sea de colombia (ejemplo: +13002596319, +583002596319, +913002596319, ...)
- Sin navegación compartida: Seria bueno que desde ya tengas el header y footer como te lo pedi anteriormente, esto ya que tambien son un punto para probar, necesito que los implementes y les realizaremos los test manuales mas adelante.
- PS (Por lo que pude ver, no se tiene ningun tipo de look and feel hasta el momento, el que tiene es bastante basico, mas adelante trabajaremos en un look and feel orientado a UX, tanto para staff como para clientes)

---

## 1. Cliente — Anunciar paquete (`/anunciar`)

**Sin sesión, sin login.** `GET` muestra el formulario; `POST` a la misma ruta lo procesa.

**Campos:**
- `nombre` (texto, obligatorio) — nombre de quien anuncia.
- `telefono` (tel, obligatorio) — teléfono de quien anuncia.
- `a_nombre_de` (radio, 3 opciones, obligatorio, default "A mi nombre"):
  - **A mi nombre** — el destinatario es el propio anunciante.
  - **Otra persona registrada** — pide `destinatario_telefono`; falla con *"Ese teléfono no está registrado; usa la opción 'Solo un nombre'"* si esa Persona no existe todavía.
  - **Solo un nombre** — pide `destinatario_nombre`; no crea una Persona, el nombre queda solo dentro del snapshot de este Paquete.
- `acepta_tyc` (checkbox, obligatorio) — sin enlace real a un texto de Términos y Condiciones en esta pantalla (no hay link a `/terms`).

**Qué pasa al enviar (todo o nada):**
1. Se busca o crea la Persona del **anunciante** por su teléfono (`get_or_create_persona`) — así es como un residente nuevo entra al sistema por primera vez.
2. Se resuelve el destinatario según la opción elegida.
3. Se congela el snapshot de apartamento: si el destinatario es una Persona registrada, usa **su** apartamento actual; si no, usa el del **anunciante**. Si ninguno tiene apartamento asignado, el paquete queda "sin apartamento" (así se ve luego en `/paquetes`).
4. Se genera `tracking_number` y `access_code`, el Paquete nace en estado `ANUNCIADO`.
5. Éxito → pantalla de confirmación con nombre del destinatario, número de seguimiento y código de acceso. Link único: "Anunciar otro paquete" (vuelve a `/anunciar`, formulario vacío).

**No captura:** número de guía del transportador (eso lo hace el staff al recibir).

### Notas de ajustes
* Para los clientes, seria necesario que solo coloquen el nombre, el numero de telefono y aceptar los terminos y condiciones, mas adelante en este mismo documento, describire como se realizara la asociacion entre el nombre y el telefono, pero solo lo podra hacer un staff, no el cliente, este solo ingresa Nombre y Numero. La idea es que para el cliente sea transparente el anunciar un paquete, ya sea a su nombre o a nombre de un tercero y para el personal de staff si sea posible poder asociar Nombre (nombre), Telefono (telefono) y Tercero (a_nombre_de), todo esto basado en que exista o no el cliente.
* Aclarando la opcion de "a_nombre_de" solo a la vista del staff, se enfoca en que el cliente anuncia un paquete teniendo coo base su numero de telefono y colocando cualquier nombre (propio o de un tercero), seguido a esto se realizara el anuncio. Despues este anuncio lo vera el personal de staff el cual es quien decide finalmente "a_nombre_de" se anuncia el paquete, esto ya que el cliente solo intenta anunciar, pero el staff es quien podra crear este tercero o asociar a un tercero existente, todo esto teniendo como base el numero de telefono que realiza el anuncio (exista o no este numero de telefono).
* En esta vista del cliente nunca se revelara informacion de telefono asociada a un nombre, solo se ingresan los datos y se crea el "access_code", en general se ANUNCIA el paquete.
* Para la creacion del "access_code", debes tener presente esto, el codigo es de 4 caracteres, donde se debe omitir para evitar confuciones en el manejo de los codigos los números **0 y 1** y las letras **O, I, L**, adicional los casos en que se contenga la secuencia **"666"** (ya sea al inicio o al final).
* El "tracking_number" se crea vacio en esta vista y esta enfocado a poder ingresar el nuero de guia del transportados al momento de recibir el paquete, este paso lo realizara el personal de staff al momento de recibir el paquete fisico.
* El caso de exito debera ser una pantalla que contenga Nombre (nombre), numero de telefono (telefono), el codigo de acceso (access_code), la torre y el apartamento, y enlaces para consultar dicho codigo, actualizar los datos personales.
* No se si al hablar de "access_code" y "tracking_number" nos referimos a lo mismo que planteo en estas notas o tu tienes un entendimiendo de estos diferentes?

---

## 2. Cliente — Consultar paquete (`/consultar`)

**Sin sesión.** Un solo campo de búsqueda `q`, por `GET`.

**Lógica de búsqueda (en este orden):**

1. Si `q` coincide **exactamente** con un `tracking_number` → muestra la ficha completa de ese Paquete: nombre del destinatario, estado, apartamento (o "Sin apartamento"), y una **línea de tiempo** (Anunciado/Recibido/Entregado/Cancelado con fecha y, si aplica, motivo de cancelación). No se muestra qué miembro del staff hizo cada acción.
2. Si no coincide con ningún tracking, se interpreta `q` como **teléfono** (normalizado) y se buscan **todos** los paquetes donde ese teléfono sea el anunciante o el destinatario, ordenados del más reciente al más antiguo.
3. Si tampoco hay resultados → "No encontramos ningún paquete con ese dato."

**Limitación notable:** cuando la búsqueda por teléfono devuelve varios paquetes, cada tarjeta solo muestra nombre + estado + número de seguimiento — **no es clickeable**, no lleva a la línea de tiempo de ese paquete en particular. Para ver el detalle hay que volver a buscar por ese `tracking_number` exacto.

### Notas de ajustes
* Las consultas se podran hacer por "access_code" o "tracking_number", el access_code siempre debe existir si fue creado al anunciar un paquete, mientras que el tracking_number solo se podra crear o no al recibir un paquete fisico.
* Si la consulta ex existosa, se mostrara el historial completo de ese paquete, incluyendo (CLIENTE, TELÉFONO, GUIA (tracking_number), ESTADO ACTUAL, LINEA DE TIEMPO (DATOS DEL PAQUETE ANUNCIADO, RECIBIDO, ENTREGADO O CANCELADO) en forma de historial con sus datos relevantes (FECHAS, HORAS, CONDICIONES, TIPO DE PAQUETE, IMAGENES)) siempre y cuando esta informacion exista del paquete, en cada accion se debe mostrar el miembro del staff hizo cada acción (recibir, entregar y cancelar).
* Seria bueno mostrar entre los datos del cliente la torre y el aprtamento, en caso que estos no existan, seria bueno tener un enlace que permita al cliente actualizar sus datos, podiendo asi agregar los datos que requiera.
* SOLAMENTE se puede consultar por access_code o tracking_number (si existe) ,nunca se podra en esta vista consultar por otro campo deferente a estos.
* NUNCA se podra realizar la búsqueda por teléfono en esta vista, esto es todo por seguridad, en el contexto se aclara que casa access_code se crea solo al momento de anunciar un paquete y solamente quien anuncia es quien conocera este codigo.

---

## 3. Cliente — Verificación por teléfono (`/otp*`)

Cuatro rutas relacionadas + una quinta que es en la práctica redundante con la sección 4.

| Ruta | Método | Qué hace |
|---|---|---|
| `/otp` | GET | Formulario: un solo campo teléfono. |
| `/otp/solicitar` | POST | Genera un código de 6 dígitos, se lo entrega al `OtpSender` (hoy: `DevOtpSender`, **no manda SMS real** — el código solo existe en memoria del proceso). Rate limit 5/60s por IP. |
| `/otp/verificar` | POST | Verifica teléfono + código de 6 dígitos. Éxito → abre sesión de cliente → redirige a `/otp/perfil`. Error → "Código inválido o expirado" (genérico, no distingue código malo de expirado). |
| `/otp/salir` | POST | Cierra solo la sesión de cliente. |
| `/otp/perfil` | GET | Página protegida mínima: teléfono + nombre + botón "Cerrar sesión". **Es, literalmente, una "ruta de prueba"** según su propio comentario en el código (`customer_auth.py`) — quedó de cuando aún no existía `/mis-datos`. |

**Punto a decidir:** tras verificar el código, el cliente cae en `/otp/perfil` (la pantalla mínima), **no** en `/mis-datos` (la pantalla completa de edición). Hoy no hay ningún link de una hacia la otra — son dos pantallas de "sesión de cliente" desconectadas entre sí.

### Notas de ajustes
* El "/otp/solicitar" sera un codigo generado de 2 digitos numericos, asociado al numero de telefono que lo solicite, este sera temporal, con una vida de 5 minutos, este numero solo sera posible utilizarlos durante ese tiempo, este sera enviado por SMS al cliente que lo solicite.
*  El "/otp/verificar" verificara el codigo generado en "/otp/solicitar", con todas sus carantes descritas.
* La opcion de "/otp/perfil" debera poder hacer CRUD a la mayoria de datos del cliente, incluyendo los numeros y otros clientes asociados a el.
* No entiendo diferencia entre "/otp/perfil" y "/mis-datos", la idea es que el cliente pueda editar sus datos, la idea es que si el cliente tiene exito al verificar el OTP que recibio por SMS, este deberia ser gido a "/mis-datos" con el fin de editar lo que crea comveniente.

---

## 4. Cliente — Mis datos (`/mis-datos`)

**Requiere sesión de cliente** (verificada por OTP). Si no hay sesión, cualquier intento de entrar redirige automáticamente a `/otp`.

**Sección "Datos personales":**
- `nombre`, `email`, `tipo_documento`, `documento`, `segundo_contacto` — todos opcionales, actualización parcial (un campo vacío en el formulario significa "no cambiar" excepto que aquí, al ser un form completo pre-rellenado, vacío sí borra el valor visualmente... en la práctica el usuario siempre ve y reenvía todos los campos).
- Único campo validado: `email` debe tener forma de email si se envía; si es inválido, **se descarta todo el request** (rollback completo, ningún campo se guarda) y se re-muestra el formulario con el error.
- Checkbox **"Recibir notificaciones por SMS"** — a diferencia del resto de campos, su ausencia en el POST sí significa algo explícito (desmarcado = `False`), nunca "no tocar".

**Sección "Mi apartamento":**
- `conjunto`, `torre`, `apartamento` — los tres vacíos (no toca el apartamento actual) o los tres llenos (declara/actualiza su apartamento). Si se llena solo alguno, error: *"Completa Conjunto, Torre y Apartamento, o deja los tres vacíos."*
- Declarar aquí **une al cliente a esa unidad** como único miembro de este acto — si ya hay otros residentes en ese apartamento, se mantienen como están (no los desvincula ni los reasigna).

**Guardado:** un único botón "Guardar", redirige a `/mis-datos?guardado=1` (mensaje de éxito visible tras el redirect).

### Notas de ajustes
* Con relacion al "segundo_contacto", pueden existir varios "segundo_contacto", este estara siempre asociado al apartamento y al numero de telefono principal.
* Para el "segundo_contacto" debe existor la posibilidad de tener asociado un numero de telefono de este segundo contacto, esto debe ser posible para cada segundo contacto que exista, la idea de esto es que si llega un paquete a nombre de un "segundo_contacto" que podamos identificar por el numero de telefono de este, sera posible anunciar el paquete para este segundo_contacto y notificar al segundo contacto por medio de su numero.
* Los "segundo_contacto" podran tambien solicitar OTP para cambiar los datos que le pertenecen solo a ellos, no de la cuenta asociada al numero principal.
* En esta misma vista se podran editar las preferencias de noticiacion actuales o futuras.
* Esta vista permitira de igual forma se podra dar de baja a un cliente, o tambien desasociar un "segundo_contacto".

---

## 5. Staff — Ingresar / sesión (`/ingresar`, `/salir`, `/mi-sesion`)

**`/ingresar`** (GET/POST): `email` + `password`. Rate limit 10 intentos/60s por IP → 429 con *"Demasiados intentos..."*. Credenciales inválidas → *"Email o contraseña incorrectos"* (no distingue cuál de los dos falló). Éxito → sesión de staff → redirige a `/mi-sesion`.

**`/mi-sesion`** (GET, protegida): muestra nombre, email y rol (`ADMIN`/`OPERADOR`) del staff en sesión. Único botón: "Cerrar sesión" → POST a `/salir`. Es también la **única pantalla de toda la app con un link de salida hacia otra pantalla de staff** (el "· sesión" que aparece arriba en `/paquetes` apunta aquí).

**`/salir`** (POST): cierra solo la sesión de staff (no la de cliente si coexiste) → redirige a `/ingresar`.

### Notas de ajustes
* Se ve todo bien.

---

## 6. Staff — Paquetes (`/paquetes`)

**La pantalla principal del staff.** Requiere sesión de staff (cualquier rol).

**La lista:**
- Todos los paquetes, **sin filtro y sin paginación**, ordenados del más recientemente anunciado al más antiguo. Con muchos paquetes esto será una lista larga sin forma de acotarla (no hay buscador aquí, ni por estado, ni por nombre, ni por fecha).
- Cada tarjeta: nombre del destinatario, badge de estado (Anunciado azul / Recibido amarillo / Entregado verde / Cancelado gris), y apartamento (o "Sin apartamento").
- Vacío → "No hay paquetes."

**Acciones, condicionadas al estado exacto (máquina de estados):**

```
ANUNCIADO ──Recibir──▶ RECIBIDO ──Entregar──▶ ENTREGADO   (terminal)
    └──────────Cancelar─────────┴────Cancelar────▶ CANCELADO (terminal)
```

- Toda transición **valida antes de mutar**: si se rechaza, el paquete queda exactamente igual (ni estado ni fechas cambian) y la lista se re-muestra con un aviso, sin tocar nada.
- `ENTREGADO` y `CANCELADO` son terminales — ninguna acción posterior es posible desde ahí (ya no aparecen botones).
- Cada transición registra **quién** (el `Usuario` de la sesión real) y **cuándo** — nunca queda anónima.

**Modal "Recibir"** (solo si `ANUNCIADO`):
- Campo `guide_number` (texto, **opcional**).
- Botón "📷 Escanear con cámara": pide permiso de cámara, carga el bundle ZXing de forma perezosa (`/static/vendor/zxing.min.js`), decodifica multi-formato y rellena el campo de guía automáticamente. Si la cámara no está disponible o falla, muestra un mensaje y el campo queda disponible para escribir a mano — nunca bloquea el flujo.
- Confirmar → `RECIBIDO`, dispara notificación (ver §10).

**Modal "Entregar"** (solo si `RECIBIDO`):
- Sin campos — solo confirma. Muestra a quién se entrega y su apartamento (si tiene) como recordatorio visual.
- Confirmar → `ENTREGADO`, dispara notificación.

**Modal "Cancelar"** (si `ANUNCIADO` o `RECIBIDO`):
- Campo `motivo` (select, **obligatorio**): `ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`. Sin motivo → error, el paquete queda intacto.
- Advertencia visual: "Esta acción es irreversible."
- Confirmar → `CANCELADO`, dispara notificación.

**Mecánica de los modales:** son `<div hidden>` que un botón `data-open` des-oculta y otro `data-close` vuelve a ocultar — todo en JS plano, sin librería. Cerrar cualquier modal también libera la cámara si el escáner estaba activo.

### Notas de ajustes
* Los colores correctos deben ser (Anunciado Naranja / Recibido Azul / Entregado Verde / Cancelado Rojo).
* Deben existir los filtros y paginación, FILTROS DE BUSQUEDA (EJEMPLO: x estado, x codigo, x guia, x cliente, x telefono, x torre, x apartamento), PAGINACION INFERIOR Y SUPERIOR (EJEMPLO: Anterior 1 2 3 ... 10 Siguiente)
* En esta vista debe existir la posibilidad hacer click en un boton para anunciar un paquete a nombre de un cliente. 

---

## 7. Staff — Declarar unidad (`/announce`)

Accesible para **cualquier rol de staff** (no solo ADMIN) — se considera tarea operativa rutinaria.

**Campos:**
- `conjunto`, `torre`, `apartamento` — los tres obligatorios.
- Filas dinámicas de residentes (`nombre` + `telefono` cada una): arranca con 2 filas vacías, botón "+ Agregar residente" clona una fila, botón "×" en cada fila la quita (mínimo 1 fila siempre visible). **Ambos campos de una fila son obligatorios si se usa esa fila** — filas completamente vacías se ignoran silenciosamente; una fila con solo nombre o solo teléfono → error *"Cada residente necesita nombre Y teléfono."*
- Al menos un residente válido es obligatorio.

**Qué hace:** crea (o reutiliza) el Apartamento, y une a **todos** los teléfonos listados a esa unidad de una sola vez — esta es la única acción que hace herencia de apartamento para más de una persona a la vez (a diferencia de `/mis-datos`, que solo declara para uno mismo). Solo admite residentes **con teléfono** — un nombre sin teléfono no puede ser miembro aquí.

**Éxito:** mensaje de confirmación con conjunto/torre/apartamento y la lista de nombres creados/unidos, sin redirect (misma pantalla, formulario limpio para declarar otra unidad).

### Notas de ajustes
* La idea de la vista "/announce" es que se pueda anunciar un paquete de un cliente en su nombre.
* Los campos `conjunto`, `torre`, `apartamento` son obligatorios si se decide llegarlos, o todos vacios o todos llenos.
* Voy a realizar pruebas a esta seccion y te comentare mas adelante. 

---

## 8. Staff — Residentes (`/residentes`)

**`/residentes`** (búsqueda, GET): un campo `q`. Si `q` normaliza como teléfono válido → busca coincidencia **exacta** de teléfono. Si no → busca por nombre con coincidencia **parcial** (`ILIKE %texto%`). Sin `q` → lista vacía, sin mostrar "todos los residentes" (no hay forma de listarlos todos desde aquí).

**`/residentes/{id}`** (ficha, GET/POST): abierta a **cualquier rol de staff**.
- Campos editables: `nombre`, `email`, `tipo_documento`, `documento`, `segundo_contacto` — mismas reglas de actualización parcial y validación de email que `/mis-datos` (mismo `update_datos_personales`).
- Checkbox "Recibir notificaciones por SMS" — mismo campo que ve el propio cliente en `/mis-datos`, editable también por el staff.
- **No permite** declarar/cambiar el apartamento desde aquí (a diferencia de `/mis-datos`) — solo lo muestra en el encabezado, de solo lectura.

**Zona de peligro — "Eliminar cliente"** (visible **solo si el staff en sesión es ADMIN**; la ruta también está protegida server-side, no solo oculta en la UI):
- Confirmación vía `confirm()` nativo del navegador antes de enviar.
- No es un DELETE real: **anonimiza** (ADR-0005) — limpia los datos personales y el teléfono queda libre para que otra persona lo use en el futuro. El historial de paquetes de esa persona permanece intacto.
- Irreversible.

### Notas de ajustes
* Debe tambien contener la opcion de un numero de telefono para un segundo_contacto.
* El personal  de staff podra realizar modificacions aqui sin ninguna restriccion.
* Toda transaccion debe ser auditable, con los datos correspondientes en cada caso.

---

## 9. Staff — Administración de personal (`/administracion/personal`)

**Solo ADMIN** (`require_admin` — 403 para `OPERADOR`).

**Campos:** `email`, `nombre`, `password`, `rol` (select: `ADMIN` / `OPERADOR`) — los cuatro obligatorios.

El actor de la creación (quién dio de alta a quién) sale siempre de la sesión del ADMIN, nunca de un campo del formulario. Es la **única puerta** para crear cuentas de staff — no existe autoregistro en ningún punto de la app.

Éxito: mensaje "Cuenta creada: {email} ({rol})", formulario limpio para dar de alta otra.

### Notas de ajustes
* Se ve bien.

---

## 10. Notificaciones (transversal)

Aplica a las 3 transiciones de `/paquetes` (Recibir/Entregar/Cancelar). **`ANUNCIADO` nunca notifica** — el cliente ya lo sabe, lo acaba de hacer él mismo.

**A quién le llega el aviso** (`resolver_destino_notificable`, una sola regla unificada):
1. Si el Destinatario tiene teléfono propio **y** ese teléfono sigue perteneciendo a una Persona viva (no anonimizada) → le llega a él.
2. Si no (nunca tuvo teléfono propio — "solo un nombre" —, o lo tenía pero esa Persona fue anonimizada después) → cae al **Anunciante**, siempre que el Anunciante mismo siga vivo.
3. Si tampoco hay Anunciante vivo → no se envía nada, sin error.

Además, si a quien le tocaría recibir el aviso tiene **`notificaciones_activas = False`** → tampoco se envía nada.

**El envío es best-effort:** si el `NotificationSender` lanza una excepción, se ignora — la transición del Paquete ya se completó y no debe bloquearse por un proveedor caído.

**El mensaje** es fijo por evento (Recibido / Entregado / Cancelado con motivo), sin plantilla configurable todavía.

**Implementación actual — sin proveedor real conectado:**
- `WEB_ENV=staging` → `StagingOverrideSender`: TODO mensaje se redirige a `SMS_OVERRIDE_NUMBER`; si esa variable no está puesta, **no se envía nada** (fail-closed, nunca cae al envío real por accidente).
- Cualquier otro valor de `WEB_ENV` (incluido `production`, y el default sin definir) → `ConsoleNotificationSender` directo, sin ningún override — no hay proveedor real (Twilio, etc.) conectado todavía en ningún ambiente.

> **⚠️ Nota para el servidor de staging actual (52.6.204.211):** el `docker-compose.yml` desplegado usa `WEB_ENV=production`, no `WEB_ENV=staging`. Hoy es inofensivo porque no hay SMS real conectado en ningún caso — pero el día que se conecte un proveedor real, **hay que revisar esta variable en ese servidor específico** para que el fail-closed de `StagingOverrideSender` aplique ahí (no es un ambiente de producción real, es staging).

### Notas de ajustes
* La transaccion de anunciar un paquete si requiere notificacion via SMS.
* Los mensajes deben tener un plantilla modificable para cada caso en los cambios de estado o motivos de cancelacion.
* Para staging el numero de telefono del "SMS_OVERRIDE_NUMBER" es +573002596319, dime si ya tienes contemplado todo lo relacionado a LIWA (SMS provider), que necesitas para esto.

---

## 11. Autenticación y sesiones (transversal)

- **Staff** (`current_staff`): sesión por `usuario_id` en cookie firmada. Sin sesión válida → 401 → la app lo convierte automáticamente en redirect a `/ingresar`.
- **`require_admin`**: además exige rol `ADMIN` → 403 si no (no redirige, error directo).
- **Cliente** (`current_customer`): sesión por `persona_id`, totalmente independiente de la de staff. Sin sesión válida → 401 → redirect a `/otp`.
- **Cómo decide el 401 a dónde redirigir:** una lista fija de prefijos de ruta (`/otp`, `/mis-datos`) se considera "audiencia cliente"; cualquier otra ruta con 401 se asume de audiencia staff. Esto ya ha causado bugs de colisión de substring en el pasado (ej. `/customer` vs `/customers/manage` antes del rename) — cualquier ruta nueva que empiece parecido a estos dos prefijos hay que revisarla con cuidado.
- **Roles de staff:** `ADMIN` y `OPERADOR`. Hoy la única diferencia funcional entre ambos es: eliminar residente (§8) y dar de alta personal (§9), exclusivos de `ADMIN`. Todo lo demás (`/paquetes`, `/announce`, editar residentes) es igual para ambos roles.

### Notas de ajustes
* Se ve bien.

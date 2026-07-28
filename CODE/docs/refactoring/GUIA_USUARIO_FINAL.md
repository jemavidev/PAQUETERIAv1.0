# Guía de usuario — PAQUETEX (rebuild PaqueteXv.2)

> Entregable final del rebuild (brief [`SYSTEM_REBUILD_BRIEF.md`](SYSTEM_REBUILD_BRIEF.md) §13). Explica cómo usar el sistema **tal como está hoy desplegado en staging** (`https://test.papyrus.com.co`) — sin jerga técnica — distinguiendo qué ve un **residente** y qué ve el **staff** de portería/administración.
>
> Actualizada al cierre del roadmap de 9 grupos de ajustes post-revisión funcional (ver `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`).

---

## 0. Qué probar si vienes del roadmap reciente

Si ya conocías una versión anterior de esta guía, esto es lo que cambió y vale la pena probar primero:

| Cambio | Dónde probarlo |
|---|---|
| **Header y footer** — ya no hay pantallas "isla": arriba (o abajo, en celular) siempre hay navegación a las pantallas de tu propia audiencia | Cualquier pantalla, en escritorio y en celular |
| **`https://test.papyrus.com.co/` (sin ruta) ya no da error** — redirige a Anunciar | Abrir el dominio pelado |
| **Anunciar simplificado** — el residente solo da nombre + teléfono, ya no elige "a nombre de quién" | `/anunciar` |
| **Corregir destinatario** — el staff puede arreglar nombre/teléfono de un paquete Anunciado antes de recibirlo | `/paquetes`, botón "Corregir" |
| **Filtros, paginación y colores correctos** en la lista de paquetes | `/paquetes` |
| **Tipo, condición y foto** del paquete al recibirlo | `/paquetes`, modal "Recibir" |
| **Declarar unidad + anunciar en un solo flujo**, con Ocupantes (residentes sin teléfono propio incluidos) | `/announce` |
| **Ocupantes** visibles en la ficha del residente | `/residentes/{id}` |
| **Plantillas de notificación editables** | `/administracion/notificaciones` (solo ADMIN) |
| **Código OTP de 2 dígitos** (antes 6), válido 5 minutos | `/otp` |
| **SMS reales vía LIWA** (antes solo quedaban en consola) | Cualquier notificación — ver nota en §6 |

**Ronda 2 (en curso)** — ajustes adicionales sobre lo ya desplegado:

| Cambio | Dónde probarlo |
|---|---|
| **Quién hizo cada acción, visible** — anunció/recibió/entregó/canceló | `/consultar`, `/paquetes` |
| **Ya no se pide "documento"** en ningún formulario | `/mis-datos`, `/residentes/{id}` |
| **El Conjunto ya no lo cambia el residente** — solo Torre y Apartamento, y solo si el staff ya le asignó un Conjunto | `/mis-datos` |
| **Notificaciones por Canal × Momento** (tabla, no un solo interruptor) — hoy solo SMS envía de verdad | `/mis-datos` |
| **"Corregir" por selección**, ya no texto libre — se elige un nombre ya conocido de la lista | `/paquetes`, botón "Corregir" |
| **Búsqueda de residentes ampliada** — torre, apartamento, segundo contacto, Ocupantes | `/residentes` |
| **Login único** con pestañas Cliente/Staff, "Mis paquetes", y un solo botón de "Cerrar sesión" | `/entrar`, header |

---

## 1. ¿Qué es PAQUETEX?

Un sistema para gestionar los paquetes que llegan a un conjunto residencial. Cuando un transportador (Servientrega, Coordinadora, Amazon, etc.) deja un paquete en portería, el **staff** lo recibe y lo guarda; cuando el residente pasa a recogerlo, el staff lo entrega. PAQUETEX es el registro de todo ese recorrido, para que:

- El residente sepa que su paquete **ya llegó** y en qué estado está, sin tener que preguntar en portería.
- El staff sepa **qué hay guardado**, de quién es y desde cuándo, sin depender de un cuaderno.

Diseñado **mobile-first**: la mayoría de la gente lo va a usar desde el celular, tanto residentes como el staff en portería.

---

## 2. Cómo entrar y moverte por la app

### 2.1 El punto de entrada

`https://test.papyrus.com.co/` (el dominio solo, sin nada más) te manda directo a **Anunciar** — es la puerta pública por defecto.

### 2.2 El header (arriba) y el footer (abajo, en celular)

Toda pantalla comparte el mismo encabezado: el logo + "PAQUETEX" a la izquierda (haz clic para volver a tu pantalla principal), y a la derecha los enlaces que te corresponden **según quién eres en ese momento**:

| Quién sos | Qué ves en el header (escritorio) |
|---|---|
| Nadie ha iniciado sesión | Anunciar · Consultar · botón único "Iniciar sesión" |
| Residente con sesión verificada | Anunciar · Consultar · Mis paquetes · Mis datos · "Cerrar sesión" |
| Staff (`OPERADOR`) | Paquetes · Clientes · Consultar · "Cerrar sesión" |
| Staff (`ADMIN`) | Lo mismo que `OPERADOR`, más Personal · Notificaciones |

El botón "Iniciar sesión" lleva a `/entrar`, una sola pantalla con dos pestañas — "Soy residente" (tu teléfono, arranca el código por SMS) y "Soy del staff" (email + contraseña) — así que ya no hay que elegir de antemano cuál botón tocar.

"Mis paquetes" (nuevo) muestra tu propio historial: los paquetes que anunciaste vos y los que otros anunciaron a tu nombre, cada uno con enlace a su detalle en Consultar.

En **celular**, el nav de arriba se reemplaza por una barra fija abajo con los 4 accesos más usados de tu audiencia — igual estés con sesión o sin ella:

| Audiencia | Barra móvil |
|---|---|
| Residente (con o sin sesión) | Anunciar · Buscar · Ayuda · Whatsapp |
| Staff | Anunciar · Buscar · Paquetes · Clientes |

"Ayuda" lleva a las preguntas frecuentes (§7). "Whatsapp" solo aparece si el conjunto tiene un número de soporte configurado. "Declarar unidad" (el formulario completo de `/announce`) por ahora solo se alcanza desde ese acceso "Anunciar" del footer de staff — todavía no tiene un botón propio en el nav de escritorio, eso queda para más adelante.

**Caso particular:** si en el mismo navegador tenés sesión de residente **y** de staff a la vez (por ejemplo, un portero que también anunció un paquete propio), el header muestra **ambos** conjuntos de enlaces de navegación juntos, pero con un **único** botón "Cerrar sesión" — al presionarlo se cierran las dos sesiones a la vez, no una por una.

El enlace de la pantalla en la que estás siempre queda resaltado, para que sepas dónde estás parado.

---

## 3. Vista del residente (sin privilegios)

### 3.1 Anunciar un paquete — `/anunciar`

Sin sesión, sin login. El residente llena un formulario de **tres campos**:

1. **Nombre.**
2. **Teléfono.**
3. Aceptar los Términos y Condiciones.

Ya no se elige "a nombre de quién llega" — eso ahora lo resuelve el staff si hace falta corregirlo (ver §4.2, "Corregir"). La idea es que anunciar sea lo más simple posible: cualquier nombre + cualquier teléfono, y listo.

Al enviar, se muestra una pantalla de confirmación con un **código de acceso** (4 caracteres, sin los caracteres que se confunden entre sí: `0`, `1`, `O`, `I`, `L`) y los datos anunciados (nombre, teléfono y apartamento, si ya tenía uno asignado). Desde ahí hay enlaces directos a "Consultar mi paquete" y "Actualizar mis datos" — el residente debe guardar el código para consultar el estado más adelante.

> **Nota:** anunciar **no** pide el número de guía del transportador — eso lo captura el staff cuando el paquete físico llega a portería.

### 3.2 Consultar el estado — `/consultar`

Sin necesidad de iniciar sesión. Se busca **solo** por:
- El **código de acceso** que se dio al anunciar, o
- El **número de guía** del transportador (si el staff ya lo capturó al recibir).

**Ya no se puede consultar por teléfono** — es una medida de seguridad: el código de acceso solo lo conoce quien anunció, así que es la única llave pública de consulta.

Si hay resultado, se muestra la ficha completa: nombre del destinatario, estado actual, y la **línea de tiempo** completa (Anunciado → Recibido → Entregado, o Cancelado con su motivo), incluyendo — cuando aplica — el **tipo de paquete**, la **condición** en que llegó y la **foto** que el staff tomó al recibirlo. No se muestra qué miembro del staff hizo cada acción; ese dato es solo para auditoría interna.
**NOTA:** Si se debe mostrar que usuario realizo el anuncio (cliente/nombre del staff), recepcion (staff que recibio), Entrega (staff que entrego), cancelacion (staff que cancelo).

### 3.3 Iniciar sesión como residente — `/otp`

Para acceder a **Mis Datos**, el residente entra a `/otp`, escribe su teléfono y recibe un **código de 2 dígitos por SMS**, válido durante **5 minutos** (5 intentos como máximo). No usa contraseña — el teléfono ya es su identidad.

### 3.4 Mis Datos — `/mis-datos`

Una vez verificado por OTP, el residente puede:
- Completar o corregir su nombre, email y un **segundo contacto** (ya no se pide "documento" — se sacó de este y de todos los demás flujos del sistema).
- Actualizar Torre y Apartamento de su unidad — el **Conjunto** ya no lo puede cambiar el residente, solo el staff lo asigna (vía `/administración` o `/announce`). Mientras no tenga Conjunto asignado, tampoco puede declarar Torre/Apartamento (no tendría sentido sin saber en cuál Conjunto).
- Elegir sus **notificaciones** en una tabla de Canal × Momento: una fila por cada momento del paquete (Anunciado, Recibido, Entregado, Cancelado) y una columna por canal (SMS, Email, Llamada, WhatsApp) — cada casilla se activa o desactiva por separado. Por ejemplo, se puede querer solo WhatsApp y solo para "Anunciado", sin tocar el resto. **Hoy solo SMS envía de verdad** (viene marcado por defecto en los 4 momentos); Email, Llamada y WhatsApp se guardan igual, pero todavía no hay ningún proveedor conectado para ellos — se activarán más adelante sin que el residente tenga que volver a configurar nada.

> Si alguien intenta entrar a `/mis-datos` sin haberse verificado antes, el sistema lo manda automáticamente a `/otp` para que primero confirme su teléfono.

---

## 4. Vista del staff (con privilegios)

### 4.1 Iniciar sesión — `/ingresar`

El staff entra con **email y contraseña** (nunca con OTP — no depende del proveedor de SMS para poder trabajar). Solo un `ADMIN` puede crear cuentas nuevas de staff (ver §4.5).

### 4.2 Paquetes — `/paquetes`

La pantalla principal del staff: la lista de paquetes, con su estado marcado con una etiqueta de color:

- 🟠 **Anunciado** — el residente avisó que lo espera, pero aún no ha llegado a portería.
- 🔵 **Recibido** — ya está físicamente en portería, esperando que el residente lo recoja.
- 🟢 **Entregado** — el residente ya lo recogió (estado final).
- 🔴 **Cancelado** — se dio de baja sin entregar (estado final).

**Filtros y paginación:** se puede filtrar por estado, por texto libre (busca a la vez en código de acceso, guía, nombre y teléfono), por torre y por apartamento — todos combinables. La lista pagina de a 20 paquetes, con navegación "Anterior / números / Siguiente" arriba y abajo de la lista.

Cada paquete **Anunciado** o **Recibido** tiene botones de acción que abren una ventana (modal) sin salir de la pantalla:

- **Recibir** (solo si está Anunciado) — registra que el paquete llegó físicamente:
  - **Guía del transportador** — opcional, a mano o tocando **"📷 Escanear con cámara"** para leer el código de barras/QR automáticamente. Si la cámara falla, se escribe a mano — nunca bloquea el flujo.
  - **Tipo de paquete** (Normal / Extra dimensionado) y **Condición** (Bueno / Abierto / Regular) — ambos opcionales.
  - **Foto** — opcional, se puede adjuntar una imagen del paquete recibido; queda visible después en la línea de tiempo de `/consultar`.
- **Corregir** (solo si está Anunciado) — ajusta el destinatario antes de recibirlo, por si el residente anunció con un dato incompleto o equivocado. Ya **no se escribe a mano**: si el paquete tiene un Apartamento resuelto, el staff elige de una lista los nombres ya conocidos de esa unidad (los Ocupantes registrados vía `/announce`, más quien anunció) — nunca se puede tipear un nombre nuevo ahí, solo seleccionar uno ya validado por el propio cliente. Solo si el paquete no tiene ningún Apartamento asociado (y por lo tanto no hay ninguna lista posible) se mantiene el campo de texto libre como antes. Deja de estar disponible una vez el paquete pasa a Recibido.
- **Entregar** (solo si está Recibido) — confirma que el residente se lo llevó. Muestra a quién se entrega como recordatorio visual.
- **Cancelar** (Anunciado o Recibido) — pide un **motivo obligatorio** (Anuncio erróneo, Devuelto al transportador, No reclamado, Otro). Es **irreversible**.

Cada acción queda registrada con quién del staff la hizo y cuándo — nunca de forma anónima. Si el nombre anunciado no coincide con el nombre ya registrado para ese teléfono, aparece una advertencia visual en la tarjeta del paquete (no bloquea nada, es solo un aviso).
**NOTA:** La idea de la "guia del transportador" es que se escanee al recibir el paquete (modal recibir) y también al momento de entregar el paquete (modal de entregar) se pueda escanear esta misma guía para confirmar que se estará entregando el mismo paquete que se recibió, haciendo una doble confirmación de que ese es el paquete que se recibió para ese cliente, esto disminuye la posibilidad de cometer errores al momento de entregar un paquete, por ahora toda esta funcionalidad debería ser opcional y no bloque ante para recibir/entregar paquetes.
La idea de las fotos es que se puedan capturar hasta 3 imágenes de cada paquete, en diferentes ángulos, esto permitirá tener una confirmación de como se ve el paquete y su estado, así poder identificarlo entro todos los que existan (actualmente ya hay una implementacion de las imágenes y están guardadas en AWS S3, analiza el como se hace en la solución corriendo en producción).

### 4.3 Declarar unidad y anunciar — `/announce`

Un solo formulario con **tres bloques**, todos opcionales salvo su propia regla interna — se puede usar solo el primero, solo el tercero, o los tres juntos:

1. **Apartamento** — Conjunto, Torre y Apartamento: los tres vacíos o los tres llenos.
2. **Residentes de esa unidad (Ocupantes)** — filas de nombre + teléfono; el **teléfono es opcional por fila** (a diferencia de antes). El primer residente de una unidad nueva sí necesita teléfono obligatoriamente (es quien queda como "principal" de esa unidad); los siguientes pueden agregarse solo con nombre, sin teléfono propio — por ejemplo, para un hijo menor o alguien que no tiene celular propio, pero que igual puede recibir paquetes a su nombre.
3. **Anunciar un paquete** (opcional) — el mismo anuncio simple de `/anunciar`, pero con un campo extra: un teléfono de notificación distinto al del anunciante, por si el paquete es para otra persona de la unidad.

Es la única forma en que varios teléfonos quedan asociados a un apartamento **de una sola vez** — anunciar un paquete normal (§3.1) nunca hace esto por sí solo.

### 4.4 Residentes — `/residentes`

Buscador de residentes por teléfono, nombre, torre, apartamento, o nombre/teléfono del segundo contacto — un match por el nombre de un Ocupante (con o sin teléfono propio) lleva a la ficha de la Persona principal de esa misma unidad. Al entrar a la ficha de un residente, el staff puede:

- Editar sus datos (nombre, email, segundo contacto — ya no "documento", se sacó de todos los flujos).
- Ver la lista de **Ocupantes** de su misma unidad (los residentes registrados vía `/announce`, con o sin teléfono propio).
- Activar/desactivar sus notificaciones por SMS.
- **Eliminar cliente** (solo `ADMIN`) — no borra el historial de paquetes, pero **anonimiza** a la persona: sus datos personales se limpian y su teléfono queda libre para uso futuro. Pide confirmación porque es irreversible.

### 4.5 Administración › Personal — `/administracion/personal`

Solo visible para `ADMIN`. Crea nuevas cuentas de staff (email, nombre, contraseña, rol `ADMIN` u `OPERADOR`). Es la única puerta para crear staff nuevo.
**NOTA:** En esta sección se debería tener también una sección (tabla) donde se pueda gestionar usuarios existentes (se podrá hacer CRUD a cada uno de ellos).

### 4.6 Administración › Notificaciones — `/administracion/notificaciones`

Solo visible para `ADMIN`. Una fila editable por cada evento que notifica (Anunciado, Recibido, Entregado) más una fila por cada motivo de cancelación (Anuncio erróneo, Devuelto al transportador, No reclamado, Otro). Cada texto se puede personalizar; si no se toca, se usa el mensaje por defecto del sistema.
Así mismo como existen motivos de cancelación, debería existir 2 tipos de anuncios (ANUNCIADO · Cliente y ANUNCIADO · Staff) con su mensaje para cada caso.

---

## 5. El paquete, de principio a fin

```
Anunciado ──► Recibido ──► Entregado
    │             │
    └───────► Cancelado
```

Un dato importante para entender por qué la información de un paquete **nunca cambia después de anunciado** (salvo por "Corregir", ver §4.2, mientras siga Anunciado): al momento de anunciar, el sistema toma una "foto" (snapshot) de a quién llega, con qué teléfono y en qué apartamento. Si esa persona se muda **después**, los paquetes viejos siguen mostrando el apartamento de cuando fueron anunciados — mudarse no reescribe el historial. Los paquetes nuevos sí usarán el apartamento actualizado.

---

## 6. Notificaciones por SMS

Cada cambio de estado (Anunciado, Recibido, Entregado, Cancelado) le avisa por SMS a quien corresponda — el destinatario si tiene teléfono propio, o si no, quien anunció. Si la persona desactivó sus notificaciones (§3.4), no se le envía nada.

**Los SMS ya son reales**, enviados a través de LIWA — dejaron de ser solo un mensaje en consola. En el ambiente de staging (`test.papyrus.com.co`), por seguridad, **todo** SMS se redirige a un único número de prueba en vez de llegar al residente real — así se puede probar el flujo completo sin mandarle mensajes a nadie de verdad.

> Si al probar no llega ningún SMS, puede ser que la verificación de conectividad con LIWA siga pendiente del lado del proveedor (whitelist de IP) — no es necesariamente un error del sistema. Pregunta si tenés dudas sobre si ya está resuelto.

---

## 7. Preguntas frecuentes

**¿Qué pasa si el paquete no tiene número de guía?**
No pasa nada — es opcional. El emparejamiento entre el anuncio y el paquete físico se hace por nombre/teléfono del destinatario, no por la guía.

**¿Puedo anunciar un paquete para alguien que no tiene teléfono?**
En `/anunciar` (público) **no** — siempre se exige un teléfono válido de quien anuncia. Pero si esa persona ya es un Ocupante conocido de un apartamento que tiene un teléfono principal asociado (registrado antes vía `/announce`, §4.3), el staff sí puede anunciarle un paquete a su nombre sin que tenga teléfono propio: la notificación llega al teléfono principal de esa unidad.

**Si desactivo mis notificaciones, ¿dejo de poder anunciar o consultar paquetes?**
No — solo deja de llegar el aviso por SMS. El resto del sistema funciona exactamente igual.

**¿Qué significa que "eliminar" a un residente no borra sus paquetes?**
El historial de paquetes se conserva siempre (es la trazabilidad del conjunto), pero los datos personales de esa persona se anonimizan y su teléfono queda libre.

**Si me equivoco anunciando, ¿puedo corregirlo yo mismo?**
No — el residente no puede editar un paquete ya anunciado. Debe pedirle al staff que use "Corregir" (§4.2), disponible mientras el paquete siga en estado Anunciado.

**¿Por qué a veces veo enlaces de residente Y de staff al mismo tiempo en el header?**
Porque tenés las dos sesiones abiertas a la vez en el mismo navegador (por ejemplo, entraste como staff y también anunciaste un paquete propio). El botón "Cerrar sesión" (uno solo) cierra ambas de una vez.

---

## 8. Referencia rápida de rutas

| Ruta | Quién la usa | Qué hace |
|---|---|---|
| `/` | Cualquiera | Redirige a `/anunciar` |
| `/anunciar` | Residente (público) | Anunciar un paquete nuevo (nombre + teléfono) |
| `/consultar` | Residente (público) | Ver el estado de un paquete por código de acceso o guía |
| `/entrar` | Cualquiera (público) | Login unificado — pestañas "Soy residente" / "Soy del staff" |
| `/ayuda` | Cualquiera (público) | Preguntas frecuentes |
| `/otp` | Residente | Verificar el teléfono para entrar (código de 2 dígitos, 5 min) |
| `/mis-datos` | Residente (verificado) | Ver/editar sus propios datos, torre/apartamento y notificaciones |
| `/mis-paquetes` | Residente (verificado) | Su propio historial de paquetes (anunciados o a su nombre) |
| `/ingresar` | Staff | Iniciar sesión (email + contraseña) |
| `/mi-sesion` | Staff | Ver su propia sesión |
| `/salir-todo` | Cualquiera con sesión | Cierra TODAS las sesiones abiertas (residente y/o staff) a la vez |
| `/paquetes` | Staff | Recibir, corregir, entregar, cancelar — con filtros y paginación |
| `/announce` | Staff | Declarar unidad + Ocupantes + anunciar, en un solo flujo |
| `/residentes` | Staff | Buscar y editar clientes, ver sus Ocupantes; eliminar (solo ADMIN) |
| `/administracion/personal` | Staff (solo ADMIN) | Crear cuentas de staff |
| `/administracion/notificaciones` | Staff (solo ADMIN) | Editar los textos de los SMS por evento/motivo |

*(Nombres de ruta en español. Header y footer transversales — Grupo 9 de la Ronda 1 — implementados y verificados en staging; login unificado, "Mis paquetes" y logout único del Grupo 10 de la Ronda 2.)*

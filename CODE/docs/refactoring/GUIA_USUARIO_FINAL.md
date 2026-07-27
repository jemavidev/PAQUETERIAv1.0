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

| Quién sos | Qué ves en el header |
|---|---|
| Nadie ha iniciado sesión | Anunciar · Consultar · botón "Iniciar sesión" (residente) · botón "Staff" |
| Residente con sesión verificada | Anunciar · Consultar · Mis datos · "Cerrar sesión" |
| Staff (`OPERADOR`) | Paquetes · Declarar unidad · Residentes · Consultar · "Cerrar sesión" |
| Staff (`ADMIN`) | Lo mismo que `OPERADOR`, más Personal · Notificaciones |

En **celular**, los mismos enlaces (los 2-3 más usados) se repiten como una barra fija abajo, para no tener que estirar el pulgar hasta arriba.

**Caso particular:** si en el mismo navegador tenés sesión de residente **y** de staff a la vez (por ejemplo, un portero que también anunció un paquete propio), el header muestra **ambos** conjuntos de enlaces juntos, cada uno con su propio botón de cerrar sesión — cerrar una sesión nunca cierra la otra.

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

### 3.3 Iniciar sesión como residente — `/otp`

Para acceder a **Mis Datos**, el residente entra a `/otp`, escribe su teléfono y recibe un **código de 2 dígitos por SMS**, válido durante **5 minutos** (5 intentos como máximo). No usa contraseña — el teléfono ya es su identidad.

### 3.4 Mis Datos — `/mis-datos`

Una vez verificado por OTP, el residente puede:
- Completar o corregir su nombre, email, documento y un **segundo contacto**.
- Declarar o actualizar su apartamento (Conjunto/Torre/Apartamento).
- Activar o desactivar el interruptor de **"Recibir notificaciones por SMS"** — si lo apaga, deja de recibir avisos automáticos de sus paquetes (el sistema sigue funcionando igual, solo no le escribe).

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
- **Corregir** (solo si está Anunciado) — permite ajustar el **nombre** y el **teléfono de notificación** del destinatario antes de recibirlo, por si el residente anunció con un dato incompleto o equivocado. Deja de estar disponible una vez el paquete pasa a Recibido.
- **Entregar** (solo si está Recibido) — confirma que el residente se lo llevó. Muestra a quién se entrega como recordatorio visual.
- **Cancelar** (Anunciado o Recibido) — pide un **motivo obligatorio** (Anuncio erróneo, Devuelto al transportador, No reclamado, Otro). Es **irreversible**.

Cada acción queda registrada con quién del staff la hizo y cuándo — nunca de forma anónima. Si el nombre anunciado no coincide con el nombre ya registrado para ese teléfono, aparece una advertencia visual en la tarjeta del paquete (no bloquea nada, es solo un aviso).

### 4.3 Declarar unidad y anunciar — `/announce`

Un solo formulario con **tres bloques**, todos opcionales salvo su propia regla interna — se puede usar solo el primero, solo el tercero, o los tres juntos:

1. **Apartamento** — Conjunto, Torre y Apartamento: los tres vacíos o los tres llenos.
2. **Residentes de esa unidad (Ocupantes)** — filas de nombre + teléfono; el **teléfono es opcional por fila** (a diferencia de antes). El primer residente de una unidad nueva sí necesita teléfono obligatoriamente (es quien queda como "principal" de esa unidad); los siguientes pueden agregarse solo con nombre, sin teléfono propio — por ejemplo, para un hijo menor o alguien que no tiene celular propio, pero que igual puede recibir paquetes a su nombre.
3. **Anunciar un paquete** (opcional) — el mismo anuncio simple de `/anunciar`, pero con un campo extra: un teléfono de notificación distinto al del anunciante, por si el paquete es para otra persona de la unidad.

Es la única forma en que varios teléfonos quedan asociados a un apartamento **de una sola vez** — anunciar un paquete normal (§3.1) nunca hace esto por sí solo.

### 4.4 Residentes — `/residentes`

Buscador de residentes por teléfono o nombre. Al entrar a la ficha de un residente, el staff puede:

- Editar sus datos (nombre, email, documento, segundo contacto).
- Ver la lista de **Ocupantes** de su misma unidad (los residentes registrados vía `/announce`, con o sin teléfono propio).
- Activar/desactivar sus notificaciones por SMS.
- **Eliminar cliente** (solo `ADMIN`) — no borra el historial de paquetes, pero **anonimiza** a la persona: sus datos personales se limpian y su teléfono queda libre para uso futuro. Pide confirmación porque es irreversible.

### 4.5 Administración › Personal — `/administracion/personal`

Solo visible para `ADMIN`. Crea nuevas cuentas de staff (email, nombre, contraseña, rol `ADMIN` u `OPERADOR`). Es la única puerta para crear staff nuevo.

### 4.6 Administración › Notificaciones — `/administracion/notificaciones`

Solo visible para `ADMIN`. Una fila editable por cada evento que notifica (Anunciado, Recibido, Entregado) más una fila por cada motivo de cancelación (Anuncio erróneo, Devuelto al transportador, No reclamado, Otro). Cada texto se puede personalizar; si no se toca, se usa el mensaje por defecto del sistema.

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
Sí, de dos formas: al anunciar en `/anunciar` cualquiera puede poner el nombre que quiera (no se valida contra nada); o el staff puede registrar a esa persona como Ocupante sin teléfono desde `/announce` (§4.3), para que quede como residente permanente de la unidad, no solo dentro de un paquete puntual.

**Si desactivo mis notificaciones, ¿dejo de poder anunciar o consultar paquetes?**
No — solo deja de llegar el aviso por SMS. El resto del sistema funciona exactamente igual.

**¿Qué significa que "eliminar" a un residente no borra sus paquetes?**
El historial de paquetes se conserva siempre (es la trazabilidad del conjunto), pero los datos personales de esa persona se anonimizan y su teléfono queda libre.

**Si me equivoco anunciando, ¿puedo corregirlo yo mismo?**
No — el residente no puede editar un paquete ya anunciado. Debe pedirle al staff que use "Corregir" (§4.2), disponible mientras el paquete siga en estado Anunciado.

**¿Por qué a veces veo enlaces de residente Y de staff al mismo tiempo en el header?**
Porque tenés las dos sesiones abiertas a la vez en el mismo navegador (por ejemplo, entraste como staff y también anunciaste un paquete propio). Son independientes: cerrar una no cierra la otra.

---

## 8. Referencia rápida de rutas

| Ruta | Quién la usa | Qué hace |
|---|---|---|
| `/` | Cualquiera | Redirige a `/anunciar` |
| `/anunciar` | Residente (público) | Anunciar un paquete nuevo (nombre + teléfono) |
| `/consultar` | Residente (público) | Ver el estado de un paquete por código de acceso o guía |
| `/otp` | Residente | Verificar el teléfono para entrar (código de 2 dígitos, 5 min) |
| `/mis-datos` | Residente (verificado) | Ver/editar sus propios datos, apartamento y notificaciones |
| `/ingresar` | Staff | Iniciar sesión (email + contraseña) |
| `/mi-sesion` | Staff | Ver su propia sesión y cerrar sesión |
| `/paquetes` | Staff | Recibir, corregir, entregar, cancelar — con filtros y paginación |
| `/announce` | Staff | Declarar unidad + Ocupantes + anunciar, en un solo flujo |
| `/residentes` | Staff | Buscar y editar clientes, ver sus Ocupantes; eliminar (solo ADMIN) |
| `/administracion/personal` | Staff (solo ADMIN) | Crear cuentas de staff |
| `/administracion/notificaciones` | Staff (solo ADMIN) | Editar los textos de los SMS por evento/motivo |

*(Nombres de ruta en español. Header y footer transversales — Grupo 9 del roadmap post-revisión funcional — implementados y verificados en staging.)*

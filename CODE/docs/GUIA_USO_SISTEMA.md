# Guía de uso — PaqueteX

Guía básica del sistema de paquetería para el conjunto residencial. Cubre las dos audiencias del sistema — **residentes** (clientes) y **staff** (personal de portería/administración) — y al final lo que un **Administrador** puede hacer de más sobre un Staff normal.

> Para el glosario completo del dominio (Persona, Ocupante, Apartamento, Paquete...) ver [`CONTEXT.md`](../../CONTEXT.md) en la raíz del repo.

---

## 1. Los dos tipos de sesión

El sistema tiene **dos sesiones independientes** que pueden coexistir en el mismo navegador:

| | Residente | Staff |
|---|---|---|
| Quién | Cualquier persona del conjunto | Personal de Papyrus (portería/administración) |
| Cómo entra | Código de un solo uso (OTP) por SMS/WhatsApp | Email + contraseña |
| Qué ve | Solo sus propios datos y paquetes | Todos los paquetes y residentes del conjunto |

Se entra por una única puerta, **`/entrar`**, con un selector "Cliente" / "Staff" arriba del formulario.

---

## 2. Guía para Residentes

### 2.1 Iniciar sesión

1. Entra a `/entrar` → pestaña **Cliente**.
2. Escribe tu número de teléfono (ej. `3001234567`).
3. Llega un código de 6 dígitos por SMS o WhatsApp — escríbelo en la siguiente pantalla.
4. Quedas dentro. No hay contraseña que recordar: cada inicio de sesión pide un código nuevo.

### 2.2 "Mis Datos" (`/mis-datos`)

Tu ficha personal editable:

- **Nombre, email, WhatsApp** — los puedes corregir tú mismo en cualquier momento.
- **Torre/Apartamento** — se ve, pero es de **solo lectura**: la asignación de unidad la hace únicamente el staff (evita que alguien se auto-asigne el apartamento de otra persona).
- **Preferencias de notificación** — una tabla de casillas por *Canal* (SMS, WhatsApp, Email) × *Evento* (paquete anunciado, recibido, etc.), para elegir cómo te avisamos.
- **Residentes de tu unidad** — si eres el residente **Principal** de tu apartamento, aquí también agregas o das de baja a los demás residentes de tu unidad (ej. tu pareja, un hijo). Si no eres el Principal, no ves esta sección.

### 2.3 "Mis Paquetes" (`/mis-paquetes`)

Historial de todos los paquetes de tu apartamento (los que anunciaste tú y los que anunció cualquier otro residente activo de tu misma unidad), organizado en pestañas por estado (Anunciado, Recibido, Entregado). Cada paquete se puede abrir para ver su línea de tiempo completa y sus fotos.

### 2.4 Consultar un paquete sin iniciar sesión (`/consultar`)

Página pública. Sirve para que **cualquiera** (no hace falta ser residente ni tener sesión) revise el estado de un paquete puntual con el **código de acceso** que se generó al anunciarlo — por ejemplo `A3F9K2`. Nunca se busca por teléfono acá, solo por ese código (o por el número de guía del transportador).

---

## 3. Guía para Staff (rol Operador)

### 3.1 Iniciar sesión

`/entrar` → pestaña **Staff** → email + contraseña (las crea un Administrador, ver sección 4). Si la olvidas, "¿Olvidaste tu contraseña?" en `/staff/olvide-password` envía un enlace de recuperación por correo.

### 3.2 Paquetes (`/paquetes`) — el módulo principal

Lista completa de paquetes con acciones sobre su ciclo de vida:

```
ANUNCIADO  →  RECIBIDO  →  ENTREGADO
    ↓             ↓
              CANCELADO
```

- **Recibir** — cuando el transportador deja el paquete en portería: registras tipo (caja, sobre...), condición, y opcionalmente una foto.
- **Entregar** — cuando el residente lo retira.
- **Cancelar** — con motivo obligatorio (ej. "el residente ya no vive acá").
- **Ver** — abre el detalle: destinatario, Torre/Apto (enlaza directo a la ficha del residente), línea de tiempo completa con quién hizo qué y cuándo, y las fotos.
- **Asignar apartamento / Corregir destinatario** — si el paquete quedó con datos incompletos o el nombre no coincide con ningún residente real de la unidad, estas acciones lo enlazan a la persona correcta.

### 3.3 Anunciar (`/announce`) — registrar un paquete nuevo rápido

Un solo campo de texto que detecta automáticamente qué escribiste:

| Escribes | Se interpreta como |
|---|---|
| `3001234567` (10 dígitos, empieza en 3) | Teléfono |
| `0502` (empieza en 0 o 1) | Torre + Apartamento — primeros 2 dígitos son la Torre (`05`), el resto el Apartamento (`02`) |
| `juanperez` (empieza con letra) | Usuario de WhatsApp |

El sistema resuelve quién es (o te deja crear a la persona si no existe) y confirmas el anuncio.

### 3.4 Residentes (`/residentes`) — buscar y gestionar

Barra de búsqueda unificada que acepta:

- Nombre, teléfono (completo o parcial), WhatsApp, email
- Apartamento con el esquema `apt302` (Apartamento 302, en cualquier Torre)

La ficha de cada residente tiene 4 pestañas: **Datos**, **Dirección** (asignar/mover de apartamento), **Notificaciones**, **Residentes** (los demás ocupantes de su misma unidad). A diferencia del residente en `/mis-datos`, el staff sí puede cambiar la Torre/Apartamento de cualquier persona.

Botones "Listar principales" / "Agrupar por apartamento" ayudan a ver toda una unidad de un vistazo en vez de resultados sueltos.

### 3.5 Consultar (`/consultar`)

Misma vista pública de la sección 2.4, pero con sesión de staff activa aparecen botones extra de **Recibir**/**Entregar** directamente ahí, sin tener que ir a `/paquetes`.

### 3.6 Cerrar sesión

El botón de salir en el header cierra **ambas** sesiones si coexisten (staff + cliente en el mismo navegador) de una sola vez.

---

## 4. Lo que un Administrador hace de más

Un Administrador ve y usa **todo lo del staff normal** (sección 3), más tres pantallas exclusivas bajo `/administracion/` y dos acciones destructivas que un Operador no puede ejecutar:

### 4.1 Personal (`/administracion/personal`)

Alta y gestión de cuentas de staff: crear una cuenta nueva (email + contraseña + rol Admin/Operador), editar datos, **resetear la contraseña** de cualquiera, y activar/desactivar cuentas (desactivar corta la sesión ya abierta de esa persona, no solo bloquea su próximo login).

### 4.2 Notificaciones (`/administracion/notificaciones`)

Edita el texto de los mensajes automáticos que el sistema envía por cada evento (paquete anunciado, recibido, cancelado con motivo, etc.) — el contenido real que le llega al residente por SMS/WhatsApp/Email.

### 4.3 Nombre del conjunto (`/administracion/conjunto`)

Cambia el nombre del conjunto residencial que se muestra en toda la app y en las notificaciones.

### 4.4 Borrar de verdad (en vez de anonimizar)

El resto del sistema nunca borra filas — anonimiza o archiva, para no romper el historial de auditoría. Solo un Admin puede:

- **Eliminar un paquete**, y solo mientras sigue en estado ANUNCIADO (antes de tener fotos o historial real).
- **Eliminar (anonimizar) un residente** — para casos de "olvido" de datos personales.

Un Operador normal ni siquiera ve estos botones; si de alguna forma llegara al endpoint directamente, el servidor lo rechaza igual.

---

## 5. Glosario rápido

| Término | Significado |
|---|---|
| **Persona** | Cualquier residente conocido por el sistema (registrado al anunciar o creado por staff). |
| **Ocupante** | Un residente ya vinculado formalmente a un Apartamento. |
| **Principal** | El Ocupante responsable de una unidad — el único que ve/gestiona a los demás residentes de su apartamento en `/mis-datos`. |
| **Usuario** | Cuenta de staff (rol `ADMIN` u `OPERADOR`) — nunca se usa para nombrar a un residente. |
| **Código de acceso** | Código corto que identifica un paquete para consultarlo públicamente en `/consultar`. |
| **Anunciar** | Registrar que se espera (o llegó) un paquete, antes de que el staff lo reciba físicamente. |

# CONTEXT — PAQUETEX (rebuild PaqueteXv.2)

Glosario de dominio y lenguaje ubicuo del sistema. **Los skills deben usar estos términos** tal como se definen aquí (en títulos de tickets, specs, hipótesis, nombres de test). No derivar a sinónimos que el glosario evita explícitamente.

> Diseño completo en [`CODE/docs/refactoring/SYSTEM_REBUILD_BRIEF.md`](CODE/docs/refactoring/SYSTEM_REBUILD_BRIEF.md), restricciones de la base actual en [`DATABASE_CONSTRAINTS.md`](CODE/docs/refactoring/DATABASE_CONSTRAINTS.md), bugs a no heredar en [`PACKAGES_DIAGNOSIS.md`](CODE/docs/refactoring/PACKAGES_DIAGNOSIS.md). Las decisiones de dominio se resolvieron en una sesión de grilling (2026-07-22).

## Qué es el sistema

Gestión de paquetería para un **conjunto residencial**, **mobile-first** (90% del uso desde celular). Un transportador entrega paquetes en la portería; el **staff** los recibe, almacena y entrega a los residentes; los **residentes** anuncian que esperan un paquete y consultan su estado.

---

## Las dos audiencias

- **Staff (con privilegios)** — administra y gestiona paquetes: recibe, entrega, cancela, anuncia por un cliente, gestiona clientes y administración. Identidad separada de los clientes (entidad **Usuario**, roles `ADMIN` / `OPERADOR`).
- **Cliente (sin privilegios)** — residente, **registrado o no**. Se registra implícitamente al anunciar; puede anunciar paquetes y consultar su estado. Nunca administra.

Término evitado: no llamar "usuario" al cliente ni "cliente" al staff. **Usuario = staff**; **Persona/Cliente = residente**.

---

## Glosario del modelo de datos

Definido pregunta a pregunta en el grilling. Es el corazón del rebuild.

### Persona
Un residente. **Su identidad estable es el Teléfono o el usuario de WhatsApp** — siempre existe AL MENOS uno de los dos (nunca ninguno, [ADR-0007](docs/adr/0007-persona-telefono-o-whatsapp.md), que relaja [ADR-0003](docs/adr/0003-telefono-llave-universal.md)). El Teléfono sigue siendo la ÚNICA llave que habilita login/OTP y notificaciones automáticas — una Persona solo-WhatsApp existe y puede ser Ocupante (incluso Principal, ver sección Ocupante), pero no puede loguearse ni recibir avisos automáticos todavía. Tiene nombre, un **Apartamento actual** (opcional, mutable) y datos de registro ampliables (email, documento, segundo contacto…). Se crea implícitamente al anunciar (teléfono + nombre, o usuario de WhatsApp + nombre) y amplía sus datos desde `/mis-datos`.

- Término evitado: **`display_name` huérfano** — el modelo viejo guardaba un nombre de texto libre suelto en el paquete, sin identidad. Ya no existe: todo nombre vive bajo una identidad real (Teléfono o WhatsApp).
- Término evitado: "cliente = teléfono único e inmutable" (modelo viejo, phone-céntrico rígido). Aquí el Teléfono (o el WhatsApp) es la llave, pero la Persona es la entidad.

### Teléfono
La identidad de una Persona **cuando la tiene** — habilita login/OTP y notificaciones automáticas, ninguna otra vía las habilita todavía (ADR-0007). No siempre existe: una Persona solo-WhatsApp no lo tiene.

### Usuario de WhatsApp (`whatsapp_usuario`)
Identidad alterna de una Persona, con la misma garantía de unicidad que el Teléfono (ADR-0007) — una Persona tiene Teléfono, WhatsApp, o ambos, nunca ninguno. No habilita login/OTP ni notificaciones automáticas (depende de un canal de envío por WhatsApp que este rebuild no construye todavía).

### Apartamento
La unidad de vivienda: **Conjunto → Torre → Apartamento**. Entidad **ligera** (creable sobre la marcha) y **opcional** — puede existir o no. Es un **agrupador** al que se asocian Teléfonos.

- Término evitado: "Residencia" como entidad única — se usa **Apartamento** para la unidad y *Conjunto/Torre/Apartamento* para su jerarquía.

### Apartamento actual (membresía mutable)
Una Persona tiene **un** Apartamento *actual*. Es **mutable**: puede **mudarse** a otro Apartamento o **desvincularse** en cualquier momento. La relación es **1↔1 en el tiempo (secuencial)**, no varios apartamentos a la vez.

### Herencia de apartamento
Cuando a un Teléfono de un grupo "**misma unidad**" se le asigna un Apartamento, los demás Teléfonos del grupo lo **heredan** automáticamente. El grupo se forma solo al **declarar la unidad a propósito** (staff en `/announce`, o el cliente en `/mis-datos`) — **nunca** por un "a nombre de" casual en `/anunciar`. Como mudarse/desvincular está siempre disponible, cualquier herencia errónea es **corregible**.

El **grupo "misma unidad" no es una entidad persistente**: es el conjunto emergente de Personas que comparten el mismo Apartamento actual, no una lista almacenada aparte. Declarar la unidad es el **acto** que asigna ese Apartamento a varios Teléfonos a la vez — ese acto *es* la herencia.

Declarar la unidad es también, hoy, la forma de registrar **Ocupantes** de un Apartamento (con o sin Teléfono) — ver más abajo.

### Anunciante y Destinatario
Cada Paquete guarda **dos referencias independientes** (pueden coincidir o no):
- **Anunciante** (`anunciado_por`) — la Persona (Teléfono) que anuncia el paquete.
- **Destinatario** — a nombre de quién llega el paquete.

### Nombre sin teléfono
Un Destinatario que no tiene (o no da) su propio Teléfono se representa como un **nombre bajo el Teléfono del Anunciante** — no es una Persona sin llave. Así el Teléfono nunca falta como identidad.

No tiene **existencia propia** fuera del Paquete: vive **solo dentro del snapshot** del paquete que lo nombra, no como registro independiente. Distinto de **Ocupante** (abajo), que sí persiste — un "nombre sin teléfono" es un caso puntual y no planeado (alguien anunció sin dar el teléfono del destinatario); un Ocupante es un residente reconocido a propósito como parte del padrón de un Apartamento.

### Ocupante
Un residente reconocido de un **Apartamento**, con nombre y **Persona propia opcional** — la decisión que ADR-0003 dejaba pendiente (ver [ADR-0006](docs/adr/0006-ocupante-residentes-sin-persona-propia.md)). Cada Apartamento exige exactamente **un** Ocupante **principal**, con Persona propia **obligatoria** — Teléfono o usuario de WhatsApp, nunca ninguno de los dos ([ADR-0007](docs/adr/0007-persona-telefono-o-whatsapp.md)). Los demás Ocupantes del mismo Apartamento pueden o no tener Persona propia; si la tienen, esa Persona puede tener Teléfono, WhatsApp, o ambos (con acceso vía OTP solo si tiene Teléfono).

- El principal es **intercambiable**: cualquier Ocupante con Persona propia (Teléfono o WhatsApp) puede **promoverse** a principal, degradando al anterior (que sigue siendo Ocupante, solo deja de ser el principal).
- Un Ocupante **sin** Persona propia no puede loguearse ni anunciar por sí mismo — sirve para que un Paquete se le anuncie a su nombre de forma reconocible y persistente (a diferencia de "Nombre sin teléfono", que no persiste).
- Si alguien anuncia con el Teléfono/WhatsApp del principal o el de otro Ocupante-con-Persona-propia, la notificación llega a esa misma identidad que anunció (si es capaz de recibir notificaciones automáticas — un WhatsApp-solo todavía no, ver ADR-0007).
- Término evitado: "segundo contacto" (nombre coloquial usado antes de resolver el modelo) — el término del glosario es **Ocupante**.

### Contexto de entrega (snapshot)
Al **anunciar**, el Paquete **congela** una foto inmutable de `{anunciado_por (teléfono), nombre_destinatario, teléfono_destinatario (si hay), apartamento}`. Si la Persona se muda **después**, los paquetes viejos **siguen mostrando el apartamento de entonces** — mudarse **nunca reescribe la historia**. "Los datos permanecen de principio a fin en cada paquete."

- Término clave: **snapshot** / **contexto de entrega congelado**. Evitar "referencia al estado actual de la persona" para datos de un paquete ya anunciado.

### Paquete
La unidad física gestionada. Tiene su Contexto de entrega (snapshot), un **Estado** del ciclo de vida, y `guide_number` opcional.

### Estados del Paquete (ciclo de vida)
`Anunciado` → `Recibido` → `Entregado`, o `Cancelado`. Transiciones controladas por una **máquina de estados** (a detallar en el spec). Cada transición registra **quién** la hizo (desde la sesión real, nunca un id hardcodeado) y **cuándo**.

### Anuncio
El acto/registro por el que un cliente declara que espera un paquete (nombre + teléfono + a nombre de quién). Da origen a un Paquete en estado `Anunciado`. **No** captura número de guía.

### Guía (`guide_number`)
Número del transportador. **Opcional** — no todos los operadores la usan hoy. Se captura al **Recibir**, escaneando el código de barras del paquete físico (referencia). El **emparejamiento** anuncio↔paquete físico se hace **por nombre/teléfono** del destinatario, no por la guía. El diseño deja espacio para **promover la guía a llave de emparejamiento a futuro** sin romper el esquema.

### Usuario (staff)
Miembro del staff. Entidad separada de la Persona. Roles `ADMIN` / `OPERADOR`. **Solo un `ADMIN` crea cuentas de staff.**

---

## Autenticación

- **Clientes**: **OTP por teléfono** (baja fricción; ya dan el teléfono).
- **Staff**: **usuario/email + contraseña fuerte**; no depende del proveedor SMS para entrar. MFA opcional a futuro.

---

## Invariantes y reglas de dominio

1. **Toda Persona tiene Teléfono o usuario de WhatsApp** (nunca ninguno de los dos, ADR-0007); el Teléfono es la única identidad que habilita login/OTP y notificaciones automáticas.
2. **El Paquete es inmutable en su contexto de entrega** una vez anunciado (snapshot). Mudarse no reescribe paquetes viejos.
3. **El actor de cada acción sale de la sesión real** — nunca un `operator_id`/`user_id` hardcodeado.
4. **Un solo endpoint por acción** (recibir/entregar/cancelar). Sin rutas legacy paralelas.
5. **Auth activa siempre**, también en lectura.
6. **Override de notificaciones en staging es fail-closed**: si falta la config, no se envía a nadie (nunca cae al envío real).
7. **Los modales nunca se quedan bloqueados**: todo flujo de modal re-habilita el botón con `finally`, pase lo que pase (ver `PACKAGES_DIAGNOSIS.md`).

---

## Vistas por audiencia

Nombres de ruta en español amigable (decidido 2026-07-26, ver `docs/adr/` si aplica) — el resto del glosario de este documento no cambia, solo el path visible en el navegador.

- **Sin privilegios**: `/anunciar`, `/consultar`, `/help`, `/terms`, `/privacy`, `/cookies`, `/mis-datos`, `/otp` (login OTP de cliente), `/auth/forgot-password`.
- **Con privilegios**: `/paquetes` (principal), `/announce` (declarar unidad en lote — sin sufijo "-new"), `/residentes`, `/administracion/personal`, `/ingresar` (login de staff).
- **Eliminadas**: `/messages` y toda la mensajería cliente↔staff.

---

## Fuera de alcance de este rebuild

**Facturas / CUFE / Products** (`/invoices`, `/products`, y todo el subsistema DIAN/CUFE) — pertenecen a otra reestructuración. No se tocan. `file_uploads` se conserva **solo para fotos de paquete**; el resto se recorta.

---

## Infraestructura (resumen; detalle en el brief)

- **Prod ≈ 2 GB / staging ≈ 1 GB** en AWS Lightsail, una caja por ambiente (app + Postgres + Redis + Caddy). El objetivo de $5 se descartó con evidencia de swap.
- **D/R**: `pg_dump` horario → S3 cifrado/versionado (RPO ~1 h); imágenes ya en S3. Portable a cualquier nube.
- **CI/CD**: local → GitHub → deploy auto a staging → aprobación manual (GitHub Environments) → prod. Rama de rebuild: **`PaqueteXv.2`**.

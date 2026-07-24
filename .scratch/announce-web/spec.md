# Spec — `/announce` (anunciar) + capa web clean-room

Status: ready-for-agent
Feature: announce-web
Branch: PaqueteXv.2
Depende de: `data-model` (servicio `announce`, `Destinatario`) y el arnés de Postgres efímero. Primera rebanada que cruza la capa HTTP.
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §3/§7/§8 · `CONTEXT.md` (Anuncio, Anunciante, Destinatario, Nombre sin teléfono) · `PACKAGES_DIAGNOSIS.md` (modales/finally)

---

## Problem Statement

El servicio de dominio `announce` ya existe y sabe crear un Paquete `ANUNCIADO` con su snapshot congelado — pero **no hay forma de que un residente anuncie desde su celular**: no existe ruta HTTP ni formulario nuevos. Y el rebuild no puede simplemente colgarse de la app vieja: su `config.py` **exige credenciales AWS S3 al arrancar** (`_validate_required_settings` lanza si faltan) y su app factory importa todo el mundo fuera de alcance (facturas/CUFE), así que montar una ruta nueva sobre él **falla al importar**. El dominio nuevo ya vive aislado (`app/domain/`) justo por esto; ahora la capa web necesita su propia puerta de entrada.

Desde la perspectiva del residente: quiere avisar que espera un paquete escribiendo su nombre y teléfono desde el móvil, y hoy no hay dónde hacerlo en el sistema nuevo.

## Solution

Una **capa web clean-room** (app factory FastAPI nuevo, server-rendered, desacoplado del `config`/app viejos) y su primera ruta: **`/announce`**. El residente abre `/announce`, escribe **nombre + teléfono**, acepta **T&C**, elige **a nombre de quién** llega (yo mismo / otra persona registrada por su teléfono / solo un nombre sin teléfono) y envía. El sistema **registra o reutiliza** su Persona (por teléfono), crea el Paquete en `ANUNCIADO` con su **snapshot congelado**, y muestra una **confirmación** con el número de seguimiento / código de acceso. Mobile-first, server-rendered (Tailwind + Alpine/HTMX), **sin número de guía**.

## User Stories

1. Como **residente**, quiero abrir `/announce` en mi celular y ver un formulario simple, para anunciar un paquete sin fricción.
2. Como **residente**, quiero escribir mi **nombre** y **teléfono**, para que el sistema sepa quién soy (mi teléfono es mi identidad).
3. Como **residente nuevo**, quiero quedar **registrado implícitamente** al anunciar (teléfono + nombre), sin un paso de registro aparte.
4. Como **residente recurrente**, quiero que anunciar con mi teléfono ya conocido **reutilice mi Persona**, sin duplicarme, aunque escriba el número en otro formato.
5. Como **residente**, quiero **aceptar los T&C** como parte del anuncio, y que el envío se bloquee si no los acepto.
6. Como **residente**, quiero anunciar **a mi propio nombre** (por defecto), para el caso más común.
7. Como **residente**, quiero anunciar **a nombre de otra persona registrada** dando su teléfono, para recibir por un vecino/familiar registrado.
8. Como **residente**, quiero anunciar **a nombre de solo un nombre** (sin teléfono), y que ese nombre quede **bajo mi teléfono**, sin inventar una identidad sin llave.
9. Como **residente**, quiero que ese "a nombre de" casual **no me agrupe** con nadie en un apartamento (un favor puntual no cambia mi unidad).
10. Como **residente**, quiero recibir una **confirmación** con mi número de seguimiento / código de acceso, para consultarlo luego.
11. Como **residente**, quiero **no tener que escribir un número de guía** al anunciar, porque no lo tengo (lo captura el staff al recibir).
12. Como **residente**, quiero que si dejo un campo obligatorio vacío (nombre, teléfono, T&C) el formulario me lo **avise** y **no cree** un paquete a medias.
13. Como **residente en móvil**, quiero botones grandes y un layout de una columna, para usarlo con el pulgar.
14. Como **operador del sistema**, quiero que la app nueva **arranque sin credenciales AWS** (S3 está fuera de alcance de esta rebanada), para poder correr y testear la ruta.
15. Como **desarrollador**, quiero **una sola ruta `/announce`** en la capa nueva, sin heredar las rutas legacy paralelas de announce, para no repetir el desorden viejo.
16. Como **QA**, quiero poder probar `/announce` de punta a punta (petición → respuesta → Paquete en la BD) contra un Postgres real efímero, para confiar en el flujo.
17. Como **residente**, quiero que si el envío falla, la UI **no se quede bloqueada** (el botón se re-habilita), para reintentar (bug a no heredar, `PACKAGES_DIAGNOSIS.md`).

## Implementation Decisions

### Capa web clean-room (prefactor de esta rebanada)

- **App factory FastAPI nuevo** en un módulo web propio del rebuild (p.ej. `app/web/`), **desacoplado** de `app/config.py` (que exige AWS) y de `src/main.py`. Lee la conexión desde `DATABASE_URL` directamente (o un settings mínimo del rebuild), **sin** requerir credenciales AWS/S3 (fuera de alcance).
- **Dependencia de sesión de BD** propia (estilo `get_db`) que entrega una `Session` de SQLAlchemy por request con **commit al éxito / rollback al error**, sobre un engine construido desde `DATABASE_URL`. No reutiliza el `get_db` viejo (atado al config con AWS).
- **Templates server-rendered** (Jinja2) + **Tailwind + Alpine/HTMX**, cero proceso Node en runtime (brief §3). Se puede **reutilizar el look & feel** de los templates viejos (`src/templates/announce/*.html`) como referencia, pero la ruta nueva usa su propio template.
- Esta capa **no** monta las rutas viejas; crece ruta por ruta con el rebuild y eventualmente reemplaza `main.py`.

### La ruta `/announce`

- **`GET /announce`**: renderiza el formulario — **nombre**, **teléfono**, checkbox **T&C**, y un selector **"a nombre de quién"** con 3 opciones (yo mismo / otra persona registrada [pide su teléfono] / solo un nombre [pide el nombre]). **Sin** campo de número de guía.
- **`POST /announce`**: valida (nombre, teléfono y T&C obligatorios); mapea la selección a un `Destinatario` (`yo_mismo()` / `persona_registrada(telefono)` / `solo_nombre(nombre)`); llama a `announce(session, anunciante_telefono, anunciante_nombre, destinatario)`; hace commit; responde con una **confirmación** que muestra `tracking_number` / `access_code`.
- **Contrato**: `POST` form-encoded (no JSON SPA); respuesta server-rendered (página de confirmación o redirect a un detalle). El "a nombre de" casual **no** toca `apartamento_actual` de nadie (ya garantizado por el dominio: `announce` nunca escribe membresía).
- **Errores de validación**: re-renderiza el formulario con los mensajes y **sin** crear Paquete. Un `LookupError` de `persona_registrada` (destino no registrado) se traduce a un mensaje de campo ("ese teléfono no está registrado; usa 'solo un nombre'").
- **JS con `finally`**: el submit re-habilita el botón pase lo que pase (bug a no heredar).

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable por HTTP** — el status, que la respuesta contenga lo esperado (formulario / confirmación / error), y el **efecto en la BD** (se creó o no un Paquete `ANUNCIADO` con el snapshot correcto) — no los internals de la vista ni el HTML exacto.

**Costura (nueva, la más alta del slice):** **HTTP con `TestClient` de FastAPI** contra el **app nuevo**, con la BD = **Postgres efímero construido con `alembic upgrade head`** (se reutiliza el arnés `tests/data_model`/conftest). La ruta delega en la costura de dominio existente (`announce`). **Una sola costura nueva**; por debajo, el dominio ya está cubierto.

**Casos (mapean a las user stories):**
- `GET /announce` → 200, el HTML tiene los campos nombre/teléfono/T&C y el selector; **no** tiene campo de guía.
- `POST` válido a nombre propio → crea un Paquete `ANUNCIADO`; la respuesta muestra `tracking_number`; la Persona quedó registrada.
- `POST` en los 3 casos de "a nombre de" (yo / registrada / solo nombre) → el Paquete refleja el destinatario correcto (incl. nombre sin teléfono bajo el tel del anunciante).
- `POST` sin teléfono / sin nombre / sin T&C → re-render con error, **cero** Paquetes creados.
- `POST` a nombre de un teléfono no registrado → mensaje de error claro, sin Paquete.

**Prior art:** los tests de dominio (`tests/data_model/test_announce_paquete.py`) para el comportamiento subyacente; el arnés de Postgres efímero. Nuevo: tests de nivel HTTP (`tests/web/…`) con `TestClient`/`httpx` (brief §12). Construir **test-first** con `/tdd`.

## Out of Scope

- **Vistas de staff** (`/packages` con modales, `/announce-new`) — el flujo con privilegios y su declaración de unidad son otra rebanada.
- **Autenticación** (OTP de clientes, password de staff) — `/announce` es vista **sin privilegios**; el cliente se registra implícitamente, sin login (brief §7). La invariante "auth siempre" aplica a las vistas que la requieren, no al anuncio público.
- **Notificaciones** (SMS/WhatsApp al anunciar) — rebanada de notificaciones; aquí solo se crea el Paquete.
- **`/search`, `/customer/verify`, `/help/terms/privacy/cookies`, header/footer definitivos** — rebanadas/piezas aparte (esta trae el mínimo de layout para que `/announce` funcione).
- **Escáner de guía** y captura de `guide_number` (es del staff al recibir).
- **Migrar las rutas/plantillas viejas en bloque** — se construye la ruta nueva; las viejas no se tocan.
- **S3 / subida de fotos** — fuera de alcance; la app nueva arranca sin AWS.

## Further Notes

- **Candidato a ADR:** la **capa web clean-room** (nuevo app bootstrap del rebuild, desacoplado del `config` viejo que exige AWS, reemplazando `main.py` incrementalmente) es una decisión estructural difícil de revertir y sorprendente sin contexto — vale un ADR vía `/domain-modeling` antes o durante `/to-tickets`.
- **Look & feel:** reutilizar el estilo de `src/templates/announce/*.html` como referencia visual; el brief §8 (header/footer) se aplica en su propia pieza.
- **Consumo aguas abajo:** esta rebanada abre la capa web; `/search`, `/packages` y las demás rutas cuelgan de este bootstrap y de este patrón de test HTTP.
- **Decisión abierta menor (elijo default):** la confirmación puede ser una **página propia** o un **redirect a un detalle**; propongo página de confirmación con el `tracking_number` (más simple), afinar en tickets.

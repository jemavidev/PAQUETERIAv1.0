# Spec — `/packages` (vista de staff: recibir · entregar · cancelar)

Status: ready-for-agent
Feature: packages-staff
Branch: PaqueteXv.2
Depende de: `package-lifecycle` (transiciones), `staff-auth` (`current_staff` = el actor), `announce-web` (capa web).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §7 · `CONTEXT.md` (Estados del Paquete, Contexto de entrega) · `PACKAGES_DIAGNOSIS.md` (modales/finally) · ADR-0001/0004

---

## Problem Statement

El staff no tiene **dónde operar** los paquetes. La máquina de estados (`recibir → entregar → cancelar`) existe en el dominio y ya hay un **actor de sesión** (`current_staff`), pero **no hay vista** que los una: el operador no puede ver la lista de paquetes ni ejecutar una acción desde el navegador. Es la vista **principal** del sistema con privilegios y hoy no existe en el rebuild. Además el sistema viejo arrastraba modales que **se quedaban bloqueados** y una columna de Guía/Código sin uso que estorbaba (`PACKAGES_DIAGNOSIS.md`, brief §7).

## Solution

`/packages`: la vista de staff (protegida por sesión) que **lista los paquetes con su estado** y permite ejecutar las tres acciones del ciclo de vida desde **modales unificados**, cada una registrando al operador de la sesión como **actor**:

- **Recibir** un paquete `Anunciado` → `Recibido`, capturando opcionalmente la **Guía** (entrada manual).
- **Entregar** un paquete `Recibido` → `Entregado`, mostrando el **destinatario snapshot** (nombre/apartamento congelados) para confirmar a quién se le entrega.
- **Cancelar** un paquete `Anunciado`/`Recibido` → `Cancelado`, con **motivo obligatorio** (dropdown) y aviso de irreversibilidad.

Sin columna de Guía/Código en la lista (sin uso). Mobile-first: modales como **bottom-sheet**. Los modales **nunca se quedan bloqueados**: el botón se re-habilita con `finally` pase lo que pase.

## User Stories

1. Como **staff**, quiero abrir `/packages` y ver la **lista de paquetes** con su estado, para saber qué hay pendiente.
2. Como **staff**, quiero que `/packages` **exija sesión** (me manda a login si no la tengo), para que la operación no quede expuesta.
3. Como **staff**, quiero ver en cada paquete su **destinatario** (nombre) y **estado** actual, para ubicarlo de un vistazo.
4. Como **staff**, quiero **no** ver una columna de Guía/Código en la lista, porque no se usa y estorba (brief §7).
5. Como **operador**, quiero **recibir** un paquete `Anunciado` desde un modal, para marcarlo presente en portería.
6. Como **operador**, quiero **capturar opcionalmente la Guía** del transportador al recibir (entrada manual), sin que sea obligatoria.
7. Como **operador**, quiero recibir **aunque no haya Guía**, porque no todos los transportadores la usan.
8. Como **operador**, quiero que al recibir quede registrado que **fui yo** (mi sesión) y **cuándo**, para trazabilidad.
9. Como **operador**, quiero que el sistema **rechace recibir** un paquete que no está `Anunciado`, con un mensaje claro y sin cambiar nada.
10. Como **operador**, quiero **entregar** un paquete `Recibido` desde un modal, para reflejar que el residente lo retiró.
11. Como **operador**, quiero que el modal Entregar **muestre el destinatario snapshot** (nombre + apartamento congelados al anunciar), para confirmar a quién entrego.
12. Como **operador**, quiero que al entregar quede registrado **quién** y **cuándo**.
13. Como **operador**, quiero que el sistema **rechace entregar** algo que no está `Recibido`, sin efecto.
14. Como **operador**, quiero **cancelar** un paquete con un **motivo obligatorio** (dropdown), para dejar trazabilidad de por qué se anuló.
15. Como **operador**, quiero que cancelar me **avise que es irreversible**, para no anular por error.
16. Como **operador**, quiero que **cancelar sin motivo** se rechace, para que nunca quede una cancelación sin razón.
17. Como **operador**, quiero que el sistema **rechace cancelar** un paquete ya `Entregado`/`Cancelado`, sin efecto.
18. Como **staff en móvil**, quiero que los modales sean **bottom-sheet** con botones grandes, para operar con el pulgar.
19. Como **staff**, quiero que los tres modales se vean y se comporten **igual** (título/botones/cierre consistentes), para no re-aprender cada uno.
20. Como **staff**, quiero que si una acción falla, el modal **no se quede bloqueado** (el botón se re-habilita), para reintentar (bug a no heredar).
21. Como **staff**, quiero volver a ver la lista **actualizada** tras una acción, para confirmar el nuevo estado.
22. Como **auditor**, quiero que el actor de cada transición venga **de la sesión verificada**, nunca de un id enviado por el cliente.
23. Como **operador**, quiero **escanear el código de barras** del paquete con la **cámara del celular** al recibir (multi-formato), para capturar la Guía sin teclearla ni instalar una app.
24. Como **operador**, quiero que si la cámara no está disponible o niego el permiso, el modal **caiga a entrada manual** de la Guía, para no quedar bloqueado.

## Implementation Decisions

### Rutas (capa web, gated por `current_staff`)

- **`GET /packages`**: vista protegida (dependencia `current_staff`) que **lista** los paquetes con su estado, destinatario y apartamento snapshot; **sin** columna de Guía/Código. Orden por `announced_at` desc (lo más reciente primero).
- **`POST /packages/{id}/receive`**: `guide_number` opcional del form → `receive(session, paquete, current_staff, guide_number)`.
- **`POST /packages/{id}/deliver`**: → `deliver(session, paquete, current_staff)`.
- **`POST /packages/{id}/cancel`**: `motivo` obligatorio (dropdown `MotivoCancelacion`) → `cancel(session, paquete, current_staff, motivo)`.
- Cada acción usa **`current_staff` como actor** (invariante "el actor sale de la sesión"). Tras la acción, **redirige a `/packages`** (patrón PRG) con la lista actualizada. Si el paquete no existe → 404.

### Manejo de transiciones inválidas

- `TransicionInvalida` (recibir/entregar/cancelar desde un estado no permitido) y `ValueError` (cancelar sin motivo) → se traducen a un **mensaje de error** para el staff y **no cambian** el paquete (el dominio ya valida antes de mutar). La lista se re-muestra con el aviso.

### Lectura para la lista

- Un **read** de paquetes para la vista (consulta directa o un pequeño helper de lectura). Devuelve lo necesario para pintar la fila: estado, `recipient_name`, apartamento snapshot, `announced_at`. La **paginación** se deja como mejora posterior (volumen residencial bajo; un límite razonable de entrada).

### UI — modales unificados (server-rendered + Alpine/HTMX)

- Un **componente de modal compartido** (mismo título/botones/cierre) parametrizado por acción; en móvil se presenta como **bottom-sheet**.
- **Recibir**: campo de Guía **opcional** (entrada manual) **+ escáner por cámara** (ver abajo). **Entregar**: muestra el **destinatario snapshot** (solo lectura) para confirmar; menos campos, botones grandes. **Cancelar**: **dropdown de motivo obligatorio** + aviso de irreversibilidad.
- JS del submit: deshabilita el botón y lo **re-habilita con `finally`** pase lo que pase (bug a no heredar, `PACKAGES_DIAGNOSIS.md`).

### Escáner de código de barras (ZXing) — captura de Guía por cámara

- Motor **ZXing** (`@zxing/browser` + `@zxing/library`) **vendorizado como asset estático** (bundle UMD/ESM en `/static`), **sin proceso Node en runtime** (brief §3, "liviano"). Se sirve desde la propia app (nada de CDN, portable).
- En el modal **Recibir**, un botón **"Escanear"** abre la **cámara** (`getUserMedia`); ZXing decodifica el **mayor abanico de símbolos** 1D/2D (Code128/39, EAN-8/13, UPC-A/E, ITF, Codabar, QR, DataMatrix, PDF417, Aztec, brief §3) y **rellena el campo `guide_number`**.
- **Degrada con gracia:** sin cámara o con permiso denegado, el campo sigue **editable manualmente** (nunca bloquea). `getUserMedia` exige **HTTPS** (Caddy ya lo da; en `localhost` el navegador lo permite).
- La Guía sigue siendo **opcional y de referencia**; el emparejamiento sigue por nombre/teléfono (no se promueve la guía a llave, brief §7).

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que la lista exige sesión y muestra el estado correcto; que una acción **transiciona** el paquete y **registra al actor de la sesión**; que las transiciones inválidas y el cancelar-sin-motivo se **rechazan sin efecto** — no el HTML exacto ni los internals.

**Costuras (ambas EXISTENTES):**
- **HTTP (Seam web):** `TestClient` (arnés `tests/web`), autenticando con un staff sembrado (patrón de `test_auth.py`). Casos: `GET /packages` sin sesión → redirige a login; con sesión → 200 y lista; `POST receive/deliver/cancel` → el paquete queda en el estado esperado con el **actor = el staff de la sesión** (verificado en `client.db`); recibir/entregar en estado inválido → rechazo sin efecto; cancelar sin motivo → rechazo sin efecto; el paquete inexistente → 404.
- **Dominio (Seam A):** ya cubierto por `package-lifecycle`; esta rebanada **no** re-testea la máquina de estados, solo su exposición HTTP y el cableado del actor.
- **Escáner ZXing (cámara):** el decode por cámara es **client-side** y **no** se cubre con `TestClient` (no hay cámara en CI). La cobertura automatizada se limita a: el **asset ZXing se sirve** (`GET /static/...` → 200) y el modal Recibir **incluye el disparador de escaneo**; el comportamiento servidor (recibir con `guide_number`) ya está cubierto por el ticket de Recibir. La ruta de cámara se verifica **manual/e2e**.

**Prior art:** `tests/web/test_announce.py` (rutas + `client.db`), `tests/web/test_auth.py` (login/sesión), `tests/data_model/test_recibir|entregar|cancelar_paquete.py` (comportamiento del dominio). Construir **test-first** con `/tdd`.

## Out of Scope

- **`/announce-new`** (anuncio por staff + declaración de unidad) — otra rebanada.
- **`/customers/manage`, `/admin`, `/search`** — vistas aparte.
- **Notificaciones** al recibir/entregar — rebanada de notificaciones.
- **Paginación / filtros avanzados** de la lista — mejora posterior (volumen bajo).
- **Log de eventos / timeline** por paquete — rebanada aparte.
- **Máquina de estados** en sí (ya implementada) — aquí solo su superficie HTTP.

## Further Notes

- **Actor de sesión:** las acciones toman el `Usuario` de `current_staff`; nunca un `usuario_id` del cliente — cierra el invariante del brief §14 en la capa HTTP.
- **PRG (Post/Redirect/Get):** las acciones redirigen a `/packages` para evitar reenvíos por recarga; alternativa HTMX (swap de la fila) es una mejora, no un requisito.
- **Modal compartido:** el brief §7 pide unificarlos; el componente compartido es la pieza que `/announce-new` y otras vistas reutilizarán.
- **Follow-ups heredados** que tocan esta vista: **CSRF** en los POST de acción (mismo pendiente que auth), y el **build de Tailwind** del design-system para el look definitivo.
- **Consumo aguas abajo:** el componente de modal y el patrón de acción-gated-por-`current_staff` los reutilizan `/announce-new`, `/customers/manage` y `/admin`.

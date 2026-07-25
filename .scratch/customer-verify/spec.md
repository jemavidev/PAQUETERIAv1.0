# Spec — `/customer/verify` (tablero de autoedición del cliente)

Status: ready-for-agent
Feature: customer-verify
Branch: PaqueteXv.2
Depende de: `customer-otp-auth` (`current_customer`), `data-model` (Persona/Apartamento, `declare_unit`, `get_or_create_apartamento`).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §6.4/§7 · `CONTEXT.md` (Persona, Apartamento actual, Herencia de apartamento) · ADR-0004

---

## Problem Statement

El residente que ya verificó su teléfono (OTP) no tiene dónde **completar ni corregir sus datos**: nombre, email, documento, segundo contacto, ni su **Apartamento**. `current_customer` ya identifica a la Persona de la sesión, pero no existe ninguna vista que la use. El brief (§7) pide un "tablero de autoedición… el formulario completo de Residencia + contacto secundario", y es uno de los dos lugares (junto a `/announce-new`, staff) donde el cliente **declara su unidad a propósito** — el acto que dispara la herencia de apartamento (§6.4).

## Solution

`/customer/verify`: vista **protegida por `current_customer`** donde el residente ve y edita sus datos (nombre, email, documento/tipo, segundo contacto) y **declara su Apartamento** (Conjunto/Torre/Apartamento, creable sobre la marcha) — lo que lo une al grupo "misma unidad" de ese apartamento vía el `declare_unit` ya existente. Server-rendered, mobile-first, sin mutaciones de dominio nuevas más allá de un mutador simple de datos personales (`declare_unit`/`get_or_create_apartamento` ya existen y se reutilizan sin cambios).

## User Stories

1. Como **residente verificado**, quiero abrir `/customer/verify` y ver **mis datos actuales**, para saber qué falta completar.
2. Como **residente**, quiero **editar mi nombre**, para corregirlo si quedó mal al anunciar.
3. Como **residente**, quiero agregar/editar mi **email**, para ampliar mi registro.
4. Como **residente**, quiero agregar/editar mi **documento** (tipo + número), para ampliar mi registro.
5. Como **residente**, quiero agregar/editar un **segundo contacto**, para tener un respaldo.
6. Como **residente sin sesión**, quiero que `/customer/verify` me **exija verificar mi teléfono** (OTP) antes de dejarme editar, para que solo yo pueda tocar mis datos.
7. Como **residente**, quiero **declarar mi Apartamento** (Conjunto/Torre/Apartamento) desde este formulario, para que mis paquetes futuros salgan a mi unidad.
8. Como **residente**, quiero que si el Apartamento que escribo **ya existe**, se **reutilice** (no se duplique), consistente con el resto del sistema.
9. Como **residente**, quiero que **declarar mi Apartamento** desde aquí sea la forma de **unirme deliberadamente** a esa unidad (§6.4) — no un "a nombre de" casual — para que la herencia sea intencional.
10. Como **residente que ya tenía Apartamento**, quiero poder **cambiarlo** (mudarme) desde aquí, reflejando que me mudé.
11. Como **residente**, quiero que guardar mis datos **no afecte** el snapshot de paquetes que ya anuncié (inmutabilidad, ADR-0001) — solo mi perfil hacia adelante.
12. Como **residente**, quiero que un envío con datos inválidos (p.ej. email mal formado) se **rechace con mensaje claro**, sin perder lo que ya llené.
13. Como **residente**, quiero ver confirmación de que mis cambios se **guardaron**, para saber que no se perdieron.
14. Como **residente**, quiero **cerrar sesión** desde esta misma vista, para no tener que ir a otra pantalla.
15. Como **desarrollador**, quiero que esta vista **no reintroduzca** los bugs del `/customer/verify` viejo (rebuild clean-room, ADR-0004) — al no extender el código anterior, no los hereda por construcción.

## Implementation Decisions

### Nuevo en dominio (mínimo — todo lo demás se reutiliza)

- `update_datos_personales(session, persona, *, nombre=None, email=None, documento=None, tipo_documento=None, segundo_contacto=None) -> Persona`: actualiza **solo** los campos pasados (los `None` no tocan el valor existente — permite guardar parcialmente); **no** valida reglas de negocio complejas, solo tipo/forma básica (p.ej. email con `@`, si se manda). Vive en `persona_service.py` junto a `get_or_create_persona`.
- **Sin cambios de esquema.** Los campos ya existen en `Persona` (data-model). Sin migración.
- **Declarar el Apartamento reutiliza servicios existentes, sin tocarlos**: `get_or_create_apartamento(conjunto, torre, apartamento)` + `declare_unit(apartamento, [(persona.telefono, persona.nombre)])` — pasar **un solo miembro** (el propio cliente) es la forma correcta de "declarar a propósito" desde esta vista; no agrupa a nadie más que a sí mismo (nadie más se ve afectado), y si el Apartamento ya tenía otras Personas, el cliente se une a ese grupo emergente sin tocarlas.

### Ruta (capa web — protegida por `current_customer`)

- **`GET /customer/verify`**: requiere `current_customer` (sin sesión → redirige a `/auth/customer/login`, ya cableado por el handler 401 existente). Muestra el formulario prellenado con los datos actuales de la Persona (incluido su Apartamento actual, si tiene).
- **`POST /customer/verify`**: valida forma básica; llama a `update_datos_personales(...)`; si vienen Conjunto/Torre/Apartamento, llama a `get_or_create_apartamento` + `declare_unit` con el propio teléfono; **PRG** de vuelta a `/customer/verify` con mensaje de éxito.
- Los campos de Apartamento son **opcionales en el POST** (el residente puede guardar solo datos personales sin tocar su unidad).

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que la vista exige sesión de cliente; que guardar persiste los campos correctos en `client.db`; que declarar Apartamento reutiliza uno existente y no afecta a otras Personas del mismo Apartamento; que el snapshot de paquetes ya anunciados no cambia — no el HTML exacto.

**Costuras (ambas EXISTENTES):**
- **HTTP (Seam web):** `TestClient`, autenticando como cliente (patrón de `tests/web/test_customer_auth.py`: pedir+verificar OTP para obtener sesión). Casos: sin sesión → redirige a `/auth/customer/login`; con sesión → 200, formulario prellenado; `POST` guarda nombre/email/documento/segundo_contacto (parcial, sin borrar lo no enviado); `POST` con Apartamento nuevo lo crea y lo asigna; `POST` con Apartamento existente lo **reutiliza** (no duplica) y no afecta a otras Personas ya en él; email inválido → error, sin persistir cambios inválidos; un paquete anunciado antes de mudarse conserva su snapshot tras el cambio de Apartamento (invariante ADR-0001, mismo patrón que `test_mudanza_desvinculacion.py`).
- **Dominio (Seam A):** `update_datos_personales` — actualización parcial (campos no enviados no se tocan); validación básica de email.

**Prior art:** `tests/web/test_customer_auth.py` (sesión de cliente), `tests/web/test_packages.py`/`test_announce.py` (patrón de forms + `client.db`), `tests/data_model/test_mudanza_desvinculacion.py` (inmutabilidad del snapshot). Construir **test-first** con `/tdd`.

## Out of Scope

- **Segundo contacto como entidad propia** — es un campo de texto en `Persona` (ya existe), no una Persona aparte.
- **`/announce-new`** (la otra vía de declarar unidad, staff) — rebanada aparte.
- **Notificaciones de cambio de datos** — fuera de alcance.
- **Historial de cambios/auditoría de edición de perfil** — no existe en el modelo (data-model no incluyó historial de membresía por decisión explícita, spec §Further Notes) y no se agrega aquí.
- **Fusión de "nombre sin teléfono" a Persona real** (spec §15.2 del brief, cabo pendiente) — sigue diferido.

## Further Notes

- **Reutilización, no invención:** esta rebanada añade **una sola función de dominio** (`update_datos_personales`); todo lo demás (Persona, Apartamento, `declare_unit`, `current_customer`) ya existe. Es deliberadamente pequeña.
- **`declare_unit` con un solo miembro** es la pieza de diseño más sutil de esta spec — vale la pena que el review confirme que de verdad no muta a nadie más del apartamento (ya lo garantiza la implementación actual, pero el test debe probarlo explícitamente aquí, en el contexto de esta vista).
- **Bugs viejos:** no se encontró una lista específica de bugs de `/customer/verify` en los docs de refactor disponibles; al ser un rebuild clean-room (ADR-0004, no se extiende `customer_preferences*.py` viejo), no se heredan por construcción.
- **Consumo aguas abajo:** cierra el arco completo de `customer-otp-auth` — la sesión de cliente ahora tiene una vista real que la usa.

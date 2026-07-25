# Spec — `/customers/manage` (buscar · editar · eliminar cliente, staff)

Status: ready-for-agent
Feature: customers-manage
Branch: PaqueteXv.2
Depende de: `data-model` (Persona, `update_datos_personales`, `move_resident`), `staff-auth` (`current_staff`, `require_admin`).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §7 · ADR-0005 (eliminar Persona = anonimización) · ADR-0001 (snapshot inmutable) · ADR-0003 (Teléfono llave universal)

---

## Problem Statement

El staff no tiene dónde **gestionar clientes existentes**: buscar a un residente, corregir sus datos, o **eliminarlo** cuando lo pide (derecho a ser olvidado, o simplemente un dato mal cargado). El brief (§7) acota `/customers/manage` a: "buscar clientes, ver/editar info personal, gestión de notificaciones, eliminar cliente". Antes de escribir esta spec confirmé un hecho técnico que decide gran parte del diseño: **`paquetes.announced_by_persona_id` es una FK real y `NOT NULL`** — cualquier Persona que anunció un Paquete **no puede borrarse de verdad** sin romper esa referencia o destruir historia (contra ADR-0001). Por eso "eliminar" se resuelve como **anonimización** (ADR-0005, escrito antes de esta spec), no como un `DELETE`.

## Solution

`/customers/manage`: vista de staff con tres capacidades acotadas:

- **Buscar** clientes por teléfono o nombre.
- **Ver/editar** los datos personales de un cliente (reutiliza `update_datos_personales`, sin cambios — mismo patrón que `/customer/verify` pero operado por staff sobre la Persona de otro).
- **Eliminar** (anonimizar) un cliente — gated por `require_admin` (acción destructiva/irreversible-en-la-práctica, mismo criterio que justificó `require_admin` en `admin-staff`), a diferencia de buscar/editar que cualquier staff puede hacer.

**"Gestión de notificaciones" queda fuera de esta spec** — el modelo actual no tiene ningún concepto de preferencia/opt-out de notificaciones (la rebanada `package-notifications` no construyó eso; solo el envío del mensaje). Inventar esa pieza aquí sería colar una segunda decisión especulativa dentro de esta misma spec; merece su propio `/to-spec` cuando se aborde.

## User Stories

1. Como **staff**, quiero **buscar un cliente** por teléfono o nombre, para encontrarlo sin conocer su id.
2. Como **staff**, quiero ver los **datos actuales** de un cliente encontrado (nombre, email, documento, segundo contacto, apartamento), para revisar su ficha.
3. Como **staff**, quiero **editar** esos datos (mismo formulario/reglas que `/customer/verify`), para corregir información a pedido del residente.
4. Como **staff (cualquier rol)**, quiero acceder a **buscar/ver/editar** sin necesitar privilegios de administrador — es una tarea operativa rutinaria.
5. Como **ADMIN**, quiero **eliminar (anonimizar)** un cliente, para atender una solicitud de borrado.
6. Como **operador (no admin)**, quiero que **eliminar** me sea rechazado (403) — es una acción destructiva, reservada a ADMIN.
7. Como **ADMIN**, quiero que eliminar **anonimice** los datos personales (nombre, email, documento, segundo contacto) y **reemplace el teléfono** por un valor no reutilizable, para que la identidad deje de ser buscable/operable — sin romper el historial de paquetes que esa Persona anunció.
8. Como **ADMIN**, quiero que eliminar **desvincule** al cliente de su Apartamento, para que no siga apareciendo agrupado con sus antiguos convivientes.
9. Como **residente que vuelve a anunciar** con su número real **después** de que su identidad anterior fue anonimizada, quiero que el sistema me trate como una **Persona nueva** (mi número real ya no apunta a la identidad anonimizada), para que "olvidar" sea real y no cosmético.
10. Como **cualquiera**, quiero que los **snapshots de paquetes ya anunciados** por un cliente eliminado **no cambien** (siguen mostrando el nombre/teléfono de entonces), coherente con ADR-0001.
11. Como **ADMIN**, quiero una **confirmación explícita** antes de eliminar (acción irreversible en la práctica), para no anonimizar por error.
12. Como **staff sin sesión**, quiero ser **redirigido a `/auth/login`**.

## Implementation Decisions

### Dominio — una función nueva (`anonimizar_persona`) + reutilización

- **Migración `0007`** (descendiente de `0006`, raíz única ADR-0002): añade `eliminado_en` (timestamp, nullable) a `personas`. Constraint/columna con nombre coherente con el patrón existente; guard de paridad esquema↔ORM la cubre.
- **`anonimizar_persona(session, persona) -> Persona`** (nuevo, en `persona_service.py`, junto a `update_datos_personales`): desvincula del Apartamento (reutiliza `move_resident(session, persona.telefono, None)` **antes** de tocar el teléfono); limpia `nombre` a un placeholder fijo ("Cliente eliminado"), `email`/`documento`/`tipo_documento`/`segundo_contacto` a `NULL`; **reemplaza `telefono`** por un valor sintético único no enrutable (p.ej. prefijo reservado + UUID, garantiza no colisionar con un teléfono real ni con otra anonimización); marca `eliminado_en = ahora`. Si `persona.eliminado_en` ya está seteado, es un **no-op idempotente** (eliminar dos veces no falla ni duplica trabajo).
- **Sin cambios** en `update_datos_personales`/`move_resident` — se reutilizan tal cual (mismo patrón que `admin-staff`/`announce-new`: cero reinvención de dominio ya probado).

### Ruta (capa web)

- **`GET /customers/manage`** gated por `current_staff` (cualquier rol): formulario de búsqueda (teléfono o nombre) + resultados (lista de Personas que coinciden).
- **`GET /customers/manage/{persona_id}`** gated por `current_staff`: ficha del cliente con formulario de edición (mismos campos que `/customer/verify`, sin la parte de declarar Apartamento — eso es `/announce-new`/`/customer/verify`, no se duplica aquí) + botón "Eliminar" (visible solo si el `staff` actual tiene rol ADMIN — la ruta de acción igual se protege con `require_admin` server-side, la UI no es la única barrera).
- **`POST /customers/manage/{persona_id}`**: guarda cambios vía `update_datos_personales` (mismas reglas: parcial, email inválido rechaza todo el request).
- **`POST /customers/manage/{persona_id}/delete`** gated por **`require_admin`**: llama `anonimizar_persona`; confirmación explícita en la UI (paso de "¿seguro?" antes de enviar, mismo espíritu que el aviso de irreversibilidad de Cancelar en `/packages`); tras éxito, redirige a `/customers/manage` con mensaje de confirmación.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable** — que buscar encuentra al cliente correcto; que editar guarda parcialmente (ya probado el patrón en `customer-verify`, aquí solo se confirma que el staff puede operar sobre la Persona de OTRO, no la suya); que eliminar **anonimiza sin romper** el historial de paquetes ya anunciados y **desvincula** del Apartamento; que un operador no-admin es rechazado al eliminar; que un teléfono real reutilizado tras la anonimización crea una **Persona nueva**.

**Costuras (ambas EXISTENTES):**
- **Dominio (Seam A):** `anonimizar_persona` — limpia los campos correctos; el teléfono queda sintético y único; `apartamento_actual_id` queda `NULL`; llamar dos veces es un no-op seguro; el snapshot de un Paquete ya anunciado por esa Persona **no cambia** tras anonimizar (mismo patrón que `test_mudanza_desvinculacion.py`); anunciar de nuevo con el teléfono real original (tras la anonimización) crea una Persona **distinta** (verifica que el teléfono viejo ya no resuelve a la identidad anonimizada).
- **HTTP (Seam web):** `TestClient`, sesión de staff (patrón `test_packages.py`/`test_admin_staff.py`). Casos: buscar por teléfono/nombre devuelve al cliente correcto; operador edita datos de otra Persona con éxito; operador intentando `/delete` → 403; admin eliminando → 200/redirect + Persona anonimizada verificada en `client.db`; sin sesión → redirige.

**Prior art:** `tests/data_model/test_persona_service.py`/`test_mudanza_desvinculacion.py` (invariantes de dominio reutilizados), `tests/web/test_customer_verify.py` (patrón de edición parcial), `tests/web/test_admin_staff.py` (gate `require_admin` sobre una acción destructiva). Construir **test-first** con `/tdd`.

## Out of Scope

- **"Gestión de notificaciones"** (preferencias/opt-out) — no existe ese concepto en el modelo; requiere su propia spec de dominio (qué es una preferencia, cómo se relaciona con `package-notifications`). Explícitamente diferido.
- **Deshacer una anonimización** — no existe (ni debería existir fácilmente: sería re-identificar a alguien que pidió ser olvidado). Fuera de alcance por diseño, no por omisión.
- **Notificar al cliente** que fue eliminado — fuera de alcance (además, su teléfono real ya no está asociado a la Persona anonimizada).
- **Paginación de resultados de búsqueda** — mejora posterior, volumen bajo (mismo criterio que `/search`).
- **Auditoría/log de quién eliminó a quién** — no existe log de eventos en el rebuild (mismo criterio que `search-web`); se limita a lo que ya registra la sesión de staff.

## Further Notes

- **ADR-0005 escrito antes que esta spec** (no al revés): la restricción técnica real (FK `NOT NULL`) se descubrió primero y **decidió** el diseño de "eliminar", en vez de que el diseño de la spec inventara una política y luego chocara con el esquema.
- **Separación de gates** (cualquier staff para buscar/editar, solo ADMIN para eliminar) sigue el mismo criterio que `admin-staff`: una acción destructiva/irreversible-en-la-práctica merece el gate más estricto.
- **Consumo aguas abajo:** ninguna otra rebanada depende de ésta.

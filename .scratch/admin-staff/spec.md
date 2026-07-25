# Spec — `/admin` (alta de cuentas de staff)

Status: ready-for-agent
Feature: admin-staff
Branch: PaqueteXv.2
Depende de: `staff-auth` (`create_staff`, `require_admin` — ya existen y están probados en Seam A).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §7/§9 · `CONTEXT.md` (Usuario, "Solo un ADMIN crea cuentas de staff") · ADR-0004

---

## Problem Statement

**Un ADMIN real, usando el sistema en producción, no puede dar de alta a un operador.** `create_staff(actor, email, nombre, password, rol)` existe en dominio y está probado (Seam A: solo un ADMIN puede llamarlo, email único, contraseña fuerte) — pero **ninguna ruta HTTP lo expone**. La única forma de crear un `Usuario` de staff hoy es `create_initial_admin`, el bootstrap operativo sin actor (pensado para el arranque, no para uso continuo). El sistema tiene un candado (`create_staff` exige `actor.rol == ADMIN`) sin puerta que lo use — es una capacidad construida pero inalcanzable desde fuera de los tests.

## Solution

`/admin/staff`: vista **protegida por `require_admin`** donde un administrador **da de alta** una cuenta de staff (email, nombre, contraseña, rol ADMIN/OPERADOR), reutilizando `create_staff` **sin cambios** en dominio. Sin lista de staff existente ni edición/borrado en esta rebanada — **solo crear**, que es la brecha real.

## User Stories

1. Como **ADMIN**, quiero abrir `/admin/staff` y ver un formulario de alta, para dar de alta un operador.
2. Como **ADMIN**, quiero completar **email, nombre, contraseña y rol** (ADMIN/OPERADOR), para crear la cuenta.
3. Como **ADMIN**, quiero ver una **confirmación** cuando la cuenta se crea, para saber que quedó lista.
4. Como **operador (no admin)**, quiero que `/admin/staff` me **rechace** (403), para que no pueda escalar privilegios ni crear cuentas.
5. Como **cualquiera sin sesión de staff**, quiero que `/admin/staff` me **redirija a `/auth/login`**, para no exponer la administración a quien no tiene sesión.
6. Como **ADMIN**, quiero que un **email duplicado** se rechace con un mensaje claro, sin crear una cuenta a medias.
7. Como **ADMIN**, quiero que una **contraseña débil** se rechace con un mensaje claro (misma política que ya exige `create_staff`).
8. Como **ADMIN**, quiero que **campos vacíos** (email/nombre/contraseña) se rechacen antes de llegar al dominio, con un mensaje claro.
9. Como **desarrollador**, quiero que esta vista **reutilice `create_staff` sin tocarlo** — la regla de negocio (solo ADMIN, email único, contraseña fuerte) ya vive en dominio y está probada; la vista solo la expone.
10. Como **ADMIN**, quiero que el **actor de la creación sea mi sesión** (`current_staff`/`require_admin`), nunca un campo del formulario, para que la trazabilidad de quién creó a quién sea confiable.

## Implementation Decisions

### Ruta (capa web — gated por `require_admin`)

- **`GET /admin/staff`**: formulario (email, nombre, contraseña, selector de rol ADMIN/OPERADOR). Sin sesión → redirige a `/auth/login` (ya cableado, prefijo staff); con sesión de OPERADOR → **403** (`require_admin`, ya existente); con sesión de ADMIN → 200.
- **`POST /admin/staff`**: valida presencia básica (email/nombre/contraseña no vacíos) **antes** de llamar a dominio; llama `create_staff(db, actor=current_admin, email, nombre, password, rol)`; éxito → confirmación (PRG con mensaje). `PermissionError`/`ValueError` de `create_staff` → re-render con mensaje, **sin** crear nada (ya es atómico por diseño de `create_staff` — no hace falta rollback manual, la función valida antes de mutar).
- **Sin cambios en dominio.** `create_staff`/`RolUsuario` se reutilizan tal cual (ya construidos y probados en `staff-auth`).
- La ruta placeholder `/auth/admin/check` (creada como prueba mínima de `require_admin` en `staff-auth`) queda **obsoleta** — esta rebanada es su reemplazo real; se puede retirar como limpieza (no rompe nada, no la consume ninguna otra vista).

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que el gate `require_admin` funciona (403 para operador, redirect sin sesión), que un alta válida crea la cuenta con los datos correctos, y que los rechazos de dominio (duplicado, contraseña débil) no crean nada — no reinventar los tests de `create_staff` ya escritos en `test_staff_service.py` (esos ya cubren la regla de negocio; aquí solo se prueba el cableado HTTP).

**Costura (EXISTENTE, ninguna nueva):** **HTTP con `TestClient`**, sesión de ADMIN vía `create_initial_admin` + `/auth/login` (patrón de `test_packages.py`). Casos: sin sesión → redirige; con sesión de OPERADOR → 403; con sesión de ADMIN → 200 en GET; `POST` válido crea el `Usuario` (verificado en `client.db`) y muestra confirmación; email duplicado → error, sin segunda cuenta creada; contraseña débil → error, sin cuenta creada; campos vacíos → error antes de llamar a dominio.

**Prior art:** `tests/data_model/test_staff_service.py` (la regla de negocio, no se re-testea aquí), `tests/web/test_packages.py`/`test_auth.py` (patrón de sesión + gate + `client.db`). Construir **test-first** con `/tdd`.

## Out of Scope

- **Lista/edición/borrado de staff** — esta rebanada es **solo alta**. Ver/editar cuentas existentes es una extensión natural, no incluida.
- **Plantillas de notificación** y **gestión de residencias** (el resto de `/admin` según brief §7) — rebanadas aparte.
- **Recuperación de contraseña de staff** — no existe (`/auth/forgot-password`), fuera de alcance.
- **MFA** — mencionado como opcional a futuro en el brief, no aquí.
- **`/customers/manage`** — vista de cliente aparte, no se toca.

## Further Notes

- **Reutilización total del dominio**: esta rebanada no añade nada a `app/domain/` — es exactamente el patrón "construimos el candado en `staff-auth`, aquí construimos la puerta". Vale la pena notarlo porque contrasta con rebanadas anteriores que sí añadían una función de dominio pequeña (`customer-verify` añadió una; ésta no añade ninguna).
- **Limpieza menor**: retirar `/auth/admin/check` (placeholder) puede hacerse en el mismo ticket sin riesgo, ya que nada más lo referencia.
- **Consumo aguas abajo:** una vez exista `/admin/staff`, el flujo real de "el dueño crea el primer ADMIN por bootstrap, y ese ADMIN da de alta a los operadores desde la app" queda completo de punta a punta — hoy ese segundo paso no existía.

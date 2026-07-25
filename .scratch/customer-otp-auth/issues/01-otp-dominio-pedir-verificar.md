# 01 — OTP de cliente: pedir + verificar (dominio)

**Spec:** `.scratch/customer-otp-auth/spec.md` · **Glosario:** Persona, Teléfono · **ADR:** 0002 (Alembic raíz única)

**What to build:** Un residente puede **pedir un código OTP** a su teléfono y **verificarlo**: si es correcto, no expiró y no agotó intentos, el sistema **crea o reutiliza su Persona** (por teléfono, igual que `announce`). Todo en la capa de dominio, sin HTTP, sin envío real de SMS (puerto reemplazable).

**Blocked by:** None — `Persona`/`get_or_create_persona` (data-model) ya está.

**Status:** done · 149 tests verdes

- [x] Migración `0006` **descendiente de `0005`** (raíz única, ADR-0002) que crea `otps_cliente`: `telefono` (canónico, indexado, **no único**), `codigo_hash`, `intentos` (default 0), `max_intentos`, `expira_en`, `verificado_en` (nullable), `created_at`. Constraints con **nombre explícito**; guard de paridad esquema↔ORM cubre la tabla; `alembic heads` = 1.
- [x] **Puerto `OtpSender`** (interfaz mínima `enviar(telefono, codigo)`) + una implementación de **desarrollo/test** que captura el código sin red (sin SMS real — eso es la rebanada de notificaciones).
- [x] `request_otp(session, telefono, sender)`: normaliza el teléfono; genera un código de **6 dígitos** criptográficamente aleatorio; lo **hashea** (nunca en claro) y persiste con `expira_en` (~5 min); invoca `sender.enviar(...)` con el código en claro.
- [x] `verify_otp(session, telefono, codigo) -> Persona`: busca el OTP **vigente** (no verificado, no expirado, `intentos < max_intentos`) más reciente para ese teléfono; código correcto → marca `verificado_en` y hace **get-or-create** de la Persona; código incorrecto → incrementa `intentos` y lanza `ValueError` **genérico** ("código inválido o expirado"), sin distinguir causa.
- [x] **Expirado** → rechazado igual que incorrecto (mismo mensaje genérico). **Intentos agotados** → rechazado aunque el código sea correcto.
- [x] **No reutilizable**: verificar dos veces el mismo código → la segunda falla.
- [x] Tests (Seam A, arnés compartido, con el `OtpSender` de test): pedir genera un registro con `codigo_hash` (no el código en claro); verificar correcto crea/reutiliza Persona y marca `verificado_en`; incorrecto → `ValueError` sin sesión; expirado → rechazado; tras `max_intentos` fallidos → rechazado; reutilizar el mismo código verificado → falla.

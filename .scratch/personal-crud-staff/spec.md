# Spec — Personal: CRUD completo de cuentas de staff (Grupo 18, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 18.

## Qué cambia

- Nueva columna `usuarios.activo` (migración `0015`, `NOT NULL DEFAULT true`
  — todo el staff existente queda activo, sin backfill manual).
- `verify_credentials` rechaza también una cuenta con `activo=False`, con el
  mismo mensaje genérico que email inexistente/contraseña mala (no revela
  que la cuenta existe pero está desactivada).
- Nuevas funciones en `staff_service.py`: `listar_staff`, `editar_staff`
  (nombre/rol), `resetear_password`, `set_activo_staff` — las tres últimas
  exigen `actor` `ADMIN` (mismo patrón que `create_staff`).
- Reglas de auto-protección: un `ADMIN` no puede degradarse a sí mismo a
  `OPERADOR` (`editar_staff`) ni desactivarse a sí mismo
  (`set_activo_staff`) — evita dejar el sistema sin ningún admin activo.
- `/administracion/personal` gana una tabla de cuentas existentes arriba del
  formulario de alta, con acciones por fila (modales reutilizando
  `packages/_modal.html`): Editar, Resetear contraseña, Activar/Desactivar.
  Nuevas rutas: `POST /administracion/personal/{id}/editar`,
  `.../resetear-password`, `.../activar`, `.../desactivar`.

## Por qué

**Desactivar, nunca borrar** (AgentX, por consistencia con el patrón de
anonimización de clientes, ADR-0005): las FK de actor de `Paquete`
(`received_by_usuario_id`, etc., y la auditoría visible del Grupo 11)
dependen de que el `Usuario` siga existiendo — borrar una fila real
rompería esas referencias o la auditoría histórica.

La regla de auto-protección (`ADMIN` no puede desactivarse/degradarse a sí
mismo) es una decisión de sentido común de AgentX, no pedida explícitamente
pero anotada como default en el intake — el usuario no objetó.

## Fuera de alcance

- No se agrega recuperación de contraseña por email (el reset es siempre
  una acción de un `ADMIN` sobre otra cuenta, no un flujo de autoservicio).

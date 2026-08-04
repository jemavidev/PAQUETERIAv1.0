# 10 — Staff gestiona Ocupantes sin restricción desde `/residentes/{id}`

**What to build:** extender `/residentes/{id}` (hoy solo LISTA los Ocupantes del apartamento, de solo lectura, vía `customers_manage.listar_ocupantes`) para que el staff (`ADMIN` u `OPERADOR`, sin diferencia entre roles — mismo patrón que el resto de esta vista) pueda hacer las mismas acciones que el principal tiene en el ticket 03: crear, asociar teléfono, desvincular teléfono, dar de baja, y promover (ticket 04) — reusando exactamente las mismas funciones de dominio, sin duplicar lógica.

**Nota de alcance (asunción a confirmar con el cliente si no calza):** este ticket asume que el límite de 5 Ocupantes activos por apartamento (ticket 03) **también aplica al staff** — el spec dice "el staff podrá realizar cualquiera de estas modificaciones sin restricción", que se interpreta como "sin restricción de PERMISOS" (puede hacer todo lo que el principal hace y más), no como "sin el límite numérico de 5", que es una regla de negocio del Apartamento, no un permiso de quién la ejecuta.

**Blocked by:** 03

**Status:** done

- [x] Staff puede crear, asociar teléfono, desvincular teléfono, dar de baja y promover Ocupantes desde `/residentes/{id}`.
- [x] La UI refleja el estado real (activos vs dados de baja, quién es el principal) — reusa `_ocupantes_de` (ya excluye dados de baja por defecto, vía `listar_ocupantes`).
- [x] Ambos roles de staff (`ADMIN`, `OPERADOR`) tienen acceso igual — las rutas nuevas usan `current_staff`, igual que el resto de esta vista (sin `require_admin`).
- [x] Tests cubren cada acción disponible para staff (crear con/sin teléfono, asociar, desvincular, dar de baja, promover).
- [x] Confirmado: el límite de 5 SÍ aplica también al staff (asunción del ticket, sin objeción — `agregar_ocupante` no distingue quién lo llama).

## Implementación

- `customers_manage.py`: `_contexto_detalle`/`_render_detalle_con_error` (refactor, mismo patrón que `customer_verify.py`) + 5 rutas nuevas bajo `/residentes/{persona_id}/ocupantes...`, todas con `current_staff` (sin chequeo de "es principal" — el staff no lo necesita).
- `customers_manage/detail.html`: la tarjeta "Ocupantes de la unidad" pasa de solo-lista a gestión completa (mismo patrón visual que `/mis-datos`).
- 5 tests nuevos en `test_customers_manage.py`. Suite completa: 512 passed.

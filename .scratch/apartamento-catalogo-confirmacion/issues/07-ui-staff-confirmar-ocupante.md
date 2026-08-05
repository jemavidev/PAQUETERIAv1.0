# 07 — UI staff: confirmar/rechazar Ocupantes pendientes en `/residentes/{id}`

**What to build:** la tarjeta de gestión de Ocupantes en `/residentes/{id}` (ya construida, ticket 10 de `.scratch/mis-datos/`) muestra el estado pending/confirmado de cada Ocupante y agrega acciones "Confirmar"/"Rechazar" para los pending, disponibles a cualquier miembro de staff (`ADMIN`/`OPERADOR`, mismo patrón sin distinción que el resto de esa vista). Reusa `confirmar_ocupante` (ticket 06) y `dar_de_baja_ocupante` (ya existente) para rechazar.

**Blocked by:** 06.

**Status:** done

- [x] Cada Ocupante listado muestra si está pending o confirmado (badge ámbar "Pendiente de confirmar" / verde "Confirmado" / azul "Principal").
- [x] Staff puede confirmar un pending — incluido el primero de un apartamento vacío (lo promueve a principal en el mismo acto, ya cubierto por el dominio del ticket 06).
- [x] Staff puede rechazar un pending — reusa la ruta de "baja" ya existente (sin ruta nueva; el botón dice "Rechazar" en vez de "Dar de baja" cuando el Ocupante está pending).
- [x] Ambos roles de staff (`ADMIN`, `OPERADOR`) tienen acceso igual — mismo patrón que el resto de `/residentes/{id}` (`current_staff`, sin `require_admin`).
- [x] Tests web en `test_customers_manage.py` cubren confirmar (primero y no-primero), rechazar, y el badge en la ficha.

## Implementación

- **Web:** ruta nueva `POST /residentes/{persona_id}/ocupantes/{ocupante_id}/confirmar` en `customers_manage.py`, mismo patrón que las demás acciones de esta vista (`current_staff`, sin restricción de rol). No hizo falta una ruta nueva de "rechazar" — la ruta `/baja` ya existente (`dar_de_baja_ocupante`) ya cubre exactamente ese caso desde el ticket 06 (un pending rechazado queda con `confirmado_en` en `NULL` para siempre).
- **Template:** `customers_manage/detail.html` — badge de 3 estados (Principal / Confirmado / Pendiente de confirmar) + botón "Confirmar" visible solo si `not o.confirmado_en`; el botón de baja cambia su texto a "Rechazar" cuando el Ocupante todavía no se confirmó.
- **Tests:** 4 nuevos (confirmar al primero y promoción a principal, confirmar a un segundo sin tocar al principal, rechazar un pending vía la ruta de baja existente, badge visible en la ficha).
- **Suite completa:** verde salvo los 6 fallos preexistentes de `test_layout.py`.

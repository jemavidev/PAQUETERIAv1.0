# 06 — Dominio: confirmación de Ocupante (`confirmado_en` + `confirmar_ocupante`)

**What to build:** columna nueva `Ocupante.confirmado_en` (DateTime nullable, mismo patrón que `desvinculado_en`: `NULL` = pending). `ocupante_service.agregar_ocupante` deja de marcar `es_principal=True` para el primer Ocupante de un apartamento vacío — todo Ocupante nuevo nace `pending` (`confirmado_en=None`, `es_principal=False`), sin excepción. Función nueva `confirmar_ocupante(session, ocupante, actor)`: válida solo si `actor` es el Ocupante principal ya confirmado del mismo apartamento, o un `Usuario` de staff (`ADMIN`/`OPERADOR`, sin distinción); marca `confirmado_en`; si el apartamento no tiene ningún principal todavía, promueve a este Ocupante a principal en la misma operación. Rechazar un pending reutiliza `dar_de_baja_ocupante` tal cual existe — sin función nueva para eso.

**Blocked by:** Ninguno — independiente del catálogo cerrado (tickets 01-05), puede empezar en paralelo.

**Status:** done

- [x] `agregar_ocupante` sobre un apartamento vacío crea un Ocupante `pending`, `es_principal=False` (ya no auto-promueve al primero).
- [x] `confirmar_ocupante` por staff sobre ese primer Ocupante marca `confirmado_en` y lo promueve a principal en la misma operación.
- [x] `confirmar_ocupante` por el principal ya confirmado sobre un segundo Ocupante lo confirma sin tocar quién es principal.
- [x] Un actor que no es ni el principal confirmado del apartamento ni staff intentando confirmar es rechazado (`PermissionError`).
- [x] `dar_de_baja_ocupante` sobre un pending lo retira dejando `confirmado_en` en `NULL` para siempre (se distingue de un confirmado que luego se fue) — sin tocar la función, reutilizada tal cual.
- [x] Un Ocupante pending ya cuenta para `MAX_OCUPANTES_ACTIVOS=5`.
- [x] Un Ocupante pending resuelve igual que uno confirmado en los flujos que dependen de `apartamento_actual_id` (anunciar/recibir) — sin gate funcional, la confirmación es solo el sello.
- [x] Tests de dominio en `test_ocupante_service.py` cubren cada punto anterior (9 tests nuevos).

## Hallazgo: blast radius sobre tests ya existentes (esperado, no un bug)

Igual que el ticket 03, este cambio de comportamiento (ya no auto-promover al crear) rompió **muchos** tests preexistentes que asumían "el primer Ocupante con teléfono queda principal de inmediato" como parte de su fixture de setup, sin ser tests SOBRE ese comportamiento en sí — en `test_ocupante_service.py`, `test_announce_paquete.py`, `test_preferencia_notificacion.py`, `test_announce_new.py`, `test_customer_verify.py` (16 tests), `test_customers_manage.py`, `test_packages.py`. Todos corregidos agregando un paso explícito de confirmación (por staff) antes de la acción que el test realmente quiere probar — no cambios de intención, solo de fixture.

## Hallazgo real de diseño: `es_ocupante_no_principal` con la nueva confirmación

`customer_verify.py` decide si mostrar el formulario editable de Torre/Apartamento o la vista de solo lectura mirando `es_ocupante_no_principal = mi_ocupante is not None and not mi_ocupante.es_principal`. Antes de este ticket, el primer Ocupante de una unidad SIEMPRE era principal de inmediato, así que esa condición nunca capturaba a alguien recién auto-declarado. Ahora sí — un residente que se acaba de declarar (pending, sin principal en su unidad todavía) cae en esa condición y vería el mensaje "Estos datos los gestiona el Ocupante principal de tu unidad", que no tiene sentido cuando ese principal ni existe todavía.

**Se deja sin resolver a propósito** — es exactamente el terreno de los tickets 07/08 (UI de confirmar/rechazar), que necesitan diseñar esta distinción de tres estados (principal confirmado / pending sin reclamar / confirmado-pero-no-principal) de todos modos. Documentado acá para que no se pierda: la condición correcta probablemente necesita distinguir "ya hay un principal confirmado que no soy yo" (sí, solo lectura) de "todavía no hay principal en esta unidad" (no, edición normal) — no solo mirar `es_principal` del propio Ocupante.

## Implementación

- **Modelo:** `Ocupante.confirmado_en` (DateTime nullable, mismo patrón que `desvinculado_en`) en `ocupante.py`. Migración `0022_ocupante_confirmado_en.py` (`down_revision = 0021_seed_catalogo_apartamentos`). `ocupante` agregado a `test_parity_esquema_orm.py` (no estaba cubierto por el guard de paridad antes de este ticket — sin drift preexistente detectado).
- **Dominio:** `ocupante_service.agregar_ocupante` ya no marca `es_principal` al crear (siempre `False`). Función nueva `confirmar_ocupante(session, ocupante, actor)` + helper privado `_puede_confirmar` (acepta `Usuario` de staff o `Persona` principal confirmada del mismo apartamento).
- **Suite completa:** todos los tests en verde salvo los 6 fallos preexistentes de `test_layout.py` (no relacionados, confirmados en el ticket 01).

# 09 — "Corregir destinatario" (staff): opción "Es un nuevo ocupante de este apartamento"

**What to build:** en el modal "Corregir destinatario" de `/paquetes` (hoy, cuando hay candidatos — Ocupantes del apartamento del snapshot + el anunciante — el staff está OBLIGADO a elegir de la lista, sin escape a texto libre), agregar una opción nueva en ese mismo `<select>`: **"Es un nuevo ocupante de este apartamento"**, que revela un campo de nombre (obligatorio) + teléfono (opcional). Al guardar con esa opción, se crea un `Ocupante` nuevo para el Apartamento del snapshot del paquete (vía `agregar_ocupante`, respetando el límite de 5 y el bloqueo de un-teléfono-un-apartamento de los tickets 02/03) y el destinatario del paquete queda corregido a ese Ocupante recién creado.

**Blocked by:** 08, 03

**Status:** done

- [x] El `<select>` de "Corregir destinatario" incluye la opción nueva cuando hay candidatos (Ocupantes conocidos del apartamento).
- [x] Elegir esa opción revela un campo de nombre y teléfono (opcional), reemplazando la selección de la lista (JS vanilla, `onchange` + `hidden`).
- [x] Al guardar, se crea un `Ocupante` nuevo en el Apartamento del snapshot del paquete, y el destinatario del paquete (`recipient_name`/`recipient_phone`) queda corregido a ese Ocupante — el teléfono resuelto es el propio si lo trae, o si no, el del principal (`telefono_notificacion_ocupante`, movido a `ocupante_service.py` para reusarlo desde `packages.py` y `paquete_service.py`).
- [x] Respeta el límite de 5 Ocupantes activos por apartamento y el bloqueo de un-teléfono-un-apartamento (mismos mensajes de error que en el ticket 03, vía `agregar_ocupante`).
- [x] El comportamiento existente (elegir un candidato ya conocido de la lista, o el campo de texto libre cuando NO hay apartamento resuelto) sigue funcionando sin regresión.
- [x] Tests cubren: creación de Ocupante nuevo con/sin teléfono vía este flujo + rechazo sin nombre + no-regresión del flujo viejo (43 tests previos de `test_packages.py` siguen pasando).

## Implementación

- `ocupante_service.telefono_notificacion_ocupante` (renombrada, antes privada en `paquete_service.py`) — ahora la comparten `announce()` (ticket 08) y esta ruta.
- `packages.py`: nuevos form fields `nuevo_ocupante_nombre`/`nuevo_ocupante_telefono`; rama `candidato_idx == "nuevo"` crea el Ocupante vía `agregar_ocupante` y corrige con su nombre/teléfono resuelto.
- `packages/list.html`: opción nueva en el `<select>` + bloque oculto con los 2 campos, mostrado/ocultado con `onchange`.
- 3 tests nuevos en `test_packages.py`. Suite completa: 506 passed (1 fallo no relacionado y confirmado flaky en `test_otp_service.py` — un código OTP de 2 dígitos generado al azar coincidió como substring de su propio hash bcrypt; pasa limpio al reintentar, sin tocar nada de OTP en este ticket).

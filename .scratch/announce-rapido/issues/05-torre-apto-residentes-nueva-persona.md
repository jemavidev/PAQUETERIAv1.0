# 05 — Torre+Apto: resolución en vivo + lista de residentes + nueva persona + Anunciar

**What to build:** extiende el campo único del ticket 04 con la 3ª rama de detección: empieza en `0` o `1`, todo dígitos → candidato Torre+Apartamento. El código se arma como Torre de 2 dígitos (`01`–`10` → `TORRE 1`..`TORRE 10`) seguida del número de Apartamento tal cual (ej. `01106` = Torre 1 / Apto 106, `041304` = Torre 4 / Apto 1304). La búsqueda se dispara en cuanto los dígitos tecleados calzan EXACTO con una unidad real del catálogo (vía `resolver_apartamento`) — no antes —, más el mismo debounce de ~150ms del ticket 04 como red de seguridad.

Al resolver la unidad, el endpoint de identificación (ticket 04) devuelve: la lista de residentes activos de esa unidad (`listar_ocupantes`, Principal primero), y **siempre** junto a la lista (exista o esté vacía) la opción "Nueva persona" — Nombre + el mismo campo inteligente Teléfono/WhatsApp del ticket 04. Dar de alta un residente nuevo reutiliza `agregar_ocupante` tal cual (nace `pending`, sin `es_principal` — la confirmación sigue siendo un flujo aparte en `/residentes`/`/mis-datos`, esta ficha no agrega ninguna acción de confirmar).

Clic/tap sobre un residente de la lista resuelve el Destinatario vía `Destinatario.ocupante(ocupante_id)` (ticket 03) y revela los botones **Anunciar**/**Recibir**, mismo comportamiento que el ticket 04 ya dejó funcionando para Teléfono/WhatsApp. **Anunciar** funciona de punta a punta para este camino.

**Blocked by:** 04.

**Status:** done

## Hallazgos de code-review (corregidos antes de desplegar)

- **Bug real (Spec):** el `contacto` de "Nueva persona" que no clasificaba limpio ni como Teléfono ni como WhatsApp (ej. un teléfono mal tecleado de 8 dígitos) se descartaba en silencio -- el Ocupante quedaba creado SIN el contacto que el staff sí quiso darle, sin ningún aviso. Corregido: ahora se rechaza explícitamente ("Ese contacto no parece un Teléfono ni un usuario de WhatsApp válido").
- **Duplicación real (Standards):** el parseo de `ocupante_id` (UUID) estaba repetido en `GET /announce/identificar-ocupante` y en el camino 2 de `POST /announce`. Extraído a `_resolver_ocupante`, un único lugar.
- **Menor:** la etiqueta "Teléfono o WhatsApp (opcional)" del campo Contacto era engañosa para el primer residente de una unidad vacía (ahí SÍ es obligatorio, `agregar_ocupante` lo exige) -- ahora la etiqueta cambia según si la unidad ya tiene residentes o no.
- Agregado test end-to-end faltante: anunciar un residente existente identificado solo por WhatsApp (antes solo estaba cubierto a nivel de dominio).

- [x] Un código Torre+Apto incompleto o inválido no dispara ningún resultado (no revienta).
- [x] Un código válido con residentes muestra la lista (Principal primero) + "Nueva persona".
- [x] Un código válido de una unidad vacía muestra solo "Nueva persona" (sin lista).
- [x] "Nueva persona" da de alta un Ocupante `pending`, sin `es_principal`, con Teléfono o WhatsApp según lo que se haya tecleado.
- [x] Clic en un residente de la lista resuelve vía `Destinatario.ocupante()` y muestra Anunciar/Recibir.
- [x] "Anunciar" sobre un residente de la lista (con Teléfono propio, con WhatsApp propio, o sin ninguno de los dos — cae al Principal) deja el Paquete en `ANUNCIADO` con el snapshot de esa unidad.
- [x] Verificación manual en navegador real (skill `run`): flujo completo Torre+Apto de punta a punta, sin errores de consola.

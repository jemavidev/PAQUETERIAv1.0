# 05 — Torre+Apto: resolución en vivo + lista de residentes + nueva persona + Anunciar

**What to build:** extiende el campo único del ticket 04 con la 3ª rama de detección: empieza en `0` o `1`, todo dígitos → candidato Torre+Apartamento. El código se arma como Torre de 2 dígitos (`01`–`10` → `TORRE 1`..`TORRE 10`) seguida del número de Apartamento tal cual (ej. `01106` = Torre 1 / Apto 106, `041304` = Torre 4 / Apto 1304). La búsqueda se dispara en cuanto los dígitos tecleados calzan EXACTO con una unidad real del catálogo (vía `resolver_apartamento`) — no antes —, más el mismo debounce de ~150ms del ticket 04 como red de seguridad.

Al resolver la unidad, el endpoint de identificación (ticket 04) devuelve: la lista de residentes activos de esa unidad (`listar_ocupantes`, Principal primero), y **siempre** junto a la lista (exista o esté vacía) la opción "Nueva persona" — Nombre + el mismo campo inteligente Teléfono/WhatsApp del ticket 04. Dar de alta un residente nuevo reutiliza `agregar_ocupante` tal cual (nace `pending`, sin `es_principal` — la confirmación sigue siendo un flujo aparte en `/residentes`/`/mis-datos`, esta ficha no agrega ninguna acción de confirmar).

Clic/tap sobre un residente de la lista resuelve el Destinatario vía `Destinatario.ocupante(ocupante_id)` (ticket 03) y revela los botones **Anunciar**/**Recibir**, mismo comportamiento que el ticket 04 ya dejó funcionando para Teléfono/WhatsApp. **Anunciar** funciona de punta a punta para este camino.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] Un código Torre+Apto incompleto o inválido no dispara ningún resultado (no revienta).
- [ ] Un código válido con residentes muestra la lista (Principal primero) + "Nueva persona".
- [ ] Un código válido de una unidad vacía muestra solo "Nueva persona" (sin lista).
- [ ] "Nueva persona" da de alta un Ocupante `pending`, sin `es_principal`, con Teléfono o WhatsApp según lo que se haya tecleado.
- [ ] Clic en un residente de la lista resuelve vía `Destinatario.ocupante()` y muestra Anunciar/Recibir.
- [ ] "Anunciar" sobre un residente de la lista (con Teléfono propio, con WhatsApp propio, o sin ninguno de los dos — cae al Principal) deja el Paquete en `ANUNCIADO` con el snapshot de esa unidad.
- [ ] Verificación manual en navegador real (skill `run`): flujo completo Torre+Apto de punta a punta, sin errores de consola.

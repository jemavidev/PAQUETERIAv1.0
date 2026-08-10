# 04 — Campo único inteligente: identificar por Teléfono o WhatsApp + Anunciar

**What to build:** reemplaza el formulario actual de `/announce` (3 bloques desconectados: Apartamento, Residentes, Anunciar) por un campo de texto único, con foco automático al cargar, arriba de todo. La opción de "solo declarar el apartamento sin anunciar nada" desaparece de esta ruta — un enlace visible lleva a `/residentes` para quien necesite registrar residentes sin que haya un paquete de por medio.

Detección de formato (re-aplicada en el servidor, no solo confiada al cliente):
- Empieza en `3`, todo dígitos → candidato Teléfono. Se valida/normaliza con `normalizar_telefono`.
- Empieza con una letra → candidato usuario de WhatsApp. Se normaliza igual que ya hace `update_datos_personales` (recorta `@` inicial).
- (La rama Torre+Apartamento, dígitos que empiezan en `0`/`1`, es del ticket 05 — en esta ficha esos casos simplemente no resuelven nada todavía.)

Endpoint nuevo bajo `/announce` que recibe el valor tecleado, re-aplica la detección, y devuelve un fragmento HTML: la Persona resuelta (con los botones **Anunciar**/**Recibir**) si hay match, el formulario de "Persona nueva" (Nombre + este mismo campo inteligente) si no hay match, o nada si el valor no calza con ningún candidato todavía. Debounce de ~150ms tras el último carácter tecleado. Mismo patrón de fragmento-reemplaza-`innerHTML` que ya usa la búsqueda en vivo de `/paquetes`.

El botón **Anunciar** funciona de punta a punta para este camino (Teléfono/WhatsApp, con o sin match previo): llama a `announce()` (ticket 03 para el caso WhatsApp) con la Persona resuelta o recién creada como Anunciante y Destinatario (`Destinatario.yo_mismo()`), deja el Paquete en `ANUNCIADO`, muestra un toast con el nombre + código de acceso, limpia el formulario y devuelve el foco al campo principal.

El botón **Recibir** aparece junto a Anunciar pero todavía no hace nada (se cablea en el ticket 06) — puede quedar deshabilitado o simplemente sin `onclick` todavía, a criterio de quien implemente.

**Blocked by:** 03.

**Status:** done

## Bug real encontrado en code-review (corregido antes de desplegar)

`_clasificar()` clasificaba CUALQUIER prefijo como candidato completo (el primer "3" tecleado ya era "candidato Teléfono"). Como el fragmento se re-renderiza (`innerHTML`) en cada tecleo y el campo Nombre del caso "sin match" tenía `autofocus`, esto le robaba el foco al campo principal en cada actualización mientras el staff seguía escribiendo un Teléfono/WhatsApp real -- interrumpía justo el tecleo rápido que esta pantalla existe para habilitar. No lo agarró la suite (usa valores completos) ni la primera verificación manual (usó `fill()`, que no simula tecleo real). Se re-verificó con Playwright tecleando carácter por carácter (delay 200ms > debounce 150ms): el valor final quedaba completo y el foco nunca se movía.

Corregido con dos cambios: (1) `_clasificar` exige el valor COMPLETO -- 10 dígitos exactos para Teléfono, mínimo 3 caracteres para WhatsApp; (2) el campo Nombre del fragmento ya NO lleva `autofocus` (cierra el caso por completo, incluso para nombres de usuario largos donde el umbral de (1) no alcanza a prevenir todas las re-renderizaciones intermedias).

Además, dos simplificaciones menores de `/code-review` (Standards): `buscar_persona_por_whatsapp` reusa `_validar_whatsapp_usuario` en vez de repetir el regex; `announce_submit` ya no duplica el guard XOR de `announce()` para el caso "ninguno de los dos" (se deja que `announce()` lo rechace); y se repuebla el campo `q` en la respuesta de error para no perder lo ya identificado.

- [x] Escribir un Teléfono que coincide con una Persona ya registrada la resuelve y muestra Anunciar/Recibir.
- [x] Escribir un Teléfono que NO coincide crea una Persona nueva pidiendo el Nombre ahí mismo, sin apartamento asociado.
- [x] Escribir un usuario de WhatsApp que coincide con una Persona ya registrada la resuelve y muestra Anunciar/Recibir.
- [x] Escribir un usuario de WhatsApp que NO coincide crea una Persona nueva solo-WhatsApp pidiendo el Nombre ahí mismo.
- [x] Un valor que no calza con ningún candidato (vacío, empieza en `2`/`4`-`9`, símbolos) no dispara ningún resultado.
- [x] La detección se re-aplica en el servidor — un valor mal clasificado por el cliente no cambia el resultado real.
- [x] "Anunciar" deja el Paquete en `ANUNCIADO` con el snapshot correcto, para ambos casos (Teléfono y WhatsApp).
- [x] Tras "Anunciar", el formulario se limpia y el foco vuelve al campo principal.
- [x] `/announce` ya no ofrece declarar el apartamento sin anunciar; hay un enlace visible a `/residentes`.
- [x] Verificación manual en navegador real (skill `run`): detección de formato en vivo, debounce, sin errores de consola.

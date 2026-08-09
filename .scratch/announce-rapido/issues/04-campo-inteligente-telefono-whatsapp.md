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

**Status:** ready-for-agent

- [ ] Escribir un Teléfono que coincide con una Persona ya registrada la resuelve y muestra Anunciar/Recibir.
- [ ] Escribir un Teléfono que NO coincide crea una Persona nueva pidiendo el Nombre ahí mismo, sin apartamento asociado.
- [ ] Escribir un usuario de WhatsApp que coincide con una Persona ya registrada la resuelve y muestra Anunciar/Recibir.
- [ ] Escribir un usuario de WhatsApp que NO coincide crea una Persona nueva solo-WhatsApp pidiendo el Nombre ahí mismo.
- [ ] Un valor que no calza con ningún candidato (vacío, empieza en `2`/`4`-`9`, símbolos) no dispara ningún resultado.
- [ ] La detección se re-aplica en el servidor — un valor mal clasificado por el cliente no cambia el resultado real.
- [ ] "Anunciar" deja el Paquete en `ANUNCIADO` con el snapshot correcto, para ambos casos (Teléfono y WhatsApp).
- [ ] Tras "Anunciar", el formulario se limpia y el foco vuelve al campo principal.
- [ ] `/announce` ya no ofrece declarar el apartamento sin anunciar; hay un enlace visible a `/residentes`.
- [ ] Verificación manual en navegador real (skill `run`): detección de formato en vivo, debounce, sin errores de consola.

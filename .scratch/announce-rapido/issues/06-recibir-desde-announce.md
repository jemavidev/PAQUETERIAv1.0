# 06 — Recibir: anunciar y abrir de inmediato el formulario de recepción

**What to build:** cablea el botón **Recibir** que ya aparece (sin función todavía) junto a Anunciar en los tickets 04 y 05, para ambos caminos de identificación (Teléfono/WhatsApp directo, y residente elegido de Torre+Apto). Al presionarlo: se llama a `announce()` igual que hace Anunciar, y a continuación se muestra **inline** (sin navegar a `/paquetes`) el mismo formulario de recepción que ya existe ahí — escáner ZXing de Guía, Tipo, Condición, hasta 3 fotos —, scoped al `paquete_id` recién creado. Completar ese formulario transiciona el Paquete a `RECIBIDO` reusando `receive()` tal cual existe hoy.

Requisito duro: reusar el componente/JS de recepción existente, no reimplementarlo. El mecanismo exacto (fetch + swap del fragmento vs. redirect a una vista dedicada) queda a criterio de quien implemente.

**Blocked by:** 04, 05.

**Status:** done

## Hallazgos de code-review (corregidos antes de desplegar)

- **Bug real (encontrado independientemente por los dos ejes, Standards y Spec):** el fragmento "sin match, nueva persona" de `_identificar.html` (camino 1, Teléfono/WhatsApp nuevo) tenía su PROPIO botón Recibir, distinto del de `_persona_resuelta.html`, y se había quedado sin cablear (`type="button" disabled`) mientras los otros caminos ya funcionaban. Un operador que tecleara un teléfono/WhatsApp NUEVO nunca podía pulsar Recibir. Corregido + test de regresión agregado.
- Se cableó también el tercer camino (nueva persona dentro de una unidad Torre+Apto, `_identificar_unidad.html`) aunque el ticket solo mencionaba los dos primeros — mismo mecanismo servidor exacto en los tres, dejarlo deshabilitado ahí hubiera sido inconsistente para el staff.
- Extraído `components/_recibir_paquete.html` (macros `modal_recibir()` + `recursos_recibir()`) desde `packages/_resultados.html`/`list.html` para que `/paquetes` y `/announce` reusen el MISMO componente/JS, sin duplicar el escáner ZXing ni el form de recepción — requisito duro del ticket.
- `autofocus` del campo principal de `/announce` se desactiva cuando el modal de Recibir se muestra ya abierto (mismo tipo de bug de robo de foco ya encontrado y corregido en el ticket 04).

- [x] "Recibir" sobre un match directo de Teléfono/WhatsApp (ticket 04) anuncia el Paquete y abre el formulario de recepción para ese `paquete_id`.
- [x] "Recibir" sobre un residente elegido vía Torre+Apto (ticket 05) hace lo mismo.
- [x] El formulario de recepción mostrado es el mismo componente (escáner de guía, Tipo, Condición, fotos) que ya usa `/paquetes` — mismas aserciones de `receive()` aplican sin cambios.
- [x] Completar el formulario transiciona el Paquete a `RECIBIDO`; las fotos se suben en segundo plano igual que hoy.
- [x] Verificación manual en navegador real (skill `run`): flujo Anunciar+Recibir de punta a punta (Postgres efímero + Playwright, tecleo carácter por carácter, extensión Claude-in-Chrome no disponible), sin errores de consola. Escáner de cámara no verificable en Chromium headless (sin hardware de video) — se verificó el resto del formulario (guía manual, chips, carga de fotos, submit) de punta a punta. Desplegado y confirmado en `test.papyrus.com.co`.

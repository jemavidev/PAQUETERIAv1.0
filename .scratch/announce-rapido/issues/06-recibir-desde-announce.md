# 06 — Recibir: anunciar y abrir de inmediato el formulario de recepción

**What to build:** cablea el botón **Recibir** que ya aparece (sin función todavía) junto a Anunciar en los tickets 04 y 05, para ambos caminos de identificación (Teléfono/WhatsApp directo, y residente elegido de Torre+Apto). Al presionarlo: se llama a `announce()` igual que hace Anunciar, y a continuación se muestra **inline** (sin navegar a `/paquetes`) el mismo formulario de recepción que ya existe ahí — escáner ZXing de Guía, Tipo, Condición, hasta 3 fotos —, scoped al `paquete_id` recién creado. Completar ese formulario transiciona el Paquete a `RECIBIDO` reusando `receive()` tal cual existe hoy.

Requisito duro: reusar el componente/JS de recepción existente, no reimplementarlo. El mecanismo exacto (fetch + swap del fragmento vs. redirect a una vista dedicada) queda a criterio de quien implemente.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] "Recibir" sobre un match directo de Teléfono/WhatsApp (ticket 04) anuncia el Paquete y abre el formulario de recepción para ese `paquete_id`.
- [ ] "Recibir" sobre un residente elegido vía Torre+Apto (ticket 05) hace lo mismo.
- [ ] El formulario de recepción mostrado es el mismo componente (escáner de guía, Tipo, Condición, fotos) que ya usa `/paquetes` — mismas aserciones de `receive()` aplican sin cambios.
- [ ] Completar el formulario transiciona el Paquete a `RECIBIDO`; las fotos se suben en segundo plano igual que hoy.
- [ ] Verificación manual en navegador real (skill `run`): flujo Anunciar+Recibir de punta a punta con el escáner real, sin errores de consola.

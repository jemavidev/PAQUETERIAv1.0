# 01 — Colores de estado + enlace a `/announce`

**Qué construir:** Los colores de los badges de estado pasan a Anunciado=naranja, Recibido=azul, Entregado=verde, Cancelado=rojo (en `/paquetes` y `/consultar`). Se agrega un enlace visible a `/announce` en el encabezado de `/paquetes`.

**Bloqueado por:** Ninguno.

**Estado:** ready-for-agent

- [ ] `.estado-anunciado`, `.estado-recibido`, `.estado-cancelado` actualizados en `packages/list.html` y `search/form.html` (Entregado ya era verde, sin cambio).
- [ ] Enlace a `/announce` visible en el encabezado de `/paquetes`.
- [ ] Suite completa (`pytest`) pasa.

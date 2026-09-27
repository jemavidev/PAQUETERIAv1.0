# 02 — La Posición pasa a ser obligatoria al Recibir

**What to build:** Recibir sin Posición se rechaza. El endpoint responde 400 ANTES de cualquier efecto colateral (declarar unidad, resolver/crear Ocupante, pago al mensajero) y reabre el modal Recibir de ese paquete con el mensaje junto a la grilla — en /paquetes y en /consultar (`origen=consultar`), igual que la Guía demasiado larga. El navegador también bloquea el envío (grupo requerido). Spec: `../spec.md`.

**Blocked by:** 01 — Recibir captura la Posición.

**Status:** ready-for-agent

- [ ] POST sin Posición (o inválida) → 400, modal reabierto con el mensaje, sin unidad declarada, sin Ocupante creado, sin pago registrado.
- [ ] Mismo comportamiento desde /consultar y desde /announce (anunciar y recibir).
- [ ] La grilla es un grupo requerido en el navegador.
- [ ] Las pruebas existentes que ejecutan Recibir (web y ayudante de navegador) envían una Posición válida.
- [ ] Modo Lector sin cambios: el foco sigue en la guía y la lectura nunca elige Posición ni envía.

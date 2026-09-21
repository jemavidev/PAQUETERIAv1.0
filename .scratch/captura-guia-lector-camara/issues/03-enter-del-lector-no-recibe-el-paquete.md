# 03 — El Enter (o Tab) del lector no recibe el paquete

**What to build:** hoy un lector que actúa como teclado y manda un Enter al final de la lectura envía el formulario de Recibir: el paquete queda `Recibido` al instante con Normal/Bueno por defecto, sin fotos, sin elegir Residente y sin registrar un posible pago contra entrega. Con este ticket, una lectura **solo llena la Guía**: un Enter o Tab al final deja el Paquete `Anunciado`, el modal abierto y la guía escrita; el Operador confirma con el botón "Recibir". La regla vale para lector físico y para tecleo a mano, y llega a /paquetes, /announce y al Recibir de /consultar por reusar el mismo componente.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 28, 29, 57 y 58).

**Blocked by:** 01 — Aislar la captura de guía del script compartido; 02 — Prueba en navegador real para el modal Recibir.

**Status:** ready-for-agent

- [ ] En el modal Recibir, teclear una guía rápido y pulsar Enter deja el Paquete `Anunciado` (verificado en la BD), el modal abierto y la guía escrita en el campo.
- [ ] Lo mismo con Tab: el campo conserva el valor y no se envía nada.
- [ ] Después de eso, pulsar "Recibir" deja el Paquete `Recibido` con la guía guardada (en mayúsculas, como hoy).
- [ ] La guardia no depende de una sola vía: si el formulario intenta enviarse por un camino que no sea pulsar el botón "Recibir" mientras el foco está en el campo Guía, tampoco se recibe el paquete.
- [ ] Enter en los demás campos del modal se comporta como hoy (el ticket solo protege el campo Guía).
- [ ] "Confirmar guía" de Entregar y de /consultar no cambia (ya está fuera del formulario, un Enter allí no envía nada): sigue igual.
- [ ] El mismo comportamiento se verifica en /paquetes en navegador real; para /announce y el Recibir de /consultar basta comprobar por HTTP que cargan el mismo componente con el mismo comportamiento.
- [ ] Las pruebas web existentes de Recibir pasan sin modificarse.

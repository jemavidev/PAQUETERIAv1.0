# 05 — Recibir: declarar apartamento y confirmar/elegir/crear destinatario

**What to build:** el modal de Recibir (compartido entre `/paquetes` y `/announce`) gana un paso nuevo y opcional: si el destinatario no tiene apartamento todavía, el staff puede declarar Torre+Apartamento ahí mismo; si ya tiene (o se lo acaba de declarar), el staff ve el roster de residentes de esa unidad y puede confirmar al ya resuelto, elegir a otro residente existente, o registrar uno nuevo — reusando el mecanismo de candidatos que ya existe en Corregir destinatario. Si el destinatario ya resuelve sin ambigüedad, Recibir sigue funcionando exactamente igual que hoy, sin fricción adicional.

**Blocked by:** 01 (input de contacto único para registrar un residente nuevo ahí mismo), 04 (la promoción automática necesita que este paso pueda dejar un Ocupante concreto identificado).

**Status:** ready-for-agent

- [ ] Si el destinatario del paquete no tiene apartamento en su Persona, el modal de Recibir ofrece declarar Torre+Apartamento (mismo catálogo cerrado, sin la restricción de "solo unidades vacías" del ticket 13 — acá se está identificando a una persona ya conocida por Teléfono/WhatsApp).
- [ ] Si el destinatario tiene (o se le acaba de declarar) apartamento, el modal muestra el roster de esa unidad con las mismas 3 opciones que ya tiene Corregir destinatario: confirmar al actual, elegir otro residente existente, o registrar uno nuevo (con el input único de contacto del ticket 01).
- [ ] Completar este paso no es obligatorio — si no hay ambigüedad, Recibir se completa con el flujo de siempre (tipo/condición/guía) sin mostrar nada nuevo.
- [ ] El destinatario resuelto en este paso es el que usa la promoción automática del ticket 04.
- [ ] Tests web en `test_packages.py` y `test_announce_new.py` cubriendo: destinatario sin apartamento (declarar ahí mismo), destinatario con apartamento y varios residentes (elegir/crear), destinatario sin ambigüedad (Recibir sin fricción).

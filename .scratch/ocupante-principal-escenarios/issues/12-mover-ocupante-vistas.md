# 12 — Mover residentes entre unidades — 4 vistas

**What to build:** en las 4 vistas que hoy bloquean con "ya es Ocupante activo -- debe darse de baja antes de asociarse de nuevo" (tab Dirección, tab Residentes, `/announce` Torre+Apto nueva persona, Corregir destinatario nuevo ocupante), cuando la Persona/teléfono en cuestión NO es principal en su unidad actual, se ofrece moverla directo (reusando el ticket 11) en vez de solo bloquear. Si SÍ es principal, se mantiene el bloqueo de siempre.

**Blocked by:** 11 (función de dominio para mover).

**Status:** ready-for-agent

- [ ] Las 4 vistas muestran, cuando corresponde, de qué unidad (Torre+Apartamento) es Ocupante actualmente esa persona.
- [ ] Cuando no es principal ahí, se ofrece una acción "Mover acá" que usa la función del ticket 11.
- [ ] Cuando es principal, se mantiene el mensaje de bloqueo actual, sin acción de mover.
- [ ] No se ofrece esta acción dentro de Anunciar/Recibir — es una acción de gestión de residentes aparte.
- [ ] No disponible en `/mis-datos` (exclusivo de staff).
- [ ] Tests en `test_customers_manage.py`, `test_announce_new.py`, `test_packages.py` cubriendo mover exitoso y bloqueo de principal, en cada una de las 4 vistas.

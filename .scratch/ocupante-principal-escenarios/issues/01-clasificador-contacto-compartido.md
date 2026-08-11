# 01 — Prefactor: clasificador de contacto compartido

**What to build:** el clasificador de contacto (Teléfono: 10 dígitos empezando en `3`; WhatsApp: ≥3 letras iniciales; hoy `_clasificar`, privado en `announce_new.py`) se mueve a un módulo de dominio compartido, para que otras vistas lo reusen sin duplicar la regla. Sin cambio de comportamiento observable en `/announce` — es puro movimiento de código.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] El clasificador vive en un módulo de dominio compartido (no en una ruta web específica).
- [ ] `announce_new.py` importa y usa la versión compartida — sin duplicar la lógica.
- [ ] Los 3 call sites que ya usan el clasificador dentro de `/announce` (`GET /announce/identificar`, el campo `contacto` de "Nueva persona", y donde corresponda) siguen funcionando idéntico.
- [ ] Suite completa de tests de `/announce` sigue en verde, sin cambios de comportamiento.

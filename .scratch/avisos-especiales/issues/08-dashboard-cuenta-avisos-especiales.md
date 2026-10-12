# 08 — El Dashboard cuenta los avisos especiales

**What to build:** Las tarjetas de uso y costo de SMS del Dashboard incluyen los SMS de avisos especiales junto a los avisos de paquete,
para que el gasto en SMS siga completo.

Ver spec: Implementation Decisions (Registro de envíos SMS) y User Stories 37-38.

**Blocked by:** 05 — Enviar SMS y "Último SMS"

**Status:** done (2026-10-11)

- [x] Las tarjetas que hoy suman `AVISO_PAQUETE` (cantidad y costo) suman también `AVISO_ESPECIAL`
- [x] Los OTP siguen contándose aparte, como hoy
- [x] Prueba en `test_admin_dashboard.py` (o su equivalente) con registros de los dos tipos

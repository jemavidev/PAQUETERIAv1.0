# 15 — Indicador de Torre+Apto sin coincidencia en `/announce`

**What to build:** cuando el código Torre+Apto tecleado en `/announce` no corresponde a ninguna unidad real del catálogo cerrado, se muestra un mensaje/indicador claro en vez de no mostrar nada (comportamiento actual).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `GET /announce/identificar` con un código Torre+Apto completo (2 dígitos de torre válidos + número de apartamento) que no calza con el catálogo devuelve un fragmento con un mensaje explícito, no una respuesta vacía.
- [ ] Un código todavía incompleto (a medio teclear) sigue sin mostrar nada — el indicador solo aparece cuando ya se puede evaluar contra el catálogo.
- [ ] Test en `test_announce_new.py` cubriendo ambos casos (incompleto vs. completo-pero-inválido).

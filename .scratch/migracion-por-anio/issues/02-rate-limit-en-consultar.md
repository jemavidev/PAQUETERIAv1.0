# 02 — Rate-limit en /consultar

**What to build:** un límite de 10 intentos por minuto en la consulta pública `/consultar`, reusando
el mecanismo genérico `rate_limit()` ya existente en el proyecto.

**Blocked by:** None — can start immediately (independiente de la migración por año).

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: d54801b)

- [ ] 10 solicitudes en la ventana de 60 segundos pasan con normalidad
- [ ] La 11ª solicitud dentro del mismo minuto responde 429 con el mismo patrón de mensaje que ya
      usan `/otp/solicitar` y el login de staff

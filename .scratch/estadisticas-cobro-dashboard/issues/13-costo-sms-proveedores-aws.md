# 13 — Costo promedio por SMS en /administracion/proveedores (solo AWS)

**What to build:** un campo nuevo, "Costo promedio por SMS (COP)", en la sección de AWS SNS del canal SMS
de `/administracion/proveedores` — el único dato de configuración de esta feature que un ADMIN necesita
tocar. No depende de ningún otro ticket ni ninguno depende de él salvo el 15 (que consume el valor); se
puede construir y verse en pantalla de forma completamente aislada.

**Blocked by:** None — can start immediately.

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `guardar_costo_promedio_sms` + migración 0056)

- [ ] El campo aparece SOLO en la sección de AWS SNS (no en LIWA ni en Twilio).
- [ ] Acepta números con decimales, incluido vacío (= sin configurar). Un valor negativo o no numérico
      se rechaza con un mensaje de error claro, sin perder el resto del formulario.
- [ ] El valor se guarda en la BASE DE DATOS (no en el `.env` del servidor) — guardarlo NO dispara la
      aplicación de credenciales por SSH ni reinicia el contenedor; el resto del formulario de AWS SNS
      (credenciales, toggle habilitado) sigue funcionando exactamente igual que hoy.
- [ ] Al guardar, el nuevo valor está disponible de inmediato para cualquier consulta (sin esperar un
      reinicio).
- [ ] Queda constancia de quién y cuándo lo cambió por última vez (reutilizando los mismos campos de
      auditoría que ya tiene la configuración del proveedor).
- [ ] Pruebas web de la ruta de proveedores: guardar un valor válido, un vacío, un valor negativo, y un
      valor no numérico; y que cambiarlo no dispara ningún efecto de credenciales/reinicio.

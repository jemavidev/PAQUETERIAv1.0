# 12 — Registro de envíos de SMS: códigos de acceso y mensajes de prueba

**What to build:** los otros dos caminos que hoy envían SMS —el código de acceso (OTP) al iniciar sesión,
y el mensaje de prueba que un ADMIN puede enviarse desde la administración de plantillas de
notificación— quedan anotados en el mismo registro del ticket 11, diferenciados por tipo.

**Blocked by:** 11

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `registro_sms_service.py` + 0055/0059)

- [ ] Cada código de acceso enviado por SMS queda registrado con tipo "código de acceso", el proveedor
      que lo entregó (o "fallido"), mismas reglas de failover y de tolerancia a fallos que el 11 — sin
      paquete ni evento asociado (no aplica).
- [ ] Cada mensaje de prueba de plantillas enviado por SMS queda registrado con tipo "aviso de paquete"
      (para el conteo) pero SIN paquete asociado (una prueba no tiene paquete real).
- [ ] El servicio de conteo del registro (ticket 11) puede filtrar o desglosar por tipo — "avisos" vs.
      "códigos de acceso" — para que el ticket 14 pueda construir "X avisos · Y códigos" sin recorrer las
      filas a mano.
- [ ] El remitente de consola/desarrollo tampoco registra códigos de acceso ni pruebas.
- [ ] Pruebas con proveedores falsos que cubren el envío de un código de acceso y de un mensaje de prueba,
      cada uno contado por separado del otro tipo.

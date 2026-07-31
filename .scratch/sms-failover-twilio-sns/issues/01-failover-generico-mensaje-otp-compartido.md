# 01 — Failover genérico de SMS + mensaje OTP compartido

**What to build:** Un mecanismo de reintento genérico, independiente de
proveedor: dada una lista ordenada de senders SMS (cualquier objeto con la
forma de envío `(destino, mensaje) -> None`), enviar un mensaje prueba cada
sender en orden, deteniéndose en el primer éxito. Una falla de conectividad
pasa al siguiente sender de la lista; un rechazo explícito de un proveedor
(que sí recibió y procesó la solicitud) detiene el intento de inmediato, sin
probar los demás, y propaga el error tal cual. Además, el texto del mensaje
OTP ("Tu código de verificación PAQUETEX es: {codigo}") se construye en un
solo lugar, para que todo `OtpSender` (presente y futuro) lo reutilice en
vez de duplicar el string.

Esto es un prefactor puro — no cambia ningún wiring en `app/web/`, no es
visible para ningún usuario todavía. Desbloquea limpiamente los tickets 02 y
03, que solo necesitarán aportar sus propios senders reales a esta pieza ya
probada.

**Blocked by:** None — puede empezar de inmediato.

**Status:** ready-for-agent

- [x] Existe un failover sender genérico en `app/domain` (reutilizable tanto
      para el shape de `NotificationSender` como el de `OtpSender`), que
      reintenta solo ante fallas de conectividad — timeouts/conexión,
      `HTTPStatusError` 5xx/401/403 de `httpx`, y errores equivalentes de
      conexión/throttling de `boto3`/`botocore` — nunca ante un rechazo
      explícito del proveedor (p.ej. el `RuntimeError` que ya lanza
      `LiwaNotificationSender` cuando LIWA responde `success: false`).
- [x] Dados N senders donde el primero lanza un error de conectividad, se
      prueba el segundo y su resultado (éxito o su propia excepción) es lo
      que ve quien llama.
- [x] Dados N senders donde el primero lanza un rechazo no reintentable, el
      segundo nunca se llama y la excepción original se propaga sin
      alterar.
- [x] Dados N senders que todos lanzan errores de conectividad, se propaga
      la última excepción.
- [x] La plantilla del mensaje OTP vive en un solo lugar en
      `app/domain/otp_sender.py` (o equivalente), y `LiwaOtpSender` se
      actualiza para usarla en vez de su propio string literal — el test
      existente de OTP en `tests/data_model/test_liwa_sender.py`
      (`test_liwa_otp_sender_arma_el_mensaje_con_el_codigo`) sigue pasando
      sin modificarse.
- [x] Tests nuevos cubren los cuatro escenarios de arriba (éxito directo,
      reintento tras conectividad, no-reintento tras rechazo, agotamiento de
      la cadena) con senders falsos — sin red real.

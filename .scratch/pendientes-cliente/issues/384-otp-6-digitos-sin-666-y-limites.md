# 384 — OTP de clientes: 6 dígitos sin "666" y límites por teléfono

**Pedido original (Jesús):** "el OTP debe ser de max 6 dígitos, omite el 666 en cualquier orden (al inicio, en el medio o al final)" (hallazgo 2).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- Código de 6 dígitos; nunca contiene la secuencia "666" en ninguna posición.
- Campo con `autocomplete="one-time-code"` e `inputmode="numeric"`: el celular ofrece pegar el código del SMS.
- Vida 5 minutos, 3 intentos por código; un código nuevo invalida los anteriores del mismo teléfono.
- Máximo 3 códigos por teléfono por hora y 6 por día; pasado eso, mensaje amigable y espera. La respuesta sigue sin
  revelar si el teléfono es elegible.

## Verificación

- `tests/web/test_otp_limites_por_telefono.py` (7, fallaban antes) + `tests/browser/test_otp_autocompletado.py` (2): 6 dígitos sin "666" (20.000 códigos generados), 3 intentos, 3 códigos/hora y 6/día por teléfono con el mismo mensaje para clientes y no clientes, 6 casillas con `autocomplete="one-time-code"` que reparten el código pegado. `test_rate_limit.py` y `test_otp_service.py` ajustados a propósito (fijaban la regla vieja).

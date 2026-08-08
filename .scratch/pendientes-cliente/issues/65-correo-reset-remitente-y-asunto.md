# 65 — Correo de recuperación: ajustar remitente y asunto

**Pedido original (cliente):** "Actualiza para el remitente para que use
este texto 'PaqueteX - Papyrus'. Remplaza este texto 'Restablece tu
contraseña de PAQUETEX' por 'Restablece tu contraseña de PaqueteX'. con
esto finalizaremos la seccion de login."

**Status:** implementado

## Contexto

Ajuste directo sobre [[64]] -- dos textos puntuales, sin cambios de
comportamiento.

## Implementación

- `app/domain/smtp_email_sender.py`: `_NOMBRE_REMITENTE` = "PaqueteX -
  Papelería Papyrus" → "PaqueteX - Papyrus".
- `app/web/routes/password_reset.py`: `_ASUNTO_RESET` = "Restablece tu
  contraseña de PAQUETEX" → "Restablece tu contraseña de PaqueteX".

## Verificación

- `tests/data_model/test_smtp_email_sender.py`: assertion del remitente
  decodificado actualizada al nuevo texto.
- Suite completa (`tests/data_model tests/web`): 642/642, sin
  regresiones.
- Pendiente: confirmar en `test.papyrus.com.co` con un restablecimiento
  real.

Con esto el cliente da por cerrada la sección de login (`/ingresar`,
`/entrar`, recuperación de contraseña de staff).

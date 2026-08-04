# 14 — Flujo OTP completo: restricción, latencia, casillas, redirects

**Pedido original (cliente, sesión de `/grilling` sobre `/entrar`):** ver
transcripción — resumen de decisiones abajo.

**Vistas:** `auth/customer_login.html`, `auth/customer_verify.html`,
`auth/entrar.html` (tab cliente) + rutas `customer_auth.py`, `auth.py`.

**Status:** verificado

## Decisiones acordadas en grilling

1. **Restricción de envío**: solo se manda OTP a teléfonos que existan en
   la BD (Persona) y tengan ≥1 Paquete en estado RECIBIDO. Mensaje
   genérico igual en ambos casos (no revela si el teléfono existe) —
   mismo principio que login de staff.
2. **Latencia**: mismo patrón async que `/anunciar` (responder ya,
   mandar SMS de fondo vía `BackgroundTasks`) — acepta que si el envío
   falla de verdad, no hay error visible (igual que las notificaciones
   de evento).
3. **Casillas del código**: 2 campos de 1 dígito cada uno (el código ya
   es de 2 dígitos), autoavance al escribir, auto-envío al completar el
   segundo dígito.
4. **Máximo de intentos**: ya existe (`max_intentos=5` en
   `OtpCliente`/`otp_service.py`), sin cambios.
5. **Redirects**:
   - Éxito de verificación → `/mis-datos` (hoy va a `/otp/perfil`).
   - Éxito de `/otp/solicitar` → redirige a `GET /otp/verificar?telefono=...`
     (ruta nueva) en vez de responder directo ahí — evita el problema de
     "reenviar formulario" al recargar. El caso de error se queda igual
     (consistente con el resto del sitio, ninguna otra ruta redirige en
     error).
   - Login de staff exitoso → `/paquetes` (hoy va a `/mi-sesion`).

## Qué se hizo

- `elegible_para_otp` en `otp_service.py` — filtra por Paquete RECIBIDO
  con `announced_by_phone` o `recipient_phone` igual al teléfono
  canónico. `preparar_otp` devuelve `None` (sin crear registro) si no es
  elegible; la ruta responde con la misma redirección genérica en ambos
  casos (anti-enumeración).
- `enviar_en_segundo_plano` + `BackgroundTasks.add_task` en
  `customer_auth.py` — el POST a `/otp/solicitar` ya no espera el envío
  real del SMS.
- `customer_verify.html` reescrita con 2 casillas de 1 dígito
  (autoavance vía JS + auto-envío con `form.requestSubmit()` al
  completar la segunda).
- Redirects: `/otp/solicitar` (éxito) → `GET /otp/verificar?telefono=...`;
  verificación correcta → `/mis-datos`; login de staff → `/paquetes`.
- Efecto secundario aceptado explícitamente por el cliente: la
  elegibilidad RECIBIDO-only es ahora la única forma de "convertirse en
  cliente" — un residente que solo anunció (sin que staff reciba el
  paquete) no puede entrar a `/mis-datos` todavía. Confirmado como
  comportamiento intencional, no una regresión.

## Verificación

- [x] Tests (`test_otp_service.py`, `test_customer_auth.py` y los 4
      `_login_cliente` helpers afectados en `test_layout.py`,
      `test_customer_verify.py`, `test_mis_paquetes.py`, `test_auth.py`)
      confirman la restricción y el envío async.
- [x] Prueba interactiva (Playwright) contra `test.papyrus.com.co`, con
      un teléfono elegible real (`+573009998877`, tiene Paquete
      RECIBIDO): solicitar código redirige a `/otp/verificar`; primer
      dígito hace saltar el foco a la segunda casilla; segundo dígito
      dispara el auto-envío (confirmado por el toast "Código inválido o
      expirado." del servidor — no se usó el código real por privacidad,
      ya que el OTP llega por SMS real a un teléfono de un cliente real
      y no pasa por `SMS_OVERRIDE_NUMBER` a propósito, ver docstring de
      `otp.py`). Redirects a `/mis-datos` y `/paquetes` confirmados por
      inspección de código (`auth.py:85`, `customer_auth.py:125`), no
      interactivamente — habría requerido el código real.
- [x] Suite de tests sin regresiones (437 passed).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.

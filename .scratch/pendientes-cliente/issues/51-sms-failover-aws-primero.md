# 51 — Failover de SMS/OTP: AWS SNS pasa al frente de la cadena

**Pedido original (cliente):** "por ahora vamos a utilizar aws" (en
respuesta a "estoy teniendo problemas con twilio y los mensajes de texto,
como funciona el failover").

**Status:** implementado

## Contexto

El cliente reportó problemas con Twilio. Se explicó el mecanismo de
failover (`sms_failover.py`: reintenta con el siguiente proveedor SOLO ante
falla de conectividad -- timeout, 5xx, 401/403 -- nunca ante un rechazo
explícito, para no arriesgar un envío duplicado) y se confirmó que en
`test.papyrus.com.co` los tres proveedores (LIWA, Twilio, AWS SNS) están
configurados. Se detectó además que el envío en segundo plano (tanto
notificaciones como OTP) traga cualquier excepción SIN loguear nada --
punto ciego real para diagnosticar, señalado al cliente pero NO corregido
en este pedido (no se pidió, fuera de alcance de este cambio puntual).

Aclarado el alcance con el cliente: reordenar la cadena para que AWS se
pruebe primero, dejando LIWA y Twilio como respaldo si AWS llega a fallar
por conectividad -- no desactivar los otros dos por completo (se descartó
la opción de quitarles las credenciales, para no perder la red de
seguridad).

## Implementación

Orden de precedencia cambia de **LIWA → Twilio → SNS** a **AWS SNS → LIWA →
Twilio**, en los dos puntos donde se arma la cadena (mismo mecanismo, dos
listas independientes -- una por canal):
- `app/web/notifications.py::_sender_base()` (notificaciones de evento de
  Paquete).
- `app/web/otp.py::get_otp_sender()` (envío del código OTP).

Puro reorden de la lista de candidatos que ya recibe
`sms_failover.construir_sender()` -- ese dispatch es agnóstico de proveedor
y de orden, arma la cadena con los que estén completamente configurados en
el orden que se le pase. Sin cambios en `sms_failover.py` ni en ninguno de
los 3 conectores (`liwa_sender.py`, `twilio_sender.py`, `sns_sender.py`).

Actualizados los tests que fijaban el orden anterior en sus aserciones
(`test_notifications.py`, `test_otp_wiring.py`) -- incluida la reescritura
de un test que simulaba "LIWA y Twilio caídos, SNS entrega" (ya no aplica
con SNS primero) a su espejo correcto "SNS y LIWA caídos, Twilio entrega".

## Verificación

630 tests pasan (mismo total que antes -- se reescribieron aserciones
existentes, no se agregaron tests nuevos).

Desplegado en `test.papyrus.com.co` (2026-08-06). Pendiente: confirmar en
vivo que el próximo envío real (SMS/OTP) sale por AWS SNS.

# 286 — SMS no llegaba pese a que AWS confirmó la salida del sandbox

**Pedido original (cliente):** "Perfecto, me informan de aws que ya se
soluciono lo relacionado a los mensajes sms y el sandbox, verifica y
realiza pruebas con el numero 3002596319" → (no llegó) → "no ha
llegado, corrije lo relacionado a las credenciales, actualiza lo
necesario" → (envío directo por AWS CLI SÍ llegó) "Sí me llegó"

**Status:** diagnosticado -- causa raíz encontrada y confirmada;
corrección de código (logging) implementada; **falta la corrección de
infraestructura, fuera de mi alcance (ver Seguimiento)**.

## Investigación

1. Confirmado por AWS CLI (cuenta `172460160630`, usuario `Antigravity`,
   permisos de gestión/sandbox, sin `sns:Publish`): la cuenta SÍ salió
   del sandbox de SMS -- `aws sns get-sms-sandbox-account-status
   --region us-east-1` → `IsInSandbox: false`, `ACCOUNT_TIER: PRODUCTION`.
   El número `+573002596319` no está en la lista de opt-out.
2. Primera prueba (vía la app real, `/otp/solicitar` en
   test.papyrus.com.co): el servidor aceptó la solicitud (avanzó a la
   pantalla de código) pero el SMS **no llegó**. Como el envío es
   best-effort (`enviar_en_segundo_plano`, `except Exception: pass`,
   sin logging), no había ningún rastro de por qué.
3. Para aislar "¿es AWS o es la app?": permiso temporal `sns:Publish`
   a `Antigravity`, envío DIRECTO por AWS CLI (bypaseando la app por
   completo) -- **sí llegó** ("Sí me llegó"). Permiso temporal retirado
   después de la prueba.
4. Esto aísla el problema: **AWS funciona, la app/su configuración no.**
5. **Causa raíz encontrada**: el estado del sandbox de SMS es **por
   región**, no de cuenta completa. Se probaron 10 regiones -- SOLO
   `us-east-1` salió del sandbox:
   ```
   us-east-1: false   us-west-1: true   sa-east-1: true       eu-central-1: true
   us-east-2: true    us-west-2: true   eu-west-1: true       ca-central-1: true
                                          ap-southeast-1: true  ap-southeast-2: true
   ```
   Si el `AWS_REGION` configurado en el `.env` del servidor desplegado
   es distinto de `us-east-1` (o si alguna otra variable de credenciales
   ahí está mal), los envíos vía `SnsOtpSender`/`SnsNotificationSender`
   fallan silenciosamente contra una región todavía en sandbox.

## Corrección de código (implementada)

`app/web/otp.py::enviar_en_segundo_plano` y
`app/web/notifications.py::enviar_en_segundo_plano`: agregado
`logger.exception(...)` en el `except` -- antes tragaba la excepción
sin dejar ningún rastro. Se corrigió también el razonamiento
desactualizado del comentario original ("no hace falta loguear un
proveedor caído a mitad de failover"): `FailoverSmsSender` (ver
`sms_failover.py`) solo deja propagar una excepción cuando TODOS los
proveedores fallaron -- para cuando la excepción llega hasta acá, el
mensaje YA no salió por ningún lado, nunca es un caso transitorio de
failover en curso. Este blind spot fue la razón por la que diagnosticar
esto tomó horas de investigación manual por AWS CLI en vez de una
revisión de logs de 2 minutos.

## Seguimiento (fuera de mi alcance -- necesita al cliente)

No tengo acceso SSH/Lightsail/CloudTrail al servidor de
test.papyrus.com.co, así que no puedo confirmar ni corregir
directamente qué `AWS_REGION`/credenciales tiene cargadas hoy. Se
generó un par de credenciales frescas para el usuario IAM dedicado
(`paquetex-sns-publisher`, permiso exclusivo `sns:Publish`) para
descartar dudas sobre la llave actual -- entregadas al cliente por
canal aparte (no en este archivo, es un secreto). Pendiente que el
cliente (o quien tenga acceso al servidor):

1. Confirme/corrija `AWS_REGION=us-east-1` en el `.env` del servidor
   (es el único valor correcto hoy).
2. Opcionalmente, actualice `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`
   con el par nuevo generado (o confirme que el actual ya es el
   correcto).
3. Reinicie la app (`docker compose restart app` o equivalente) para
   que tome el cambio.
4. Confirme con una prueba real (`/otp` con un teléfono propio, o
   "Enviar prueba" en `/administracion/notificaciones` -- pestaña SMS,
   necesita rol ADMIN) que el SMS ya llega solo.

## Verificación

Suite de tests de las áreas tocadas (`test_notifications`,
`test_otp_wiring`, `test_entrar`, `test_auth`,
`test_admin_notificaciones`, `test_customer_verify`,
`test_mis_paquetes`, `test_customer_auth`, `test_layout`): 221 passed,
sin regresiones.

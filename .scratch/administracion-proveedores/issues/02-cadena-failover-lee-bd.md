# 02 — La cadena de failover real lee la configuración de la base de datos

**What to build:** el punto donde esta feature empieza a tener efecto real en los
envíos — `_sender_base()` (`app/web/notifications.py`) y `get_otp_sender()`
(`app/web/otp.py`) dejan de recorrer una lista literal fija en código
(`[(sns_habilitado(), Sns...), (liwa...), (twilio...)]`) y en su lugar arman esa
misma lista de candidatos consultando `proveedor_config_service` (ticket 01) para el
orden y el habilitado, combinado con el `.configurado()`/`.sns_habilitado()` de cada
proveedor existente — un proveedor entra a la cadena SOLO si las dos condiciones son
ciertas a la vez (habilitado en BD Y con credenciales completas en `.env`).
`construir_sender()` (`app/domain/sms_failover.py`) no cambia de forma en absoluto —
sigue recibiendo exactamente `[(bool, sender), ...]`.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 17, 18; Implementation
Decisions "Refactor de la cadena de failover existente").

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] `_sender_base()` arma su lista de candidatos leyendo el orden/habilitado desde
      `proveedor_config_service` en vez de la constante fija, preservando el
      requisito de que cada proveedor también esté `.configurado()`/
      `.sns_habilitado()` para entrar a la cadena.
- [ ] `get_otp_sender()` hace el mismo cambio, en `app/web/otp.py`.
- [ ] Un proveedor habilitado en BD pero SIN credenciales completas en `.env` no
      entra a la cadena — sin error, mismo comportamiento que hoy ante una variable
      faltante.
- [ ] Un proveedor deshabilitado en BD nunca entra a la cadena aunque tenga
      credenciales completas.
- [ ] `construir_sender()` no se modifica — sus tests existentes
      (`tests/data_model/test_sms_failover.py`) siguen pasando sin cambios.
- [ ] Test que siembra la tabla con un orden DISTINTO al histórico de código (ej.
      Twilio primero) y verifica que `_sender_base()`/`get_otp_sender()` arman la
      cadena en ESE orden — prueba que el refactor de verdad lee la BD y no dejó un
      fallback oculto a la constante vieja.
- [ ] Suite completa de `tests/web/test_notifications.py` y el equivalente de
      `otp.py` sigue pasando (extendida, no reemplazada) — incluye el caso fail-closed
      existente de `StagingOverrideSender`.

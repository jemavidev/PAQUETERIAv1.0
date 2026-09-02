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

**Status:** verificado

- [x] `_sender_base()` arma su lista de candidatos leyendo el orden/habilitado desde
      `proveedor_config_service.armar_candidatos()` en vez de la constante fija,
      preservando el requisito de que cada proveedor también esté `.configurado()`/
      `.sns_habilitado()` para entrar a la cadena.
- [x] `get_otp_sender()` hace el mismo cambio, en `app/web/otp.py`.
- [x] Un proveedor habilitado en BD pero SIN credenciales completas en `.env` no
      entra a la cadena — sin error (verificado con
      `test_armar_candidatos_habilitado_en_bd_pero_sin_credenciales_excluye`).
- [x] Un proveedor deshabilitado en BD nunca entra a la cadena aunque tenga
      credenciales completas (verificado a nivel service y en ambos wirings).
- [x] `construir_sender()` no se modifica — `sms_failover.py` no aparece en el diff,
      sus tests existentes pasan sin cambios.
- [x] Test que siembra la tabla con un orden DISTINTO al histórico (Twilio primero) y
      verifica que `_sender_base()`/`get_otp_sender()` arman la cadena en ESE orden —
      presente en los tres niveles (service, notifications.py, otp.py).
- [x] Suite completa de `tests/web/test_notifications.py` y `test_otp_wiring.py` sigue
      pasando (extendida: 11+9 tests existentes actualizados para pasar `db_session`
      explícito, +4 tests nuevos) — incluye el caso fail-closed de
      `StagingOverrideSender`.

**Decisión de diseño no explícita en el ticket, documentada y testeada:** un
proveedor del catálogo SIN fila en `ProveedorConfig` (caso borde -- la migración 0037
siempre siembra los tres de SMS) se asume `habilitado=True` por defecto -- mismo
comportamiento implícito que existía antes de esta feature. Sin esto, agregar un
proveedor nuevo al catálogo en el futuro lo dejaría mudo hasta que alguien recuerde
también prenderlo en la BD, y además habría roto la mayoría de los tests existentes de
`test_notifications.py`/`test_otp_wiring.py` (que no siembran datos explícitos, solo
monkeypatchean variables de entorno).

**Code review** (Standards + Spec): 1 hallazgo confirmado (imports locales duplicados
en 4 tests nuevos), corregido antes de commitear. Spec: 0 faltantes, 0 scope creep.

**Verificación:** suite completa (1280 passed) tras los fixes del code review.

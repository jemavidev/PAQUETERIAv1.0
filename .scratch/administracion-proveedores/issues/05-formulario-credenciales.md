# 05 — Formulario de credenciales en la pantalla + auditoría de campo cambiado

**What to build:** la parte de `/administracion/proveedores` donde Jesús realmente
escribe una credencial nueva (rotar un token, cargar una API key) — cierra el pedido
original completo: gestionar TODA la configuración de proveedores desde formularios,
sin editar `.env` a mano por SSH.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 6-11, 13, 14;
Implementation Decisions "Formulario de credenciales").

**Blocked by:** 03, 04

**Status:** implementado -- sin desplegar; el servidor real necesita también el
ticket 06 (script remoto + llave restringida) para que un guardado real funcione,
no solo devuelva el error de configuración incompleta.

- [x] Cada proveedor muestra un campo por variable declarada en su catálogo (ticket
      01): `type=password` para las marcadas `secreto=True`; `tipo="booleano"`
      (`AWS_SNS_SMS_ENABLED`, `SMTP_USE_TLS`, `SMTP_USE_SSL`) se muestra como
      `<select>` de 3 estados (No cambiar / true / false) en vez de texto libre --
      hallazgo de code review, el catálogo (ticket 01) ya prometía que `tipo`
      gobernaría esto.
- [x] Un campo de credencial ya configurada muestra un placeholder fijo ("••••
      configurado", o "No cambiar (configurado: sí/no)" para los booleanos) — NUNCA
      el valor real; la pantalla solo hace `bool(os.environ.get(variable))`.
- [x] Campo vacío (o `<select>` en "No cambiar") = no cambiar esa credencial — solo
      los campos con contenido nuevo entran a `cambios` (una sola lista de
      `_CambioCredencial`, no dos colecciones paralelas).
- [x] Guardar espera la confirmación real (síncrono) de `aplicar_credenciales_
      proveedor` (ticket 04) antes de responder. Si falla, error tal cual, la
      credencial anterior sigue activa (verificado: `os.environ` no cambia), y
      habilitado/orden del MISMO submit sí se aplica igual (decisión explícita,
      documentada en el módulo -- son operaciones independientes).
- [x] Cambio de credencial exitoso → `ProveedorCredencialHistorial` (tabla NUEVA,
      migración 0038, separada de `ProveedorConfigHistorial`) con SOLO canal/
      proveedor/campo/quién/cuándo — nunca el valor.
- [x] No se construyó mecanismo de prueba propio — "Enviar prueba" de
      `/administracion/notificaciones` sigue siendo la vía de verificación en vivo.
- [x] `tests/web/test_admin_proveedores.py` (+7 tests): éxito con SSH mockeado deja
      auditoría solo del nombre; fallo muestra error sin auditoría, sin filtrar el
      valor sometido, y sin tocar `os.environ`; campo vacío no llama al mecanismo;
      campo booleano se renderiza como `<select>` y su valor sí viaja al mecanismo
      cuando se completa.

**Code review** (Standards + Spec): 1 hallazgo confirmado por los dos ejes —
`CampoProveedor.tipo` (comprometido en el docstring del ticket 01: "gobierna el
input que arme la Fase 2") se estaba ignorando, los 3 campos booleanos quedaban como
texto libre sin validar -- corregido con el `<select>` de 3 estados. De paso, la
etiqueta de `AWS_SNS_SMS_ENABLED` pasó de "Habilitado" a "Bandera AWS_SNS_SMS_
ENABLED" (se confundía visualmente con el toggle de habilitado en BD, aunque son dos
conceptos distintos). Data Clump `cambios`/`campos_cambiados` consolidado en una
sola lista de `_CambioCredencial` (NamedTuple). Spec: 0 scope creep, no tocó
`app/infra/deploy_ssh.py` ni construyó el script remoto.

**Verificación:** suite completa (1308 passed) + prueba manual en el navegador local
del camino de error real (sin mocks): guardar una credencial sin `DEPLOY_SSH_HOST`/
`DEPLOY_SSH_KEY_PATH` configurados falla con el mensaje exacto de configuración
incompleta, sin dejar auditoría -- confirma la tubería completa de punta a punta.

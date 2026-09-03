# 293 — El toggle de AWS SNS sincroniza sola la bandera `AWS_SNS_SMS_ENABLED`

**Pedido original (cliente):** "Sigo cin entender porque me muestras esto
(Bandera AWS_SNS_SMS_ENABLED, Usar TLS, Usar SSL) aparece no cambiar, pero
eso deberia ser un toggle o en su defecto 'Bandera AWS_SNS_SMS_ENABLED' no
deberia ser visible" — seguido, tras explicarle que hay dos mecanismos de
"encendido" distintos conviviendo en la misma tarjeta (el toggle
`habilitado` de BD del feature nuevo, y la variable de entorno histórica
que ya leía `sns_habilitado()` desde antes), de: "Para este caso especifico
el toggle debe hacer las 2 cosas".

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

Solo para `AWS_SNS_SMS_ENABLED` (no para `SMTP_USE_TLS`/`SMTP_USE_SSL` --
esos son configuración real de conexión, no una bandera de encendido
redundante con ningún toggle):

- El campo deja de mostrarse en el formulario (`CampoProveedor.oculto=True`,
  nuevo en el catálogo) -- sigue en el allowlist SSH, solo se le esconde al
  admin como input editable.
- El toggle `habilitado` de AWS SNS lo sincroniza solo
  (`ProveedorInfo.sincroniza_habilitado_con="AWS_SNS_SMS_ENABLED"`) --
  `"true"`/`"false"` en `.env` real, vía el mismo mecanismo SSH de
  siempre.
- Solo se sincroniza cuando el valor de `habilitado` REALMENTE cambia entre
  el guardado anterior y el nuevo -- nunca en cada submit, para no
  reiniciar el servidor sin necesidad si el admin solo reordena otros
  proveedores.
- Un POST manual con el nombre de la variable oculta se ignora (defensa en
  profundidad) -- solo la sincronización automática puede tocarla.

## Implementación

`proveedores_catalogo.py`: `CampoProveedor.oculto`,
`ProveedorInfo.sincroniza_habilitado_con`. `admin_proveedores.py`:
`_filas_proveedores` filtra `oculto` de lo que se renderiza;
`admin_proveedores_guardar` detecta el cambio de `habilitado` (comparando
contra el valor efectivo ANTES de guardar) y agrega la sincronización a la
misma lista de `_CambioCredencial` que ya usan las credenciales manuales --
una sola llamada a `aplicar_credenciales_proveedor`, un solo reinicio.

## Verificación

Suite completa: 1327 passed. `tests/web/test_admin_proveedores.py`: 33
passed (incluye: campo ya no visible; apagar/prender el toggle sincroniza
"false"/"true"; guardar sin cambiar el toggle NO dispara el mecanismo SSH;
un POST manual con el nombre del campo oculto se ignora, incluso cuando
coincide con un cambio real de `habilitado`). Code review (Standards +
Spec) sin hallazgos pendientes tras extraer `_config_por_clave` y mover la
documentación de `sincroniza_habilitado_con` al docstring de la clase.
Desplegado a `test.papyrus.com.co` el 2026-09-03 (commit `f5de6d0`, repo de
deploy -- había quedado sin sincronizar desde su implementación). Pendiente
confirmar en vivo.

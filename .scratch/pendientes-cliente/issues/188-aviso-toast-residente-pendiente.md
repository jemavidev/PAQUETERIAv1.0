# 188 — Reabrir "Corregir destinatario" no bastaba de señal: falta un aviso explícito

**Pedido original:** "necesito que en localhost, realices todo un set de pruebas de escritorio, ya
que se sigue presentando el mismo problema y nada que lo puedes corregir, analiza lo que se hace y
veras" — seguido de evidencia concreta: "acabo de probar con FANTASMA 1 A7MA y sigue el problema
aparece en un lado como asignado a una torre y apartamento, pero en otro lado no aparece... No
aparece en residentes pero si se visualiza en paquete."

**Status:** implementado

## Diagnóstico

[[186]] y [[187]] arreglaron el bug real (paquete con unidad asignada pero sin ningún Ocupante
vinculado) redirigiendo a reabrir el modal "Corregir destinatario" con candidatos reales ya
resueltos. Verificado por curl tres veces con tres paquetes de prueba distintos del cliente (RAFA T
26NU, ESTE ES UN CLIENTE FANTASMA 5AWR, FANTASMA 1 A7MA) que el modal SÍ se reabre sin `hidden` y SÍ
ofrece candidatos reales (ej. ANGELICA ARRAZOLA) — el fix funciona a nivel de código/HTTP.

Pero el cliente siguió reportando el mismo síntoma visible con casos nuevos. La causa no era un bug
de código sino de señal: un modal que se reabre solo, sin ningún aviso que lo acompañe, no se nota
en uso real de escritorio — el staff no completaba el paso pendiente (elegir candidato o llenar "+
Nuevo residente") y seguía de largo, dejando el paquete en el mismo estado a medio asociar.

## Cambio

- `packages.py`: nueva constante `_AVISO_RESIDENTE_PENDIENTE` con el texto fijo del aviso (no texto
  libre por query param — evita cualquier duda de inyección). Los dos redirects de [[186]]/[[187]]
  (`assign_apartment_action`, `receive_action`) ahora agregan `&aviso=residente_pendiente` a la URL
  de vuelta. La ruta `GET /paquetes` (`packages_list`) traduce ese código a texto server-side
  (`aviso_texto = _AVISO_RESIDENTE_PENDIENTE if aviso == "residente_pendiente" else None`) y lo pasa
  a `_render_lista` → contexto de plantilla.
- `packages/list.html`: `{% if aviso %}{{ toast(aviso, variant='warning', duracion_ms=none,
  id='toast-aviso') }}{% endif %}`, junto al toast de error ya existente. `variant='warning'` (toast
  naranja, `role="alert"`) y `duracion_ms=none` (sin auto-cierre, el staff debe cerrarlo a mano) para
  que sea imposible no notarlo, a diferencia del toast de éxito por defecto que se auto-oculta a los
  5s.

## Verificación

- 2 tests existentes actualizados (`test_recibir_declara_apartamento_sin_residente_redirige_a_corregir`,
  `test_asignar_apartamento_sin_nuevo_residente_redirige_a_corregir`): el `Location` ahora incluye
  `&aviso=residente_pendiente`, y siguiendo el redirect se confirma `id="toast-aviso"` y el texto del
  aviso presentes en el HTML.
- 1 test nuevo: `test_aviso_desconocido_en_query_no_renderiza_toast` — guard de que `aviso` es un
  código controlado (whitelist de un solo valor), no texto libre; cualquier otro valor en la URL no
  produce ningún toast.
- Los guards existentes (`..._con_nuevo_residente_no_redirige_a_corregir`) ya confirman que cuando
  SÍ se resolvió un residente en el mismo envío, el redirect va a `/paquetes` sin el parámetro
  `aviso` — sin cambios de comportamiento en ese camino.
- Suite completa de `tests/web/test_packages.py`: 187 passed.
- Pendiente: verificar visualmente en localhost (o test.papyrus.com.co tras deploy) que el toast
  naranja se ve correctamente posicionado y no se auto-cierra — no hay acceso a navegador en este
  entorno, solo verificación por curl/HTML.

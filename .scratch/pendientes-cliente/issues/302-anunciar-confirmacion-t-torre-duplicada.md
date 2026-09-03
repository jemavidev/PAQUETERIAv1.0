# 302 — `/anunciar` confirmación: "T TORRE 2" duplicaba el prefijo

**Pedido original (cliente):** "despues de anunciar un paquete exitosamente
de un residente que tenga asociado una direccion, la notificacion del
apartamento esta mala, tiene una letra T de mas asi como se muestra:
(Apartamento EL CLUB · T TORRE 2 · APT 302) debe decir (Apartamento EL CLUB
· TORRE 2 · APT 302), sin la letra T antes de la palabra TORRE"

**Status:** implementado

## Diagnóstico (`/diagnosing-bugs`)

Mismo patrón exacto que [[152]] (`snapshot_torre` ya trae el prefijo del
catálogo, "TORRE 2") -- pero acá era un `' · T '` literal concatenado ANTES
de pegar `snapshot_torre` sin pasar por el filtro `torre_sin_prefijo`
(`domain/paquete.py`), en un call site que [[152]] no cubrió.

4 hipótesis descartadas antes de tocar código (repro con Playwright/pytest
contra Postgres real):
- Catálogo corrupto (`apartamentos.torre` con el valor ya duplicado) --
  descartado, `apto.torre == 'TORRE 2'` limpio.
- `snapshot_torre` corrupto al anunciar -- descartado,
  `paquete.snapshot_torre == 'TORRE 2'` limpio.
- `torre_sin_prefijo` roto -- descartado, `torre_sin_prefijo('TORRE 2') ==
  '2'`, correcto.
- Confirmada: bug 100% de template, un solo call site
  (`announce/confirmacion.html:18`).

## Fix

`announce/confirmacion.html` -- `' · T ' ~ snapshot_torre` → `' · TORRE ' ~
(snapshot_torre|torre_sin_prefijo)`, mismo patrón que ya usan `/consultar`,
`/paquetes`, `/mis-paquetes` desde [[152]]. De paso, corregido el mismo
literal en el bloque de documentación (comentario, no ejecutable) de
`components/_confirmacion.html` para que el ejemplo no siga mostrando el
patrón roto.

## Verificación

- Desplegado a `test.papyrus.com.co` 2026-09-03 (CI `jemavidev/PaqueteX` run
  33810514014, tests + deploy success). Sin verificación visual en vivo con
  un anuncio real ahí (a propósito -- habría creado un Paquete de prueba
  espurio en el servidor compartido); confiado en la suite local + el
  mismo código ya corriendo en producción.
- Regression test agregado a la suite real (no un test descartable):
  `test_confirmacion_muestra_apartamento_cuando_el_anunciante_ya_tiene`
  (`tests/web/test_announce.py`) -- reproducido en rojo antes del fix
  (`assert "T TORRE 1" not in r.text` fallaba con el texto exacto del bug),
  verde después.
- `tests/web/test_announce.py` + `tests/data_model/test_announce_paquete.py`:
  56 passed.

## Post-mortem

Segunda vez que aparece este patrón exacto (issue 152 ya lo corrigió en 4
lugares con `torre_sin_prefijo`, pero como filtro opcional que cada template
tiene que acordarse de aplicar). Recomendación para `/improve-codebase-
architecture`: centralizar "Conjunto · TORRE X · APT Y" en un solo helper
(mismo espíritu que `etiqueta_torre_apto` de `customers_manage.py`) en vez
de que cada template concatene el string a mano -- eliminaría la clase de
bug entera, no solo este síntoma puntual.

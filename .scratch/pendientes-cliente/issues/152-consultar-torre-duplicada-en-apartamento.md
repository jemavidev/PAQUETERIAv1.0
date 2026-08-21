# 152 — `/consultar`: "Torre TORRE 10" duplicaba la palabra "Torre"

**Pedido original (cliente):**
"Para este ejemplo `/consultar?q=NME3` aparece la linea 'Apartamento EL CLUB
· Torre TORRE 10 · Apto 101' cuando en realidad debería decir 'Apartamento
EL CLUB · Torre 10 · Apto 101', la palabra 'TORRE' está de más" — seguido de
pedir que se revisara si el mismo problema aparecía en otras secciones de la
app.

**Status:** implementado

## Causa raíz

`snapshot_torre` guarda el label completo del catálogo de Torres, con el
prefijo incluido (ej. `"TORRE 10"`, ver `components/_inputs.html` — las
opciones del picker son literalmente `'TORRE 1'`, `'TORRE 2'`, etc). Varios
templates anteponen su propio `"Torre "` literal antes de interpolar ese
valor, así que el resultado queda `"Torre TORRE 10"`.

El bug ya se había encontrado y corregido una vez (issue 79, columna
"Dirección" de `/paquetes`, función `_direccion_corta` en
`web/routes/packages.py`), pero el fix nunca se propagó a los demás lugares
que tienen el mismo patrón de concatenación.

## Implementación

- Nueva función `torre_sin_prefijo()` en `domain/paquete.py` — única fuente
  de verdad del saneo (quita el prefijo `"torre"` case-insensitive), junto
  al modelo que define la columna `snapshot_torre`.
- Registrada como filtro Jinja (`torre_sin_prefijo`) en `web/templating.py`,
  mismo patrón que el filtro `hora_local` ya existente.
- `_direccion_corta` (`packages.py`, issue 79) refactorizada para reusar
  esta función en vez de duplicar la lógica `if torre[:5].lower()...` que
  tenía inline.
- Filtro aplicado en los 5 lugares que concatenaban `"Torre "` +
  `snapshot_torre` crudo:
  - `search/form.html` — fila "Apartamento" de `/consultar` (el reportado).
  - `search/form.html` — texto "Entregar a..." del modal de entrega en
    `/consultar` (visible solo staff, paquete RECIBIDO).
  - `packages/_resultados.html` — mismo texto "Entregar a..." en `/paquetes`
    (vista staff).
  - `customer/paquetes.html` — fila Torre/Apto de `/mis-paquetes`.
  - `components/_tarjetas.html` — componente de tarjeta actualmente sin uso
    en ningún template (huérfano); corregido por consistencia para que no
    arrastre el mismo bug si se retoma.

**Fuera de alcance (no es el mismo bug):** `customer/verify.html` (tab "Mi
apartamento") muestra "Torre" como etiqueta de campo separada del valor
(fila etiqueta/valor, no texto concatenado) — no produce el string
duplicado "Torre TORRE 10", es un patrón visual distinto. No se tocó.

## Verificación

- `tests/web/test_search.py`: nuevo test
  `test_torre_del_snapshot_no_duplica_el_prefijo_torre` — paquete con
  `snapshot_torre = "TORRE 10"`, confirma `"EL CLUB · Torre 10 · Apto 101"`
  en la respuesta y `"Torre TORRE 10"` ausente.
- `tests/web/test_mis_paquetes.py`:
  `test_ubicacion_con_apartamento_muestra_conjunto_torre_apto` actualizado —
  antes fijaba el bug (`">TORRE 2</strong>"` esperado), ahora fija el
  comportamiento correcto (`"Torre <strong ...>2</strong>"`,
  `"TORRE 2"` ausente).
- Suite completa (`tests/data_model` + `tests/web`): 1028 passed.
- Pendiente: confirmar visualmente en `test.papyrus.com.co` tras desplegar.

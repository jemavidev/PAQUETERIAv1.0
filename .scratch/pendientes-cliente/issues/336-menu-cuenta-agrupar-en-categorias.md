# 336 — Menú de cuenta: agrupar ítems de Administración en categorías

**Pedido original (cliente):**
"necesito tu ayuda con lo relacionado a 'site-actions' y 'account-menu', de que
forma los item aqui contenidos puedes agruparlos o simplemente hacer que se vea
mejor o que se ingrese en una categoria y de esta se pueda entrar en varios, no
se de que forma podrias arreglar esto segun tu criterio de lo que se quiera
hacer"

**Status:** implementado

## Contexto

Para un ADMIN, `.account-menu-panel` (`cuenta_menu()`/`bloque_staff()` en
`base.html`) mostraba una lista plana de 10 enlaces sueltos (Mi perfil +
9 ítems de Administración) sin ninguna agrupación.

## Prototipo (skill `prototype`)

Se armaron 3 variantes en vivo sobre la app real vía `?menu_proto=A|B|C`
(cualquier página con sesión de staff), con una barra flotante para saltar
entre ellas:

- **A — Secciones**: mismo `.account-menu-block-label` que ya separa
  "Cliente"/"Personal", cortando la lista en 3 encabezados.
- **B — Acordeón**: cada categoría como `<details>` anidado, colapsado por
  defecto.
- **C — Categorías** (estilo Ajustes de iOS): el panel arranca con solo las 3
  categorías; tocar una reemplaza la vista por sus ítems + "← Volver".

El cliente eligió **C** ("se ve bien") — coincide con la frase literal del
pedido ("que se ingrese en una categoría y de esta se pueda entrar en
varios").

## Categorías (mismo contenido en las 3 variantes, solo cambiaba la navegación)

- **Cobros**: Tarifas de cobro, Motivos de anulación, Estadísticas de cobro
- **Datos y catálogos**: Conjunto, Contactos externos, Motivos de bloqueo,
  Migrar año
- **Equipo y comunicación** (renombrada desde "Personal y comunicación" del
  prototipo -- evita chocar con la etiqueta "Personal" que ya envuelve este
  bloque cuando un ADMIN también es residente, ver `base.html`): Perfiles,
  Notificaciones, Proveedores

"Mi perfil" queda fuera de las categorías (visible para todo staff, no solo
ADMIN, sin cambios).

## Implementación

- `base.html`, macro `bloque_staff()`: reemplazada la lista plana por el
  patrón de 2 niveles (botones de categoría → panel de ítems + volver),
  ganador del prototipo C. Se retiraron las variantes A/B, el parámetro
  `menu_proto`, el `<style>` condicional y la barra flotante -- solo queda
  la variante elegida, sin gating.
- Estilos nuevos (`.account-menu-cat-btn`, `.account-menu-cat-back`)
  agregados al `<style>` permanente de `base.html`, junto al resto de
  `.account-menu-*`.
- JS: listener delegado (categoría → panel, volver → lista) movido del
  bloque de prototipo al `<script>` permanente de `base.html`. Se agregó un
  listener de `toggle` sobre `.account-menu` para resetear el panel a la
  lista de categorías cada vez que el dropdown se cierra -- sin esto, cerrar
  el menú en medio de "Cobros" y reabrirlo después mostraba directo esa
  categoría en vez de arrancar limpio (bug encontrado en la propia
  implementación, no estaba en el prototipo porque ahí nunca se cerraba el
  panel entre comparaciones).
- El prototipo completo (3 variantes + barra flotante) se preserva en la
  rama `prototype/menu-cuenta-categorias` -- no queda nada de eso en main.

## Verificación

- Smoke test con curl contra `localhost:8010` (login real como admin):
  `/paquetes` sirve 200, panel trae los 3 botones de categoría
  (`data-cat-open="cobros|datos|equipo"`) y los 3 paneles de ítems
  (`data-cat-panel=...`), cero rastros de `proto-`/`menu_proto` en el HTML
  servido.
- `tests/web` completo corrido en local tres veces: la primera cayó en medio
  de una edición (estado transitorio inconsistente entre el macro
  `cuenta_menu` y su call site -- 6 fallos en cascada, ninguno real) --
  descartada. La segunda (código ya terminado) encontró un bug real: un
  comentario del `<script>` PERMANENTE de `base.html` (se manda en TODA
  página, tenga o no sesión de staff) decía "Cobros" -- `tests/web/
  test_search.py::test_consultar_entregado_sin_sesion_de_staff_no_muestra_el_cobro`
  verifica que la palabra "Cobro" nunca llegue a un `/consultar` público
  (evita filtrar el monto cobrado a alguien sin sesión de staff), y
  matcheaba contra el HTML completo, comentarios de JS incluidos.
  Reescrito el comentario sin esa palabra -- `test_search.py` completo (42
  tests) vuelve a pasar. Tercera corrida, suite completa: **1656 passed, 3
  failed** -- los 3 fallos son preexistentes, ajenos a este ticket
  (`test_announce.py::test_post_a_telefono_bloqueado_se_rechaza_sin_crear_paquete`,
  `test_bloquear_residente.py::test_autorizar_desbloqueo_habilita_el_estado`,
  `test_bloquear_residente.py::test_autorizar_desbloqueo_sin_estar_bloqueada_se_rechaza`
  -- 403 en vez de 400, dominio de bloqueo/desbloqueo de residentes; los
  archivos que tocan ese dominio -- `persona.py`, `persona_service.py`,
  `announce.py` -- ya estaban modificados sin commitear por otra sesión de
  Claude Code (`matt-28`) antes de que este ticket empezara). Cero fallos
  nuevos por este cambio.
- Pendiente: confirmar visualmente en `test.papyrus.com.co` (o
  `localhost:8010`) -- esta sesión no tiene navegador conectado.

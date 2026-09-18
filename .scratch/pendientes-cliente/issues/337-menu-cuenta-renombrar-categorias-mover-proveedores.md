# 337 — Menú de cuenta: renombrar categorías/ítems y reubicar Proveedores + Motivos de anulación

**Pedido original (cliente):**
"Necesito que para la seccion del header (class="account-menu-panel") renombres
algunas cosas como por ejemplo: 'Datos y catálogos' por 'Datos', 'Equipo y
comunicación' por 'Perfiles', 'Perfiles' por 'Usuarios', También cambia la
seccion de 'Proveedores' hasta lo que sera la nueva seccion de 'Datos'." +
mensaje de seguimiento: "Tambien mueve lo que es 'Motivos de anulación' hasta
la nueva seccion de 'Datos'" (mensaje llegó cortado a mitad de frase, se
confirmó el destino "Datos" vía pregunta directa).

**Status:** implementado

## Contexto

Sobre las 3 categorías introducidas en el issue 336 (`base.html`, macro
`bloque_staff()`), dentro de `.account-menu-panel`:

- Categoría `data-cat-open="datos"` ("Datos y catálogos") → **"Datos"**
- Categoría `data-cat-open="equipo"` ("Equipo y comunicación") → **"Perfiles"**
- Dentro de esa categoría, el ítem "Perfiles" (enlace `/administracion/personal`)
  → **"Usuarios"** (evita choque de nombre con la categoría que pasa a llamarse
  "Perfiles")
- El ítem "Proveedores" (enlace `/administracion/proveedores`) se **mueve** del
  panel "equipo"/Perfiles al panel "datos"/Datos.
- El ítem "Motivos de anulación" (enlace `/administracion/motivos-anulacion-cobro`,
  hoy en el panel "cobros") se **mueve** también al panel "datos"/Datos.

Cada `data-cat-open`/`data-cat-panel` (los atributos internos "cobros" /
"datos" / "equipo") se mantienen como están -- solo cambia el texto visible y,
para Proveedores y Motivos de anulación, en qué panel viven.

## Implementación

- `base.html`, macro `bloque_staff()`: solo texto visible (`<span>` de los
  botones de categoría, `enlace_menu()` de los ítems) y de qué `data-cat-panel`
  cuelga cada ítem -- los atributos `data-cat-open`/`data-cat-panel` ("cobros"
  / "datos" / "equipo") no cambian, así que el JS delegado (categoría→panel,
  volver→lista) sigue funcionando sin tocarlo.
- Botón de categoría `data-cat-open="datos"`: "Datos y catálogos" → "Datos"
  (label del botón y del "← Volver" del panel).
- Botón de categoría `data-cat-open="equipo"`: "Equipo y comunicación" →
  "Perfiles" (label del botón y del "← Volver" del panel).
- Ítem `/administracion/personal` (vivía en el panel "equipo"): "Perfiles" →
  "Usuarios".
- Ítem `/administracion/proveedores`: reubicado del panel "equipo" al panel
  "datos".
- Ítem `/administracion/motivos-anulacion-cobro`: reubicado del panel
  "cobros" al panel "datos" (pedido en un mensaje de seguimiento, confirmado
  vía pregunta directa tras llegar cortado).
- No hubo que tocar CSS (`tailwind.css`) -- ningún cambio de clase, solo texto
  y posición de bloques `{{ enlace_menu(...) }}` ya existentes.

## Verificación

- `tests/web/test_layout.py` (28 tests) y `tests/web/
  test_admin_contactos_externos.py` (7 tests) completos en local: **35
  passed**. Ninguno de los dos assertea el texto visible de las categorías ni
  de estos ítems (solo `href`), así que cubren que nada se rompió mecánicamente
  pero no reemplazan una revisión visual.
- Pendiente: confirmar visualmente en `localhost:8010` o
  `test.papyrus.com.co` -- esta sesión no tiene navegador conectado.

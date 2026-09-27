# 358 — `/administracion/contactos-externos`: botones "Descargar plantilla / Exportar CSV / Importar CSV" pasan a "Descargar / Exportar / Importar"

**Pedido original (Jesús):** "Necesito que para la vista de
/administracion/contactos-externos, cambien los nombres de estas etiquetas
'Descargar plantilla, Exportar CSV y Importar CSV' por 'Descargar, Exportar,
Importar'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Solo cambia el texto visible de los 3 botones de `admin/contactos_externos.html`.
- Cada uno conserva el nombre largo original como `title` (tooltip) para que
  "Descargar" no quede ambiguo.
- Las rutas, el formulario de import ("Importar" submit, ya se llamaba así) y
  el texto de ayuda del campo de archivo no se tocan.

## Verificación

- `test_botones_de_plantilla_tienen_las_etiquetas_cortas` y
  `test_botones_de_plantilla_conservan_el_nombre_largo_como_tooltip`.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

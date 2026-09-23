# 358 — `/administracion/contactos-externos`: botones "Descargar plantilla / Exportar CSV / Importar CSV" pasan a "Descargar / Exportar / Importar"

**Pedido original (Jesús):** "Necesito que para la vista de
/administracion/contactos-externos, cambien los nombres de estas etiquetas
'Descargar plantilla, Exportar CSV y Importar CSV' por 'Descargar, Exportar,
Importar'."

**Status:** implementado, pendiente confirmar visualmente

## Decisiones

- Solo cambia el texto visible de los 3 botones de `admin/contactos_externos.html`.
- Cada uno conserva el nombre largo original como `title` (tooltip) para que
  "Descargar" no quede ambiguo.
- Las rutas, el formulario de import ("Importar" submit, ya se llamaba así) y
  el texto de ayuda del campo de archivo no se tocan.

## Verificación

- `test_botones_de_plantilla_tienen_las_etiquetas_cortas` y
  `test_botones_de_plantilla_conservan_el_nombre_largo_como_tooltip`.

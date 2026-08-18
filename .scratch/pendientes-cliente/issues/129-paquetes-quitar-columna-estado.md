# 129 — `/paquetes`: quitar la columna "Estado"

**Pedido original (cliente):**
"En la vista de /paquetes remueve la columna de 'Estado'"

**Status:** verificado en test.papyrus.com.co

## Implementación

- `packages/_resultados.html`: se quitan el `<th>Estado</th>` y su
  `<td>{{ badge(p.estado) }}</td>` correspondiente en cada fila. Tabla
  pasa de 5 a 4 columnas: Cliente/Dirección/Fecha/Acciones.
- El estado NO desaparece del todo: el chip de código de acceso (dentro
  de la columna Cliente, issue 108/109) ya llevaba fondo con color por
  Estado; el modal "Ver" sigue mostrando el badge completo. `badge`
  sigue importado -- lo sigue usando ese modal.
- Docstring del archivo actualizado (columnas/motivo del retiro).

## Verificación

- `tests/web/test_packages.py`: `test_encabezados_de_columna_nuevos`
  actualizado -- ya no espera "Estado" entre los encabezados, agrega
  aserción explícita de que `>Estado<` no aparece.
- `tests/web/test_packages.py test_announce_new.py test_search.py`:
  161 + 88 passed, sin otras regresiones (el badge de estado en el
  modal "Ver" -- issue [[81]]/[[82]] -- se queda intacto, sus tests
  siguen pasando).
- Playwright contra el servidor local real: encabezados confirmados
  `['Cliente', 'Dirección', 'Fecha', 'Acciones']`.
- Suite completa: 1016 passed.
- Pendiente: deploy a test.papyrus.com.co.

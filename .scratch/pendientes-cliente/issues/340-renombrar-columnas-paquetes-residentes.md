# 340 — Renombrar columnas en `/paquetes` y `/residentes`

**Pedidos originales (cliente), 3 mensajes seguidos:**
1. "cambia el nombre de la columna 'Direccion' por 'Torre y Apartamento'"
   (en `/paquetes`)
2. "En la vista de /residentes cambia el nombre de la columna 'Teléfono de
   contacto' por 'Contacto'"
3. "Cambia la columna 'Nombre' o 'Cliente' por 'Residente', esto en las 2
   vistas /paquetes y /residentes"

**Status:** implementado, pendiente confirmar visualmente

## Implementación

- `packages/_resultados.html`: `<th>Dirección</th>` → `<th>Torre y
  Apartamento</th>` (mismo nombre que ya usaba esa columna en
  `/residentes`); `<th>Cliente</th>` → `<th>Residente</th>`.
- `customers_manage/_resultados.html`: `<th>Teléfono de contacto</th>` →
  `<th>Contacto</th>`; `<th>Nombre</th>` → `<th>Residente</th>`.
- Comentario de cabecera de `packages/_resultados.html` actualizado para
  no dejar desactualizado el registro histórico de issue 79 (que documentaba
  los nombres viejos).

## Tests

- `test_packages.py::test_encabezados_de_columna_nuevos` actualizado (los
  4 encabezados esperados cambiaron de nombre).
- Un comentario en `test_packages.py` (línea ~4073) actualizado por
  consistencia -- no afectaba ningún assert.
- Suite completa `test_packages.py` (230) + `test_customers_manage.py`
  (196): todo verde.

## Verificación

Pendiente confirmación visual del cliente.

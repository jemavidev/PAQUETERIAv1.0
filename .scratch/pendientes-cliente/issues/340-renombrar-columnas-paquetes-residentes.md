# 340 — Renombrar columnas en `/paquetes` y `/residentes`

**Pedidos originales (cliente), 3 mensajes seguidos:**
1. "cambia el nombre de la columna 'Direccion' por 'Torre y Apartamento'"
   (en `/paquetes`)
2. "En la vista de /residentes cambia el nombre de la columna 'Teléfono de
   contacto' por 'Contacto'"
3. "Cambia la columna 'Nombre' o 'Cliente' por 'Residente', esto en las 2
   vistas /paquetes y /residentes"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

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

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

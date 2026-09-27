# 363 — `/administracion/estadisticas-cobro`: quitar el select "Usuario" (`usuario_id`)

**Pedido original (Jesús):** "Remueve el select de 'usuario_id'".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

Test: `test_no_hay_filtro_por_usuario_y_el_parametro_se_ignora` en
`tests/web/test_admin_estadisticas_cobro.py` (reemplaza a los 2 tests que
cubrían el filtro por usuario en la ruta). Verificado además en el navegador
local: atajos y pills siguen actualizando en vivo, sin errores de consola.

## Contexto

`CODE/src/app/web/templates/admin/estadisticas_cobro.html` -- la barra de
filtros traía un `<select name="usuario_id">` ("Todos los usuarios" + un
miembro del staff) que acotaba los KPIs, "Por cliente / apartamento" y "Serie
diaria" a los cobros de una sola persona.

## Decisiones

- Se quita el select **y todo su cableado de la capa web**: el `<script>` que
  lo leía/escuchaba, el parámetro `usuario_id` de la ruta
  (`admin.py::admin_estadisticas_cobro`), `filtro_usuario_id` del contexto y
  la consulta `staff_lista` (que solo existía para poblar el select y se
  ejecutaba en cada carga completa).
- **Por qué también el parámetro de la ruta y no solo el control:** si el
  parámetro siguiera aceptándose, un enlace `?usuario_id=<uuid>` aplicaría un
  filtro que ningún control muestra ni permite quitar, y el fetch en vivo
  (que arma su URL solo desde los controles visibles) lo descartaría en
  silencio al primer clic -- un estado incoherente. Sin el parámetro, la
  vista queda totalmente determinada por lo que se ve.
- La tabla **"Por usuario" se queda**: sigue comparando a todo el staff.
- La capa de dominio no se toca (`FiltrosEstadisticasCobro.usuario_id` y su
  cobertura en `tests/data_model/test_cobro_service_integration.py`): sigue
  siendo una capacidad válida de la consulta, solo que ninguna pantalla la
  usa hoy. Volver a exponerla es agregar el control de nuevo.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

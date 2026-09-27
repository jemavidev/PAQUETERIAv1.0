# 17 — Retiro del servicio de estadísticas anterior y sus pruebas

**What to build:** con el tablero nuevo completo y ya siendo lo único que la pantalla usa, se retira todo
lo que quedó huérfano: el servicio de estadísticas orientado a listas (por cliente/apartamento, por
usuario, serie diaria paginada) y sus pruebas, dejando el código base sin caminos muertos.

**Blocked by:** 03 (una vez que Recaudo completo existe en el tablero nuevo, nada depende ya del
servicio anterior)

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: solo queda `estadisticas_tablero_service.py`)

- [ ] El servicio de estadísticas anterior (agregados por cliente/apartamento, por usuario, serie diaria
      paginada) y sus estructuras de datos exclusivas se eliminan del código de dominio.
- [ ] Las pruebas de dominio y de la ruta web que ejercitaban específicamente esas listas y su paginación
      se eliminan; cualquier caso que probara una regla de negocio TODAVÍA vigente (ej. semántica de un
      filtro por rango, por Tipo, o por Cobrado/Anulado) se conserva migrado a las pruebas del servicio
      nuevo, no se pierde.
- [ ] La suite completa de la pantalla y del módulo de cobro sigue en verde tras el retiro.
- [ ] No queda ninguna referencia en rutas, plantillas ni scripts al servicio anterior (una búsqueda del
      símbolo en el repo no encuentra usos vivos).
- [ ] El script de datos de demostración del ambiente local, que hoy imprime un resumen usando el
      servicio anterior, se actualiza para usar el servicio nuevo (o se le retira ese resumen) — se
      confirma corriéndolo contra el Postgres local y revisando que no falle.

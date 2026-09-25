# 408 — "Dashboard" en todas las referencias y enlaces (antes "Estadísticas de cobro")

**Pedido original (Jesús):** "las estadísticas de cobro que ahora deben llamarse Dashboard en todas sus referencias y
links ... aquí te pido 2 cosas: renombrar todas las referencias al nuevo nombre de dashboard y retomar algo que te
había pedido" (lo segundo es el issue 371, bloques independientes).

**Status:** desplegado en test (`c77c719`), pendiente confirmar en vivo

## Decisiones

- URL nueva `/administracion/dashboard`; la vieja `/administracion/estadisticas-cobro` redirige (301, conserva
  `?...`) para no romper marcadores ni enlaces guardados.
- Menú, título y encabezados ya dicen "Dashboard" (issue 406); se renombran también rutas, plantillas y el archivo de
  pruebas (`dashboard.html`, `_dashboard_resultados.html`, `_dashboard_tarjetas.html`, `test_admin_dashboard.py`).
- NO se tocan los comentarios que apuntan a carpetas de historial (`.scratch/estadisticas-cobro-dashboard`, etc.):
  son nombres de carpetas reales, cambiarlos rompería el rastro. El servicio de dominio
  (`estadisticas_tablero_service`) tampoco: calcula estadísticas, no es la pantalla.

## Verificación

- `test_admin_dashboard.py` (antes `test_admin_estadisticas_cobro.py`): nueva prueba de la redirección 301 con y sin
  parámetros; el resto apunta a la URL nueva. `test_datos_importados_sin_apartamento.py` también. 220 + 24 en verde
  (dashboard, menú, proveedores, servicio del tablero, datos importados).

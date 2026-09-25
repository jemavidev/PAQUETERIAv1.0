# 406 — Menú de cuenta: sin sección Cobros; "Dashboard" arriba de Lector; Tarifas en Datos

**Pedido original (Jesús):** "quiero que elimines la sección de cobros, para esto vas a sacar estadísticas de cobro
que está dentro de cobros y las vas a colocar arriba de lector, esta la vas a llamar 'Dashboard' y la que se llama
tarifas de cobro la vas a agregar a la sección de datos". Luego: "cámbialo a 'Dashboard'" (también el título de la
pantalla) y "sí, puede ir al final" (Tarifas al final de Datos).

**Status:** implementado (localhost), pendiente confirmar en vivo

## Decisiones (acordadas)

- Se quita la categoría "Cobros" del menú de cuenta.
- "Estadísticas de cobro" pasa a "Dashboard", enlace suelto arriba de "Lector" (solo admin: la ruta es
  `require_admin`); el operador no cambia. Misma URL `/administracion/estadisticas-cobro`.
- El título de la pantalla (`<title>` y `<h1>`) pasa a "Dashboard".
- "Tarifas de cobro" al final de Datos (después de Notificaciones).

## Verificación

- `test_layout.py`: 2 nuevas (admin: sin Cobros, Dashboard suelto antes de Lector, Tarifas último de Datos; operador: sin Dashboard), vista fallar la del admin antes del cambio. `test_admin_estadisticas_cobro.py`: el título pasa a "Dashboard" (ajuste a propósito). Con `test_auth.py`: 98 en verde.

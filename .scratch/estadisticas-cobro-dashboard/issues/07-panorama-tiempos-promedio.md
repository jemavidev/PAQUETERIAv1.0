# 07 — Panorama: Tiempos promedio

**What to build:** la tarjeta fija "Tiempos promedio" de Panorama — una sola tarjeta con tres filas
(Anuncio → recepción, Permanencia en bodega, Bodegaje cobrado) × tres columnas (Hoy, Semana, Mes).

**Blocked by:** 01

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] "Anuncio → recepción" = promedio de (recibido − anunciado) de los paquetes recibidos en cada
      ventana (Hoy/Semana/Mes), en horas.
- [ ] "Permanencia en bodega" = promedio de (entregado − recibido) de los paquetes entregados en cada
      ventana, en horas.
- [ ] "Bodegaje cobrado" = promedio de horas de permanencia SOLO de los cobros con bloques de bodegaje
      > 0 en cada ventana (misma métrica que ya existe hoy en la pantalla actual, reubicada aquí).
- [ ] Sin ningún paquete que califique en una ventana (ej. "Hoy" sin ninguna recepción), esa celda
      muestra "—", no un error ni "0 h".
- [ ] Las tres filas se calculan en hora de Colombia y no cambian con los filtros de la barra.

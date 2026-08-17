# 106 — Modal "Ver": teléfono+dirección en una línea, chip de días transcurridos, sin "Actual"

**Pedido original (cliente), 3 puntos en un mismo turno:**
"Muy bien, ahora necesito varios cambios puntuales en la vista /paquetes,
específicamente el modal de clientes:
1. Al abrir el modal necesito que el la parte superior el numero de
telefono este justo al lado de lo que es la torre y el apartamento
(recuerda que esto debe estar distinguiblemente separado).
2. Al lado del estado actual del paquete deberia aparecer la cantidad de
dias que duro el paquete desde el dia que se recibio hasta que se
entrego o se cancelo, en su defecto si no se ha entregado deberia ir
contando cada dia desde que se recibio.
3. Por ejemplo en el estado actual de un paquete, digamos "Entregado •
Actual" debe aparecer solo el estado "Entregado", ya que al visualizar
el historial esto se sobreentiende."

**Status:** implementado

## Implementación

- **Punto 1** (`_resultados.html`, modal "Ver"): el párrafo de teléfono
  debajo del título ahora también incluye Torre/Apto, separados por un
  "|" (`aria-hidden`) -- antes el teléfono vivía en esa línea y
  Torre/Apto en la fila de badges de abajo. Se quitó la repetición de
  `p.direccion_corta` de esa fila de badges para no duplicarlo.
- **Punto 2** (`packages.py`): nueva función `_dias_transcurridos(paquete)`
  -- diferencia en DÍAS CALENDARIO (vía `hora_local`, no horas crudas de
  24h) entre `received_at` y (`delivered_at` o `cancelled_at` o "ahora" si
  sigue abierto). `None` si nunca se recibió (ANUNCIADO sin recibir), la
  plantilla omite el chip en ese caso. Wireado en `_listar` como
  `p.dias_transcurridos`, renderizado como chip gris justo después del
  badge de Estado.
- **Punto 3** (`_resultados.html`, `paso_timeline`): se quitó el sufijo
  `' • Actual'` que se le agregaba al título del último paso del
  historial -- ya se sobreentiende por ser el último ítem de la línea de
  tiempo.

## Verificación

- `tests/web/test_packages.py`: 9 tests nuevos -- `_dias_transcurridos`
  probada directamente (None sin recibir, fija entre recibido/entregado,
  fija entre recibido/cancelado, prioridad delivered sobre cancelled,
  conteo en curso sin cerrar) + a nivel HTTP (chip ausente en ANUNCIADO,
  chip presente y ubicado después del badge en RECIBIDO, teléfono +
  separador + dirección en una sola línea y sin duplicado, "Actual"
  ausente del historial tras Entregar). `tests/web/test_packages.py`
  completo: 133 passed (124 + 9).
- Playwright contra el servidor local real, 3 paquetes de prueba con
  `received_at`/`delivered_at` manipulados directamente en BD: RECIBIDO
  con recepción hace 3 días 2 horas → "3 días" (conteo en curso);
  ENTREGADO con 5 días entre recepción y entrega → "3 días" (fijo,
  matemática de calendario correcta); ANUNCIADO nunca recibido → sin chip.
  Capturas de pantalla confirman visualmente el teléfono y Torre/Apto en
  la misma línea con el separador, y el chip de días junto al badge de
  Estado.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

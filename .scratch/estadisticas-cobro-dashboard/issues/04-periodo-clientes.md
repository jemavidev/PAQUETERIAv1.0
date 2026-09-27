# 04 — Periodo seleccionado: Clientes

**What to build:** la categoría "Clientes" de la zona Periodo seleccionado — activos, nuevos,
recurrentes, y las dos tarjetas de "el cliente #1" (más paquetes, mayor gasto), mostrando siempre el
NOMBRE del cliente, nunca su teléfono.

**Blocked by:** 02

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] "Clientes activos" = Personas distintas (por el teléfono del destinatario del paquete) con al
      menos un paquete con movimiento en el periodo.
- [ ] "Clientes nuevos" = Personas cuya PRIMERA entrega histórica (no solo dentro del periodo — histórica
      completa) cae dentro del periodo seleccionado.
- [ ] "Clientes recurrentes" = de los activos, los que tienen 2 o más paquetes con movimiento en el
      periodo.
- [ ] "Cliente con más paquetes" y "Cliente con mayor gasto" muestran el NOMBRE de la Persona (o el
      nombre congelado en el paquete si no hay Persona propia), su Apartamento del snapshot más reciente
      del periodo, y la cifra correspondiente (cantidad de paquetes / monto gastado).
- [ ] Los paquetes de "nombre sin teléfono" (sin Persona detrás) NO cuentan en ninguna de las 5 tarjetas
      de esta categoría.
- [ ] Las Personas eliminadas (anonimizadas) o dadas de baja administrativa no cuentan como clientes
      activos/nuevos/recurrentes aunque tengan paquetes históricos.
- [ ] Un empate en "más paquetes" o "mayor gasto" se resuelve siempre igual: primero por la cifra, luego
      por el nombre — dos cargas seguidas con los mismos datos dan el mismo resultado.
- [ ] Matriz de "no aplica": Tipo acota las 5 tarjetas; Cobrado/Anulado solo acota "Cliente con mayor
      gasto" (depende de cobros) — las otras 4 se atenúan con "no depende de Cobrado/Anulado".
- [ ] Prueba de dominio que arma un cliente con paquetes en dos apartamentos distintos (se mudó) y
      confirma que se le atribuye el apartamento del snapshot más reciente dentro del periodo, no el
      actual.

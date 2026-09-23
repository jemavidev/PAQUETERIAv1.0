# 16 — Panorama: SMS en la tendencia (▲▼ neutro + minigráfico)

**What to build:** la tarjeta "SMS enviados por AWS" de Panorama gana el mismo indicador de tendencia que
ya tienen Ingresos/Entregados/Cancelados (ticket 08), adaptado a que SMS es una métrica neutra.

**Blocked by:** 08, 14

**Status:** ready-for-agent

- [ ] Cada columna (Hoy/Semana/Mes) de "SMS enviados por AWS" muestra su variación ▲▼ contra el mismo
      tramo del periodo anterior, con el mismo cálculo exacto que ya usan Ingresos/Entregados/Cancelados.
- [ ] La flecha se muestra en un color NEUTRO (ni verde ni rojo) sin importar si sube o baja — a
      diferencia de Ingresos/Entregados/Cancelados, más o menos SMS no es "bueno" ni "malo" por sí solo.
- [ ] La tarjeta muestra un minigráfico de los últimos 7 días, igual que las otras tres de Panorama.
- [ ] Si todavía no hay 7 días de registro de SMS, el minigráfico muestra solo los días disponibles, sin
      inventar ceros para los días anteriores a la activación del registro.

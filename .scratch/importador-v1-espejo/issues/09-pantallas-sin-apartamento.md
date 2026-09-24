# 09 — Pantallas sin apartamento

**What to build:** todas las pantallas de la v2 funcionan con Personas sin apartamento actual y paquetes con snapshot sin apartamento, que es como llegan todos los datos importados (ver `../spec.md`, historia 46).

**Blocked by:** None — can start immediately

**Status:** done

- [x] Pruebas en `tests/web` que siembran Personas sin apartamento y paquetes con snapshot vacío en todos los estados (`ANUNCIADO`, `RECIBIDO`, `ENTREGADO`, `CANCELADO`).
- [x] Recorren listados y búsqueda de paquetes, detalle y línea de tiempo, recibir, entregar, cancelar, `/consultar`, `/mis-datos`, gestión de clientes, estadísticas de cobro y exportaciones. Todas responden sin error y muestran "Sin apartamento" donde corresponde.
- [x] Se corrige cualquier pantalla que falle (ninguna falló: 24/24 en verde sin cambios de código).
- [ ] Revisión visual de las pantallas afectadas en viewport móvil.

# 09 — Ahora: Pendientes y bodega

**What to build:** la zona Ahora (foto del momento, ignora todos los filtros) se llena con sus tarjetas
de estado y bodega: pendientes, en bodega, en gracia, con bodegaje corriendo, más de 7 días, abandonados,
el paquete más antiguo, los anuncios que nunca llegaron y los clientes registrados — cada una con su
punto de semáforo.

**Blocked by:** 01

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] "Paquetes pendientes" = Anunciados + Recibidos actuales, con el desglose "X anunciados · Y
      recibidos".
- [ ] "En bodega" = Recibidos actuales (aún sin entregar).
- [ ] "En gracia (≤ 48 h)" = recibidos hace 48 horas o menos; "Con bodegaje corriendo" = recibidos hace
      más de 48 horas — ambas sobre los mismos Recibidos actuales, sin solaparse.
- [ ] "Más de 7 días" y "Abandonados" (más de 30 días) = por antigüedad de la recepción, sobre los
      Recibidos actuales.
- [ ] "Paquete más antiguo" = el Recibido con la recepción más antigua: sus días en bodega, su
      Apartamento (del snapshot) y su código de acceso.
- [ ] "Anuncios que nunca llegaron" = paquetes ANUNCIADO hace más de 7 días, aún sin recibirse.
- [ ] "Clientes registrados" = Personas sin eliminar (no anonimizadas) y sin baja administrativa, en este
      momento.
- [ ] Cada tarjeta lleva un punto de semáforo: gris/neutro por defecto, verde para lo sano (en gracia),
      ámbar para lo que requiere atención (con bodegaje, más de 7 días, anuncios sin llegar), rojo para lo
      crítico (abandonados, el más antiguo).
- [ ] Ninguna tarjeta de esta zona cambia al tocar los filtros de la barra.
- [ ] Con la base vacía, todas muestran 0 (o "—" en "paquete más antiguo") sin error.

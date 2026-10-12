# 07 — Búsqueda, filtro Anunciado/Recibido, conteos y paginación

**What to build:** El Admin puede encontrar rápido a un cliente en una lista larga: búsqueda en vivo por nombre, teléfono, código o
Torre/Apartamento, filtro por Estado (Anunciado/Recibido) con conteos, y paginación. Todo conserva el mensaje elegido
en el selector.

Ver spec: User Stories 21-24, 28.

**Blocked by:** 04 — Selector de mensaje y botón de WhatsApp

**Status:** ready-for-agent

- [ ] Búsqueda en vivo (mismo patrón de fragmento HTML que `/paquetes`) por nombre, teléfono, código o Torre/Apartamento, sin distinguir mayúsculas
- [ ] Filtro Anunciado/Recibido; un cliente con paquetes de los dos estados aparece en ambos
- [ ] Conteo de clientes total y por filtro
- [ ] Paginación con el componente de la app
- [ ] El mensaje elegido (`?mensaje=`) se conserva al buscar, filtrar y paginar, también en la búsqueda en vivo
- [ ] Pruebas por HTTP

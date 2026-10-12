# 07 — Búsqueda, filtro Anunciado/Recibido, conteos y paginación

**What to build:** El Admin puede encontrar rápido a un cliente en una lista larga: búsqueda en vivo por nombre, teléfono, código o
Torre/Apartamento, filtro por Estado (Anunciado/Recibido) con conteos, y paginación. Todo conserva el mensaje elegido
en el selector.

Ver spec: User Stories 21-24, 28.

**Blocked by:** 04 — Selector de mensaje y botón de WhatsApp

**Status:** done (2026-10-11)

- [x] Búsqueda en vivo (mismo patrón de fragmento HTML que `/paquetes`) por nombre, teléfono, código o Torre/Apartamento, sin distinguir mayúsculas
- [x] Filtro Anunciado/Recibido; un cliente con paquetes de los dos estados aparece en ambos
- [x] Conteo de clientes total y por filtro
- [x] Paginación con el componente de la app
- [x] El mensaje elegido (`?mensaje=`) se conserva al buscar, filtrar y paginar, también en la búsqueda en vivo
- [x] Pruebas por HTTP

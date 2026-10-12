# 03 — Vista "Avisos especiales": la lista de clientes

**What to build:** El Admin entra desde el menú de cuenta a una vista nueva que lista a los clientes con algo pendiente en Papyrus, una
fila por cliente. Entran los paquetes ANUNCIADOS de hoy y los 4 días calendario anteriores (hora de Colombia) y todos
los RECIBIDOS; nunca Entregados ni Cancelados. El "cliente" de cada paquete es la misma Persona que recibiría hoy sus
avisos automáticos (Destinatario alcanzable, o si no, el Anunciante). Cada fila muestra nombre, Torre/Apartamento y
los códigos de sus paquetes con el color del Estado, enlazados a `/consultar`. El look es el de `/paquetes`
(filas-tarjeta en escritorio, issue 445; tarjetas en celular). Este ticket todavía no trae botones de envío.

Ver spec: Implementation Decisions (módulo de dominio, elegibilidad, quién es el cliente, Vista) y User Stories 1-15,
20.

**Blocked by:** None — can start immediately

**Status:** done (2026-10-11)

- [x] Ruta nueva bajo `/administracion/` protegida con `require_admin`: Staff no Admin rechazado, sin sesión redirige a ingresar
- [x] Enlace "Avisos especiales" en el menú de cuenta, solo para Admin, junto a "Dashboard"
- [x] Un ANUNCIADO de hace 4 días calendario entra y uno de hace 5 no, contando en hora de Colombia (incluido un anuncio de las 11 p. m.); un RECIBIDO viejo entra; ENTREGADO y CANCELADO nunca
- [x] Un cliente con varios paquetes pendientes aparece en una sola fila con todos sus códigos
- [x] El cliente de cada paquete sale de la misma resolución que los avisos automáticos; si no se resuelve a nadie, el paquete no aparece
- [x] Cada código lleva el color de su Estado y enlaza a `/consultar?q=<código>`
- [x] Estado vacío claro cuando no hay ningún cliente pendiente
- [x] Si hacen falta clases Tailwind nuevas: recompilar las dos salidas de `tailwind.css` y subir el `?v=`
- [x] Pruebas por HTTP y, para el corte de días, sobre el servicio de dominio con "hoy" inyectado

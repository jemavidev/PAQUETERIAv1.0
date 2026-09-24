# 07 — Borrado reflejado con tope del 5 %

**What to build:** lo que desaparece de la v1 (anuncios vencidos que borra su limpieza de 15 días, clientes o paquetes borrados por un admin) desaparece también de la v2, sin riesgo de que una lectura vacía de la v1 vacíe la v2 (ver `../spec.md`, historias 12-15).

**Blocked by:** 04 — Cobros históricos, 06 — Fotos espejo

**Status:** done

- [x] Por entidad, se borran los registros con `origen_v1_id` que ya no están en la instantánea, en cascada: paquete → fotos (solo la fila; el objeto S3 se deja) → cobro.
- [x] Nunca se borran registros sin `origen_v1_id`.
- [x] Una Persona desaparecida que tiene paquetes nativos no se borra: se le quita `origen_v1_id`.
- [x] Si lo desaparecido de cualquier entidad supera el 5 % de lo importado de esa entidad, la pasada completa aborta **antes de escribir nada** y lo reporta como alerta.
- [x] Toda la escritura en la base de una pasada va en una sola transacción.
- [x] El reporte cuenta los borrados por entidad.

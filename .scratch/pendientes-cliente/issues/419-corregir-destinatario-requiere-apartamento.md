# 419 — "Corregir destinatario" solo con apartamento asignado

**Pedido original (Jesús, 2026-09-27):** "para el modal de "Corregir destinatario" no se incluya la seccion de "Sin apartamento
asignado -- asignar apartamento primero" [...] la idea de esto es que se use el modal "Asignar apartamento" para asignar
apartamentos y "Corregir destinatario" para asignar al destinatario correcto para un paquete". Aclaración: "en caso que no se
tenga un apartamento asignado, no sera posible ver el modal de "Corregir destinatario" [...] seria bueno que el tratar de activar
este modal este desactivado en caso que no exista un apartamento asociado".

**Status:** verificado (desplegado en test `96bb562`, confirmado por Jesús 2026-09-27)

## Alcance

- Sin apartamento en el paquete (`snapshot_apartamento` vacío): el lápiz "Modificar" de la fila (Acciones) y el de "Ver" salen
  apagados (grises, sin abrir nada) con el aviso "Asigna un apartamento primero"; `/paquetes?corregir=<id>` no abre nada.
- La ruta de corregir rechaza sin cambios un paquete sin apartamento ("Asigna un apartamento primero.").
- Se quitan del modal el botón "Sin apartamento asignado -- asignar apartamento primero" y la nota alternativa.
- Asignar apartamento (🏠) y el modal Recibir sin cambios.

# 202 — Acordeón exclusivo (1 abierto a la vez) + quitar "Anunciado · Staff"

**Pedido original (cliente):**
"seria bueno que solo 1 este abierta a la vez [...] Por otro lado creo que
Anunciado Staff no debe existor ya que los anuncios incluyendo estos se
van directo a los clientes, con el 'Anunciado Cliente' es mas que
suficiente"

**Status:** implementado

## Parte 1 — Acordeón exclusivo

- `admin/notificaciones.html`: los 8 (ahora 7) `<details>` comparten
  `name="notif-acordeon"` -- soporte NATIVO del navegador (sin JS): abrir
  uno cierra automáticamente cualquier otro del mismo grupo.
- La lógica de "cuál abre por defecto" se ajustó para nunca marcar `open`
  en dos `<details>` del mismo grupo a la vez (antes podía pasar que la
  primera fila Y la fila con error/guardado quedaran ambas `open` en el
  HTML servido -- con `name` compartido el navegador ya lo resuelve solo,
  pero es más limpio no depender de esa resolución para el render inicial).
- 2 tests nuevos: la fila con error NO deja la primera también abierta; las
  8→7 `<details>` comparten el mismo `name`.

## Parte 2 — Quitar "Anunciado · Staff"

`ANUNCIADO` deja de distinguir quién anunció (Cliente vía `/anunciar` vs.
Staff vía `/announce`, Grupo 19 Ronda 2) -- pasa a comportarse igual que
RECIBIDO/ENTREGADO: una sola plantilla, sin `motivo`.

- `notificacion_service.py`: `origen_anuncio()`, `ORIGEN_ANUNCIO_CLIENTE`/
  `ORIGEN_ANUNCIO_STAFF`, y las tablas `_ANUNCIADO_DEFAULT`/
  `_ANUNCIADO_ASUNTO_DEFAULT` se eliminan por completo -- `ANUNCIADO` entra
  directo a `PLANTILLAS_DEFAULT`/`ASUNTOS_DEFAULT` (mismo texto que ya
  tenía la variante "Cliente", que el cliente pidió mantener).
  `_default_de` se simplifica (ya no necesita la rama especial de
  ANUNCIADO). `construir_mensaje` ya no llama `origen_anuncio` -- el
  `motivo` buscado es `None` para todo evento que no sea CANCELADO.
- `admin.py`: `_EVENTOS_SIN_MOTIVO` ahora incluye `ANUNCIADO`;
  `_filas_plantillas` deja de generar 2 filas especiales para ANUNCIADO
  (usa el mismo camino genérico que RECIBIDO/ENTREGADO). Sin cambios de
  esquema/migración -- `motivo` para ANUNCIADO simplemente pasa a ser
  siempre `NULL`, ya cubierto por el índice único parcial existente.
- Sin migración de datos: nunca se desplegó a un ambiente real
  (test.papyrus.com.co), así que no hay filas `ANUNCIADO·STAFF`/
  `ANUNCIADO·CLIENTE` reales que migrar -- cualquier fila de prueba local
  queda huérfana e inerte, mismo criterio que otras columnas/datos
  congelados del dominio.
- Tests actualizados: se quitaron los 5 tests que verificaban las 2
  variantes por separado, reemplazados por 2 que confirman una sola fila
  y el mismo texto sin importar quién anunció.

## Verificación

- Suite completa: ver commit para el conteo final.
- Verificado en vivo contra el servidor de dev local: solo 1 acordeón
  abierto a la vez; `/administracion/notificaciones` muestra "ANUNCIADO"
  como una sola fila, sin "Cliente"/"Staff".
- Pendiente: deploy a test.papyrus.com.co.

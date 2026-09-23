# 361 — `/administracion/estadisticas-cobro`: quitar los atajos "Últimos 7 días" y "Últimos 30 días"

**Pedido original (Jesús):** "necesito que quites las píldoras o filtros
relacionados a 'Últimos 7 días y Últimos 30 días', ya que estos están
incluidos en semana y mes".

**Status:** implementado, pendiente confirmar visualmente

Test: `test_atajos_de_fecha_son_solo_hoy_ayer_semana_y_mes` en
`tests/web/test_admin_estadisticas_cobro.py`.

## Contexto

`CODE/src/app/web/templates/admin/estadisticas_cobro.html` -- la barra de
filtros traía 6 atajos de fecha: Hoy · Ayer · Esta semana · Este mes ·
Últimos 7 días · Últimos 30 días. Los dos últimos se solapan con "Esta
semana" y "Este mes" a criterio del cliente, así que quedan 4.

## Decisiones

- Se quitan los 2 botones **y** sus entradas `dias7`/`dias30` del mapa
  `ATAJOS` del script (código muerto si no).
- (Superado por [[364]]: la primera carga pasó a mostrar todos los datos.)
  El rango por defecto de la primera carga (sin `desde`/`hasta`) **no
  cambia**: sigue siendo los últimos 30 días en UTC
  (`admin.py::_DIAS_RANGO_INICIAL_ESTADISTICAS_COBRO`). Los atajos solo
  escriben Desde/Hasta y no son un estado que se resalte, así que no queda
  ningún control "huérfano" por quitar el de 30 días.

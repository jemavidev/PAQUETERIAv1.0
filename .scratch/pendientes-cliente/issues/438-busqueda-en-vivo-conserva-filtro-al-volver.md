# 438 — Al volver a `/paquetes` (desde `/consultar`, etc.) el filtro escrito se pierde

**Pedido original (Jesús, 2026-10-07):** "al tener un filtro activo en la vista de Paquetes, digamos que se buscó por
nombre y entramos en la vista de /consultas, analizamos cualquier cosa y al regresar a la vista anterior el nombre que se
quiere filtrar está ahí en posición, pero el filtro se perdió, es necesario presionar enter o actualizar el valor del
nombre que se escribió (quitando o agregando un carácter para que se filtre nuevamente)".

**Status:** implementado (local, sin desplegar)

## Causa

La búsqueda en vivo (`busqueda_filtros()` en `components/_busqueda_filtros.html`) trae los resultados por `fetch` sin
tocar la URL: sigue en `/paquetes` a secas. Al volver con "atrás", el servidor dibuja esa URL (vista por defecto) y el
navegador solo rellena el campo con el texto que tenía (restauración de formularios), así que texto y lista no calzan.

## Decisiones

- Cada búsqueda en vivo actualiza la URL con `history.replaceState` (`?q=...&estado=...&conectados=...&vista=...`):
  sin entradas nuevas en el historial ("atrás" sigue yendo a donde iba), y al volver o recargar el servidor dibuja la
  lista ya filtrada. Aplica a las tres vistas que usan la barra: `/paquetes`, `/residentes`,
  `/administracion/contactos-externos`.

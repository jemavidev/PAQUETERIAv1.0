# 172 — `/residentes`: unificar barra de búsqueda con la de `/paquetes`

**Pedido original:** "quiero que unifiques la barra de busqueda, que quede similar (en lo que
aplique) a la barra de la vista /paquetes, corrije esto"

**Status:** implementado

## Cambio

- `customers_manage/search.html`: reemplazar el form propio (tarjeta centrada `max-w-lg` con
  `input_texto` + botón "Buscar" debajo) por el macro compartido `busqueda_filtros` de
  `components/_busqueda_filtros.html` — el mismo componente que ya usa `packages/list.html` en
  `/paquetes`.
- `mostrar_estado=False` (Residentes no tiene un Estado de paquete que filtrar, no aplica).
  `mostrar_agregar` y `conteos` tampoco aplican (sin equivalente en Residentes).
- `titulo='Residentes'`, mismo patrón mobile/desktop que `/paquetes`: `<h1>` propio solo en
  mobile (`md:hidden`), en desktop lo pinta el macro inline junto a la barra.
- `placeholder_q` propio de Residentes (nombre, teléfono, torre o apartamento) en vez del
  default del macro (pensado para paquetes: código, guía, email...).
- Sin `resultados_id` — NO se activa la búsqueda en vivo (fetch/debounce) que sí tiene
  `/paquetes`; el pedido fue igualar el LOOK, no agregar esa función nueva. El form sigue
  siendo un GET normal a `/residentes`, con la paginación de servidor que ya tenía.

## Verificación

- Suite completa: 286/286 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`) vía HTML renderizado: la barra de `/residentes` usa
  ahora el mismo `<div class="bg-white rounded-xl border ...">` + `<form id="busqueda-filtros-form">`
  que `/paquetes`, mismo placeholder de campo, mismo botón `sr-only`, título inline en desktop.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

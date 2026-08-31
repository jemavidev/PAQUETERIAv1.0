# 267 — Fichas con tabs (staff /residentes, cliente /mis-datos): refrescar mantiene la tab activa

**Pedido original (cliente):** "Necesito que al refrescar la página web,
ya sea por F5 o el botón de refrescar del navegador, se realice esta
acción, pero si se está en cualquier tab de cualquier vista
(staff/residentes), se realice el refresco y se mantenga o se regrese
al tab desde donde se realizó el refresh."

**Status:** implementado

## Diagnóstico

El cambio de tab es 100% client-side (JS, `activar(nombre)` solo
oculta/muestra `.tab-panel`, sin tocar la URL) en las 2 fichas con
tabs: `customers_manage/detail.html` (staff, `/residentes/{id}`) y
`customer/verify.html` (cliente, `/mis-datos`). Al refrescar, el
navegador re-pide la MISMA URL que tenía antes -- si esa URL nunca
incluyó `?tab=`, el server no tiene forma de saber cuál tab estaba
activa y cae al default ("Datos").

`/residentes` YA soporta `?tab=` del lado servidor (`customers_manage.py`,
conversación 2026-08-17) -- pensado para links externos, nunca se
conectó con los clicks de tab de la propia ficha. `/mis-datos` no
soporta `?tab=` en absoluto todavía.

## Alcance

1. `customers_manage/detail.html`: al hacer click en un tab, además de
   `activar(nombre)`, sincroniza `?tab=<nombre>` en la URL vía
   `history.replaceState` (no `pushState` -- no ensucia el historial
   con un entry por cada click). El server ya lo lee.
2. `customer/verify.html` + `customer_verify_form` (`/mis-datos`): el
   template ya calcula `tab_inicial` completo en Jinja (no en la ruta)
   -- se le agrega `request.query_params.get('tab')` como tercera
   prioridad (después de `error_telefono/email` y `ocupante_guardado`,
   que siguen ganando -- mismo orden que ya usa `/residentes`). Mismo
   `history.replaceState` en el click del tab.
3. `/mis-paquetes` (`customer/paquetes.html`) queda FUERA de este
   alcance -- su tab activo hoy es puramente client-side sin ningún
   mecanismo `tab_inicial`/`?tab=` de por medio (siempre arranca en
   "ANUNCIADO"), es una vista distinta a las dos fichas -- el cliente
   mencionó puntualmente "staff/residentes".

## Verificación

- Tests nuevos: `test_mis_datos_query_param_tab_abre_directo_en_esa_tab`,
  `test_mis_datos_tab_desconocida_cae_al_default`,
  `test_mis_datos_ocupante_guardado_gana_sobre_query_param_tab`
  (`test_customer_verify.py`). Suite (`test_customers_manage.py` +
  `test_customer_verify.py`): 217 passed.
- Verificado en vivo en las 2 vistas: `/residentes/{id}?tab=residentes`
  y `/mis-datos?tab=notif` abren directo en esa tab, y el snippet
  `history.replaceState` está presente en el HTML servido de ambas.

# 276 — `/residentes` lista: quitar el ícono "Ver ficha" de Acciones

**Pedido original (cliente):** "remueve el ícono que se llama 'Ver
ficha', no creo que sea muy útil."

**Status:** implementado

## Alcance

`customers_manage/_resultados.html` -- el ícono "Ver ficha" (columna
Acciones) es redundante: el NOMBRE del residente, en la misma fila, ya
enlaza a la misma URL (`/residentes/{{ p.id }}`). Se quita el ícono,
el nombre se queda como única vía a la ficha desde esta lista. El
mismo patrón redundante existía 3 veces en este archivo (tabla
principal + vista agrupada por apartamento + "sin apartamento
asignado") -- se quitaron las 3 para consistencia.

## Verificación

Un test dependía del conteo de links a la ficha para verificar
"no duplicado" (`test_resultados_no_se_duplican_si_varios_criterios_
coinciden`, esperaba 3 por fila -- Nombre + 👫 + Ver ficha) -- ajustado
a 2 (Nombre + 👫). Otro test que verificaba "Ver ficha es ícono, no
texto" quedó obsoleto (la premisa ya no existe) -- reemplazado por uno
que confirma la ausencia total. Suite completa: 151 passed. Verificado
en vivo: 0 ocurrencias de "Ver ficha" en `/residentes`.

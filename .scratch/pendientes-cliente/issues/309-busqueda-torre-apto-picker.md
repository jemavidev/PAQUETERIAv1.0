# 309 — Buscar por Torre/Apto reusando el picker (número → torres posibles)

**Pedido original (cliente):** hoy buscar "Torre 5 302" (combinado) no encuentra nada -- cada campo
se compara por separado contra todo el texto. Pide reusar el picker ya existente
(`components/_picker_apartamento.html`, el mismo de "Recibir"/"Asignar apartamento"): escribís el
número de apartamento, se listan las Torres que YA tienen residentes en ese número, elegís una, y
la búsqueda pasa a filtrar ESTRICTAMENTE por esa Torre+Apto -- descartando cualquier otro campo
(teléfono/email/whatsapp que contengan esos mismos dígitos por coincidencia, etc.).

**Status:** removido -- después de 2 rondas de retroalimentación en vivo (issues 311, 312)
tratando de acomodar la UI, el cliente pidió explícitamente deshacer todo el trabajo: "esto de
buscar por torre y apartamento te quedo grande, hagamos algo mejor, remueve todo lo relacionado
a la busqueda por torre y apartamento en la vista de /paquetes". Revertido por completo --
`packages.py` (`_listar`/`_render_lista`/`packages_list` sin `torre`/`apartamento`),
`_busqueda_filtros.html` (sin el ícono ni el dropdown, `q` vuelve a su forma simple),
`_picker_apartamento.html`/`_recibir_paquete.html` (sin `mostrar_input`/eventos custom, vuelven
a su estado pre-309), `icons.py` (sin el ícono `torres`). El toggle "conectados" (issue 308) y
su gate de activación (issue 310) NO se tocaron -- el pedido de remover fue específico a
Torre/Apto. 386 tests en verde tras la reversión (`test_packages.py`/`test_layout.py`/
`test_customers_manage.py`), incluye 4 tests removidos y 1 revertido a su forma original
(`test_parametros_torre_apartamento_obsoletos_se_ignoran_sin_error` -- vuelve a verificar que
esos parámetros no tienen efecto, como antes de este issue). Ver issues 311/312 para el detalle
de las 2 rondas de UI que no funcionaron.

## Confirmado con el cliente

Al resolverse una Torre/Apto vía el picker, el campo de búsqueda libre (`q`) se deshabilita y se
limpia visualmente -- no pueden convivir los dos criterios ni por accidente ni en apariencia.

## Piezas reusables (ya existen, sin construir nada nuevo del lado de datos)

`packages.py::_render_lista` ya pasa `catalogo_torres` (`listar_catalogo_por_torre`) y
`residentes_por_unidad` (`residentes_por_torre_apartamento`) al contexto de `/paquetes` -- son
exactamente los datos que necesita `picker_apartamento()`, hoy usados solo dentro de los modales
"Recibir"/"Asignar apartamento".

# 169 — `/residentes` tab Datos: staff puede editar "Autoriza recepción automática"

**Pedido original:** "no tengo forma en este momento yo (staff) de modificar la Píldora verde
'Auto - recepción automática de paquetes', puedes hacer esto posible."

**Status:** verificado

## Diagnóstico

`autoriza_recepcion_automatica` solo se podía tocar desde `/mis-datos` (autoservicio del cliente,
`set_autoriza_recepcion_automatica` llamado únicamente desde `customer_verify.py`). La ficha de
staff (`/residentes/<id>`) lo mostraba como badge de solo lectura en el header -- sin ningún
control para cambiarlo desde ahí.

## Cambio

- `customers_manage.py` (`customers_manage_update`, tab "Datos"): nuevo parámetro
  `autoriza_recepcion_automatica: str = Form(None)`, llama `set_autoriza_recepcion_automatica`
  junto con el resto de los campos de esa tab (un solo POST). Mismo contrato de checkbox HTML que
  `/mis-datos`: ausente en el form = no autoriza (no "no tocar") -- coherente porque el checkbox
  viaja SIEMPRE dentro del mismo `<form>` que el resto de "Datos", su estado real siempre se
  manda.
- `detail.html`: mismo checkbox/texto que `/mis-datos`, agregado al final del form de tab "Datos".

## Verificación

- 3 tests nuevos (`test_staff_activa_recepcion_automatica`, `test_staff_desactiva_recepcion_
  automatica_al_omitir_el_checkbox`, `test_ficha_muestra_el_checkbox_de_recepcion_automatica_
  marcado`).
- Suite completa: 1070/1070 (ver spec.md, pendiente la corrida final con este issue incluido).
- Verificado en vivo contra `localhost:8010`: activado desde la ficha de staff, confirmado que la
  píldora "Auto" aparece en la lista; desactivado (omitiendo el checkbox), confirmado que
  desaparece. Datos de prueba revertidos a su estado original.

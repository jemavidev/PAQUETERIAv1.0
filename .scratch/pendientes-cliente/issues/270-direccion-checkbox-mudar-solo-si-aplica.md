# 270 — `/residentes` tab Dirección: checkbox "Mudar residente de apartamento" solo si aplica

**Pedido original (cliente):** "Como puedes hacer para que esto
aparezca solamente cuando sea necesario 'Mudar residente de
apartamento', que me sugieres" -- confirmó la sugerencia: mostrarlo
solo si `mi_ocupante` existe (la Persona de la ficha ya es Ocupante
activo de alguna unidad).

**Status:** implementado

## Verificación

Tests nuevos: `test_tab_direccion_checkbox_mudar_oculto_si_no_es_ocupante`,
`test_tab_direccion_checkbox_mudar_visible_si_es_ocupante`
(`test_customers_manage.py`). Suite: 151 passed. Verificado en vivo en
ambos casos (LAIS, principal activa: aparece; una persona sin Ocupante
activo: no aparece).

## Alcance

`customers_manage/detail.html` -- el checkbox `mover_de_otra_unidad`
hoy se renderiza siempre, aunque la ruta (`customers_manage_asignar_
apartamento`) solo lo usa cuando `ocupante_activo_de_persona(db,
persona.id)` (= `conflicto` ahí, = `mi_ocupante` en el contexto de la
ficha) no es `None` -- si la Persona no es Ocupante activo de ninguna
unidad, marcar la casilla no tiene ningún efecto. Se envuelve el
`<label>` en `{% if mi_ocupante %}` -- mismo dato que ya calcula
`_contexto_detalle` para el resto de la ficha, sin ningún cambio de
ruta.

# 257 — `/residentes/{id}`: modal "Convertir en residente principal" en azul

**Pedido original (cliente):** "Para el modal 'Convertir en residente
principal / ¿Convertir a ANGELICA ARRAZOLA en el nuevo residente
principal? Se degrada automáticamente a quien es principal ahora.',
permite que los colores predominantes sean los tonos azules así como
debería ser."

**Status:** implementado

## Alcance

`components/_modales.html::modal_confirmacion` -- nueva variante
`'info'` (azul, `bg-blue-100 text-blue-800` / `bg-blue-800 hover:bg-blue-
700`, mismo azul primario que `boton()` y que el ícono ⭐ de esta misma
acción) además de las ya existentes `'danger'` (rojo) y `'warning'`
(naranja). Solo se cambió el llamador de `/residentes` (`variant='info'`
en vez de `'warning'`) -- el modal equivalente de `/mis-datos` no se
tocó, el pedido fue puntual sobre esta vista.

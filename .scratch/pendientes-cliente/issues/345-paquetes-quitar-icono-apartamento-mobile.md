# 345 — `/paquetes` mobile: quitar por completo el ícono de Apartamento de la píldora

**Pedido original (cliente):**
"Puedes remover el icono de Apartamento de la vista mobil de /paquetes."

**Status:** implementado, pendiente confirmar visualmente

## Contexto

Tras issue 343, cuando un paquete no tenía unidad asignada, la píldora
mobile (bajo el nombre del residente) mostraba un indicador apagado (🏠
`grayscale opacity-50`) -- el cliente pidió quitar ese ícono también,
directamente.

## Implementación

`packages/_resultados.html`: la píldora mobile ahora es condicional a
`p.direccion_corta` -- con unidad asignada, se sigue mostrando la píldora
de dirección (ámbar/roja); sin unidad, no se renderiza NADA en mobile (ni
texto ni ícono). La columna de desktop (`<td>` separado, oculto en
mobile) NO se tocó en este pedido puntual -- sigue mostrando el indicador
apagado, ver issue 346 para la investigación relacionada sobre por qué
ese mismo ícono no aparece activo donde antes sí lo estaba (desktop perdió
el botón activo en issue 343, sin que quedara claro si eso era parte del
pedido original o alcance excedido -- pendiente de confirmar con el
cliente).

## Tests

Suite `test_packages.py`: 229 passed (sin cambios de conteo -- el `<span>`
retirado no tenía ningún assert dependiente).

## Verificación

Pendiente confirmación visual del cliente.

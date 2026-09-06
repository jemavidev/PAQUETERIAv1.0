# 311 — Torre/Apto y "conectados" como íconos DENTRO del campo `q` (no botones/barra aparte)

**Pedido original (cliente):** la primera implementación de issue 309 (picker de Torre/Apto)
agregó un botón cuadrado nuevo en la fila de íconos de filtro, que abría un panel con borde
propio ocupando todo el ancho de la barra -- el cliente lo rechazó explícitamente: "no fuiste
capaz de implementar el sistema de Torre/Apartamento en la barra de búsqueda que te pedí, por tu
parte creaste un nuevo botón que invoca una nueva barra con esta funcionalidad". Pidió además
mover el ícono de "conectados" (issue 308) al mismo tratamiento, con el mismo criterio de
activación de issue 310 para ambos.

**Status:** la mitad Torre/Apto de este issue fue REMOVIDA en issue 309 (el cliente pidió
deshacer toda la búsqueda por Torre/Apto tras esta 2da ronda de UI). La mitad "conectados"
(reubicarlo como ícono dentro del campo `q`, con el mismo criterio de activación de issue 310)
SÍ se mantiene -- eso nunca fue parte del pedido de remover, sigue implementado y en verde.

## Diseño confirmado (AskUserQuestion, 3 opciones con preview)

Elegido: **ícono dentro del mismo campo de texto** -- ni "conectados" ni "Torre/Apto" son
botones cuadrados en la fila de filtros. Ambos viven como íconos pequeños DENTRO del mismo
recuadro del campo `q` (a la derecha, después del texto), cambiando de color (no de fondo)
cuando están activos. El picker de Torre/Apto se despliega como un dropdown `absolute` anclado
a ESE campo (no una sección nueva con borde propio que ocupe todo el ancho de la barra).

## Regla de activación (issue 310, extendida acá a los 2 íconos)

- `conectados`: `disabled` si `hay_conexiones` es `False` para el `q` actual (sin cambios de
  issue 310, solo reubicado visualmente).
- Torre/Apto: `disabled` si el catálogo de unidades está vacío (`torre_apto_disponible`) -- a
  diferencia de `conectados`, no depende de `q` (el catálogo es fijo por página), así que no
  necesita actualizarse tras cada fetch de búsqueda en vivo.

## Sin parpadeo mientras se escribe (pedido explícito)

El estado habilitado/deshabilitado de "conectados" se actualiza SOLO cuando la petición
`actualizar()` responde -- el debounce de 300ms + `AbortController` que cancela peticiones
viejas (ya existente desde issue 308) es lo que evita que el ícono aparezca/desaparezca en
cada tecla mientras el staff sigue escribiendo.

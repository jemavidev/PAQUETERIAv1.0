# 55 — `/mis-datos` y `/mis-paquetes`: tabs mobile más grandes y uniformes entre las 2 vistas

**Pedido original (cliente):** "se ve bastante bien, solo necesitaria que
en la grilla que acabas de crear hagas que sea somo un poco mas grande.
Adicional a esto necesito que en la vista '/mis-paquetes' apliques la misma
logica de la grilla para que se vea uniforme las 2 vistas."

**Status:** verificado (el cliente confirmó "el tamano es perfecto, en las
2 vistas" en `test.papyrus.com.co`, pidió después resaltar cada tab con
fondo/borde — ver [[56]])

## Contexto

Ajuste directo sobre [[54]] (grid 2x2 de tabs en `/mis-datos`, recién
verificado como buen resultado por el cliente) + extenderlo a
`/mis-paquetes`, que tenía el mismo problema (`flex-1` + `whitespace-nowrap`
compitiendo) pero no había sido tocado en 54 porque el pedido original era
específico de `/mis-datos`.

## Implementación

**Tabs más grandes en mobile** (`app/web/templates/customer/verify.html`):
`px-3 py-2 text-sm` → `px-3 py-3 text-base` en mobile, con `lg:py-2
lg:text-sm` para que el tamaño en desktop quede exactamente igual que
antes. También `gap-1` → `gap-2` entre celdas del grid (`lg:gap-1`
preserva desktop).

**Mismo patrón replicado en `/mis-paquetes`**
(`app/web/templates/customer/paquetes.html`): contenedor
`flex gap-1 overflow-x-auto border-b` → `grid grid-cols-2 gap-2 ...
lg:flex lg:gap-1 lg:overflow-x-auto`, y los 4 botones con las mismas
clases que `/mis-datos` (`flex-1 text-center leading-tight px-3 py-3
rounded-lg text-base ... lg:py-2 lg:text-sm lg:whitespace-nowrap`). Acá
los 4 tabs (Anunciados/Recibidos/Entregados/Cancelados) son siempre fijos
(sin tab condicional como "Residentes" en /mis-datos), así que el grid 2x2
no tiene el caso borde de un tab impar quedando solo en la última fila.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()` en ambos archivos.
- `tests/web/test_customer_verify.py` + `tests/web/test_mis_paquetes.py`:
  62/62.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co`, en un dispositivo móvil
  real, que el tamaño se sienta "un poco más grande" (no exagerado) y que
  las dos vistas se vean uniformes entre sí.

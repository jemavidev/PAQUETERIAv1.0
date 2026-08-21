# 151 — `/paquetes`: 🏠 apagado (gris) en vez de "🏢❌" para "sin apartamento, no editable"

**Pedido original:** "Necesito que remplaces estos emojis 🏢❌... necesito que lo actualices y solo
uses este 🏢, pero lo vas a dejar desactivado o de color gris para que haga lo mismo" -- y en un
segundo pedido, cambiar además 🏢 por 🏠 ("el de la casa"), con 3 opciones presentadas (🏠/🏡/🏘️),
eligió la 1.

**Status:** implementado

## Contexto

Columna "Dirección" de la tabla de `/paquetes` (`_resultados.html`): un paquete `ANUNCIADO`/
`RECIBIDO` sin unidad ofrece un botón (ahora 🏠) que abre "Asignar apartamento"; uno
`ENTREGADO`/`CANCELADO` sin unidad no tiene nada que ofrecer (estado terminal, fuera de
`ESTADOS_CORREGIBLES`) -- antes se marcaba con el emoji compuesto "🏢❌".

## Fix (2 rondas)

1. Mismo ícono (🏢 primero, después 🏠 tras el segundo pedido) en los dos casos -- la diferencia
   la da el estilo, no un emoji distinto.
2. **Bug real encontrado en vivo, ronda 2**: el primer intento usó `text-slate-300` (mismo
   criterio que "Sin teléfono registrado" en `/residentes`) -- pero ESE ícono es SVG
   (`fill="currentColor"`, hereda el color de texto); un emoji es un glifo a color de la fuente
   del sistema, que **ignora por completo** cualquier `text-*` de Tailwind. El usuario reportó
   que el 🏠 seguía viéndose a todo color pese a la clase. Corregido con `grayscale` (filtro CSS
   real) + `opacity-50`, que sí desatura el glifo.

## Verificación

- `tests/web/test_packages.py::test_icono_asignar_apartamento_en_anunciado_y_recibido_sin_unidad`:
  actualizado para verificar el `<span class="grayscale opacity-50 ...">🏠</span>` exacto.
- Suite `/paquetes`: 171/171.
- Render real contra `localhost:8010` confirmando la clase en el HTML devuelto.

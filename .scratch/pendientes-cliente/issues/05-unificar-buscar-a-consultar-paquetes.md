# 05 — Unificar "Buscar" → "Consultar" en todo lo relacionado a paquetes

**Pedido original (cliente):** "necesito que unifiques 'Buscar' --> 'Consultar',
la idea es que lo que se consultan son paquetes, estos no se buscan,
confirmame donde podrias cambiar esta palabra en este contexto."

**Status:** verificado

## Alcance confirmado con el cliente

Se encontraron 6 ocurrencias de "Buscar". Se le presentó el desglose y
confirmó (`AskUserQuestion`, opción recomendada): **solo cambia lo que es
sobre paquetes**; `/residentes` (busca un CLIENTE, no un paquete) se queda
como "Buscar" — coherente con la razón que dio el propio cliente.

### Cambia a "Consultar"

- `base.html` líneas 321 y 329 — enlace del footer mobile que apunta a
  `/consultar` (una vez para no-autenticado, otra para autenticado).
- `search/form.html` línea 11 — botón de envío de `/consultar`.
- `components/_busqueda_filtros.html` línea 56 — default de `texto_boton`
  del macro (hoy solo lo usa `/paquetes`, que no lo sobreescribe).
- `components/_busqueda_filtros.html` línea 62 — label fijo "Buscar" arriba
  del campo de texto, visible solo cuando `mostrar_estado=True` (solo
  `/paquetes`).

### Se queda igual

- `customers_manage/search.html` línea 9 — botón de `/residentes` (busca
  personas, no paquetes) — sigue pasando `texto_boton='Buscar'` explícito,
  así que no le afecta el cambio del default.

## Verificación

- [x] Render local (tests dedicados) confirma "Consultar" en footer (mobile,
      ambas variantes), `/consultar` y `/paquetes` (botón + label) — y
      "Buscar" intacto en `/residentes`.
- [x] 229/229 `tests/web/` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `b0b5531`) y confirmado en
      vivo vía `curl` en `/consultar`: 0 ocurrencias de "Buscar", 3 de
      "Consultar" (footer mobile, nav desktop, botón de envío).

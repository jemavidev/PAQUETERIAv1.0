# 128 — Recibir: lista de residentes como chips (no oración con comas)

**Pedido original (cliente):**
"Seria mejor si solo muestras la lista de los residentes asi como has
echo en los otros flujos 'Residentes actuales: ROBERTO DIAZ, RESIDENTE
PARA MOVER, ELENA RUIZ, MARIO PAZ.' por ejemplo, solo los nombre en una
lista distinguible y algo compacto, tu sabes similar a los otros,
recuerda SOLO EL NOMBRE del residente"

Refina [[127]] (aviso de residentes al declarar unidad nueva desde
Recibir), que originalmente mostraba "Residentes actuales: X, Y, Z."
como una sola oración con comas.

**Status:** implementado

## Implementación

- `components/_picker_apartamento.html`: el contenedor
  `picker-residentes-{id_prefix}` pasa de `<p>` a `<div>` (necesita
  contener elementos de bloque).
- `components/_recibir_paquete.html`, `pickerElegirTorre` (rama
  liviana): en vez de `textContent` con nombres unidos por coma, arma
  una etiqueta "Residentes actuales" + chips compactos
  (`rounded-full`, `bg-slate-100`, `text-xs`) con SOLO el nombre de
  cada residente -- sin badge de estado (ya se había quitado de las
  tarjetas de candidato en [[125]]) ni ningún otro dato. Caso "Libre"
  sin cambios (sigue siendo un solo párrafo).
- Tailwind: rebuild + `?v=` de 48 a 49.

## Verificación

- Tests existentes de [[127]] (markup estático) siguen pasando sin
  cambios -- el cambio es puramente JS/visual.
- Playwright contra el servidor local real: 3 residentes de una unidad
  real (Torre 8/403) se ven como 3 chips separados, solo el nombre en
  mayúsculas, con la etiqueta "Residentes actuales" arriba.
- Suite completa: pendiente de confirmar.
- Pendiente: deploy a test.papyrus.com.co.

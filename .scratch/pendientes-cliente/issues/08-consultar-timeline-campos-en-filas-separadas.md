# 08 — `/consultar` timeline: cada campo en su propia fila

**Pedido original (cliente):** "mejoro bastante, pero seria bueno separar
y poder distinguir los diferentes campos, realiza un anlisis de los
campos y permite que se puedan distinguir entre uno y otro."

**Vista:** `search/form.html` (`/consultar`, resultado) + componente
compartido `components/_timeline.html` (`paso_timeline`).

**Status:** verificado

## Análisis de campos (hecho antes de implementar)

Por paso del timeline existen hasta 6 campos distintos, mezclados hoy en
solo 2 líneas (fecha+actor inline, chips en fila envuelta):

| Campo | En qué pasos aplica |
|---|---|
| Fecha | Todos |
| Actor | Todos |
| Tipo | Solo Recibido |
| Condición | Solo Recibido |
| Guía | Solo Recibido, si se capturó |
| Motivo | Solo Cancelado |

## Qué hacer

- `paso_timeline()` (`components/_timeline.html`): reemplazar los
  parámetros `fecha`/`actor`/`chips` (líneas separadas + chips envueltos)
  por un único `campos=[(etiqueta, valor), ...]` — cada uno renderiza como
  su propia fila (etiqueta izquierda, valor derecha), mismo patrón visual
  que `fila_dato()` (`components/_confirmacion.html`, ya establecido en el
  proyecto para "campo distinguible") pero a escala `text-xs` para caber
  en la tarjeta del timeline.
- `search/form.html`: construir `campos` en el orden Fecha → Actor → Tipo
  → Condición → Guía → Motivo (los que apliquen a ese paso).
- Único caller real de `paso_timeline` en todo el repo — cambio de firma
  seguro, sin romper otras vistas.

## Verificación

- [x] Captura de pantalla (mobile + desktop) confirma cada campo (Fecha,
      Actor, Tipo, Condición, Guía) en su propia fila, etiqueta izquierda
      / valor derecha.
- [x] 13/13 `test_search.py` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `0a73948`) y confirmado
      en vivo con `NSFC`. Deploy automático (pipeline funcionó bien esta
      vez).

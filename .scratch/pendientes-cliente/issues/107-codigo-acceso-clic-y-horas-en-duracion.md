# 107 — Código de acceso clic → /consultar, duración con horas

**Pedido original (cliente), 2 puntos en un mismo mensaje:**
"Ahora en vista /paquetes para la columna 'Cliente' necesito que el codigo
de acceso por ejemplo 'FSS4' sea cliqueable y redirija a la vista
/consultar?q=FSS4. Otra cosa que necesito es que la nueva funcionalidad
que acabas de implementar en el modal de clientes '1 dia', '0 dias' o
similares tambien incluya las horas, por ejemplo '3 dias y 4 horas' o
'16 horas'."

**Status:** implementado

## Contexto

Punto 2 es una evolución directa de [[106]] (mismo día, chip de días
transcurridos recién agregado) -- no una corrección de bug, sino más
precisión pedida sobre la marcha al ver el resultado en vivo.

## Implementación

- **Punto 1** (`_resultados.html`, columna Cliente): el `<span>` del
  código de acceso pasa a `<a href="/consultar?q={{ p.access_code }}">`,
  mismo patrón ya usado en `/mis-paquetes` (issue 46) -- sin
  `target="_blank"`, navegación normal en la misma pestaña, para
  consistencia entre las dos vistas que ya resuelven el mismo enlace.
- **Punto 2** (`packages.py`): `_dias_transcurridos` (devolvía un `int` de
  días CALENDARIO vía `hora_local`) se reemplaza por
  `_duracion_transcurrida` (devuelve un `str` ya formateado, ej. "3 días y
  4 horas" / "16 horas" / "0 horas"). Cambio de cálculo, no solo de
  formato: con horas en el texto, la aproximación de calendario (cruzar
  medianoche cuenta como "1 día" aunque hayan pasado pocas horas) ya no es
  coherente -- "3 días y 4 horas" solo tiene sentido si son 3*24+4 horas
  reales. Se cambió a duración real (`fin - received_at` en segundos,
  sin pasar por `hora_local`). `None` si nunca se recibió (mismo criterio
  que antes). La plantilla ya no pluraliza "día(s)" por su cuenta -- el
  string ya viene formateado completo desde Python.

## Verificación

- `tests/web/test_packages.py`: los 9 tests de `_dias_transcurridos`/chip
  de [[106]] se reescriben para `_duracion_transcurrida` (None sin
  recibir, "X horas" bajo 24h, "X días y Y horas" sobre 24h, "X días" sin
  resto exacto, singular/plural, prioridad delivered/cancelled, chip
  ausente en ANUNCIADO, teléfono+dirección sin romper por el cambio) +
  nuevo test del link `/consultar?q=` en la columna Cliente.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

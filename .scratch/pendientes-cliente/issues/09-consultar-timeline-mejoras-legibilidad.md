# 09 — `/consultar`: verbo contextual, fecha resaltada, letra más grande, días desde recibido, sección superior separada, hora 12h

**Pedido original (cliente):** "Se ve mucho mejor, pero ahora necesito
que cambien el contexto de 'Actor' a (Anuncio, Recibio, Entrego o
Cancelo). Ademas necesito que la fecha se vea resaltada ya que es uno
de los campos mas importantes. La letra en general del contenido de las
tarjetas esta pequena, seria bueno que esten un poco mas grande. Seria
bueno colocar la cantidad de dias que tiene un paquete desde que se
recibio (ejemplo 5 dias)... En la parte superior de la linea de tiempo...
veo que aqui los campos sigues estando todo muy juntos (direccion en
general), seria bueno separar asi como hiciste con los estados, que se
vea de forma diferente. Para la hora en los estado seria bueno colocar
12horas con AM y PM."

**Vista:** `search/form.html` + `components/_timeline.html` (`/consultar`).

**Status:** verificado

## Qué se hizo

1. **Actor → verbo contextual**: label "Actor" reemplazado por el verbo
   del paso (Anunció/Recibió/Entregó/Canceló según `h.titulo`).
2. **Fecha resaltada**: `paso_timeline()` gana soporte de `destacado` por
   campo (`campos` pasa de pares `(etiqueta, valor)` a tripletas
   `(etiqueta, valor, destacado)`) — Fecha es `destacado=True` (negrilla),
   sin forzar mayúsculas (no aporta en una fecha).
3. **Letra más grande**: filas de campos del timeline `text-xs` → `text-sm`.
4. **Días desde recibido**: calculado en `search.py`
   (`dias_desde_recibido`, diferencia con `paquete.received_at`) —
   aplica para cualquier estado posterior a Recibido, no atado a un paso
   puntual. Se muestra en la sección superior de la tarjeta (dato del
   paquete, no de un hito).
5. **Sección superior separada**: Teléfono/Apartamento/Días desde recibido
   ahora son filas con `fila_dato()` (mismo patrón reusado de la
   confirmación de `/anunciar` y ahora del timeline) — antes eran párrafos
   sueltos sin etiqueta.
6. **Hora en 12h con AM/PM**: construido a mano (`strftime('%I:%M')` +
   AM/PM explícito según `hour < 12`) en vez de `%p` de `strftime`, para
   no depender del locale del servidor (en `es_CO` `%p` podría devolver
   "a. m."/"p. m." en vez de "AM"/"PM").

## Verificación

- [x] Captura de pantalla (mobile + desktop) confirma los 6 cambios:
      "Anunció"/"Recibió" en vez de "Actor", Fecha en negrilla, letra más
      grande, "Días desde recibido: 0 días" en la sección superior,
      Teléfono en fila separada con etiqueta, hora "03:00 PM"/"03:11 PM"
      en 12h con AM/PM.
- [x] 13/13 `test_search.py` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `704d9fe`) y confirmado
      en vivo con `NSFC`. Deploy automático.

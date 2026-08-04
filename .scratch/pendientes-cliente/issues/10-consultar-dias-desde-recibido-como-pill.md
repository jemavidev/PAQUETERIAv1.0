# 10 — `/consultar`: "Días desde recibido" como pill destacado, sin etiqueta

**Pedido original (cliente):** "de que manera puedes hacer que el numero
de 'Dias desde recibido' se convierta en por ejemplo '1 dia' o '7 dias',
y que este dato se resalte de otra manera pero en esa misma seccion" →
aclaración: "Solo que diga '5 dias' sin el 'Días desde recibido'".

**Vista:** `search/form.html` (`/consultar`, sección superior del resultado).

**Status:** verificado

## Qué hacer

- Quitar la fila `fila_dato('Días desde recibido', ...)` (ticket 09) de la
  lista de campos.
- Mostrar SOLO el valor ("5 días"/"1 día", ya pluralizado — esa lógica ya
  existía desde el ticket 09, no cambia) como un pill de color, sin
  etiqueta, justo debajo de la fila nombre+badge de estado.
- Color distinto a los 4 roles de estado ya usados (ámbar=Anunciado,
  azul=Recibido, verde=Entregado, rojo=Cancelado) para no confundirse con
  un badge de estado — se usa índigo, libre en la paleta actual.

## Verificación

- [x] Render local + captura confirman el pill "0 días" sin la etiqueta
      "Días desde recibido", en índigo (distinto del badge de estado).
- [x] 13/13 `test_search.py` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `5158a8f`) y confirmado
      en vivo con `NSFC` (mobile + desktop). Deploy automático.

# 400 — `/residentes` móvil: tarjeta por residente con botones grandes (mismo patrón que `/paquetes`)

**Pedido original (Jesús):** "me puedes mostrar cómo se vería esta vista "/residentes" si aplicas lo mismo que en la
vista de /paquetes, esto enfocado a la versión móvil ... serían unos botones en la parte inferior del residente y que
sea de 2 líneas, decide cuál dejas arriba y cuáles abajo".

**Status:** implementado; aprobado por Jesús ("ahora sí se ve bien todo"), pendiente confirmar en test

## Decisiones (propuestas)

- Arriba, línea 1: nombre completo (`text-lg`) + píldora con el total de paquetes (enlace a `/paquetes`) + basurero
  de Admin, separado de los botones de uso diario (en la ficha no existe "Eliminar residente": no puede salir de móvil).
- Arriba, línea 2: Principal / Auto / De baja / Bloqueado / Eliminado + Torre · Apto + teléfono o @WhatsApp, en una
  línea (corta con "…").
- Abajo: 4 espacios FIJOS, activos o apagados, siempre en el mismo orden -- WhatsApp, Llamar, Unidad (👫, comparte
  apartamento) y Asignar (solo activo sin apartamento). Ícono arriba y nombre corto abajo (56 px de alto): 4 botones
  con texto a lo ancho no caben en 390 px. Ronda 2, pedido de Jesús: "que en la parte inferior donde están los íconos
  se puedan tener hasta 4 íconos, estén activos o no" (antes eran 3, con el tercero variable y "Ver ficha").
- Franja de color: azul para Principal, rojo para eliminado/bloqueado, gris para el resto.
- Residentes sin ficha propia: tarjeta gris sin botones, "vive con X · sin ficha propia".
- Solo < 640 px; la tabla de escritorio no cambia.

## Vista previa

Rama `prototipo/residentes-movil-tarjetas` (ronda 1 `1d205e8`, ronda 2 con 4 espacios), servidor `:8011` sobre la BD local.

## Ronda 3

**Pedido (Jesús):** "sería bueno que todo esté inline" -- ícono y nombre en la misma línea en cada botón (como en
`/paquetes`), en vez de ícono arriba y nombre abajo.

Con 4 botones en el ancho del celular el espacio es justo: cabe sin cortarse a 360-390 px con letra de 11 px e ícono de
14 px (medido: ningún botón desborda); a 320 px (celulares muy angostos) todavía se corta. Alternativas si la letra
resulta chica: volver a ícono arriba / nombre abajo (ronda 2), o 2 filas de 2 botones más grandes.

## Ronda 4 y aprobación

"Los 4 botones de WhatsApp, llamar, unidad y asignar deben estar inline" -- una sola fila de 4 (se descartan las dos
filas de 2). Jesús: "ahora sí se ve bien ... despliega a localhost y test.papyrus.com.co".

## Verificación

- `tests/web/test_residentes_movil_tarjetas.py` (5): tarjeta por residente solo en móvil y tabla solo en escritorio;
  siempre 4 botones en el orden WhatsApp/Llamar/Unidad/Asignar con los apagados en su lugar; Asignar activo sin
  apartamento y Unidad con unidad compartida; el basurero solo para Admin y fuera de la fila de botones. Escritas
  después de traer la plantilla de la vista previa (no se vieron fallar antes).
- Ajustadas a propósito en `test_customers_manage.py`: el conteo de enlaces a la ficha (+2 por la tarjeta; se agrega
  que haya una sola tarjeta) y del nombre (+1). 201 en verde.
- Tailwind reconstruido, `?v=105`. Capturas a 390/360 px revisadas; a 320 px los textos de los botones se cortan.
- Vista previa apagada; rondas en la rama `prototipo/residentes-movil-tarjetas`.

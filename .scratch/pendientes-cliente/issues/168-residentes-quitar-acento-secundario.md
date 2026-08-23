# 168 — `/residentes`: quitar el acento rojo de "Secundario"

**Pedido original:** "veo que en la vista de /residentes existen una especie de etiquetas tipo
rojo/gris donde se resalta al lado izquierdo de un residente... no tengo claro a qué se debe" →
tras la explicación (marca "Secundario", issue 71), pedido explícito: "remueve esa marca y dime si
hay otras similares en esta vista."

**Status:** verificado

## Cambio

`customers_manage/search.html`: quitado `es_secundario` y la clase condicional
`border-l-4 border-l-red-400` de la fila de la tabla de resultados.

Otras 3 marcas similares que SÍ se quedan en esta misma vista (reportadas al cliente, no
removidas -- no se pidió): píldora verde "Auto" (`autoriza_recepcion_automatica`), píldora azul
"Principal" (`p.ocupante.es_principal`), ícono 👫 "comparte apartamento" ([[156]]/[[160]]).

Nota aparte (informada, no tocada): la ficha individual (`/residentes/<id>`, `detail.html`) tiene
una marca análoga -- el mismo acento rojo en el borde de sus 4 tabs cuando el residente es
Secundario. Distinta vista, el cliente pidió específicamente "en esta vista" (la lista) -- queda
pendiente de que confirme si también la quiere quitar ahí.

## Verificación

- Test existente reescrito (`test_lista_muestra_badge_principal_no_badge_secundario_pero_si_acento`
  → `test_lista_muestra_badge_principal_no_badge_secundario_ni_acento`, invierte la aserción final).
- Suite completa: 1070/1070 (ver [[167]] para el número previo a este cambio; reconfirmado con
  este también incluido).
- Verificado en vivo contra `localhost:8010`.

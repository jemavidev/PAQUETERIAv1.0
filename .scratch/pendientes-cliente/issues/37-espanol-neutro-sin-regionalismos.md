# 37 — Eliminar regionalismos (voseo) del texto de la app

**Pedido original (cliente):** "Veo en varias partes que utilizas palabras
como (vos, podés, entre otras), estas palabras no corresponden a una region
que hable espanol neutro, nada de regionalismos."

**Status:** verificado

## Implementación

Barrido completo de `src/app/web/templates/` (texto renderizado Y comentarios
de documentación de componentes) buscando voseo. Encontrado y corregido en 6
archivos:

- `customer/verify.html` — 6 ocurrencias (Elegí→Elige, querés→quieres, vos
  podés→puedes, podés→puedes, "(vos)"→"(tú)" x2, "Vos pasarás"→"Tú pasarás").
- `customer/no_verificado.html` — podés→puedes.
- `customer/paquetes.html` — tenés→tienes.
- `components/_carga_fotos.html` — Arrastrá→Arrastra, elegí→elige.
- `components/_estado_vacio.html` — corregido en los ejemplos de uso
  (docstring, no texto renderizado) para no modelar voseo a futuros usos.
- `packages/list.html` — elegí→elige, Probá→Prueba, Podés→Puedes.

Fuera de alcance a propósito: "acá" (vs "aquí") no se tocó -- es un
regionalismo léxico más amplio y ambiguo, no una conjugación de voseo; el
cliente señaló específicamente "vos, podés" como ejemplos, así que el barrido
se acotó a formas verbales/pronombre de 2da persona voseante.

Tests: `test_sin_paquetes_muestra_mensaje_vacio` (existente) actualizado al
nuevo texto neutro de `/mis-paquetes`.

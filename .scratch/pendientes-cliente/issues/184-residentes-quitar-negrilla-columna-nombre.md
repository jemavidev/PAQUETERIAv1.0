# 184 — `/residentes`: quitar negrilla de la columna Nombre

**Pedido original:** "en la columna Nombre de la vista /residentes esta en negrilla, quitale las
negrillas"

**Status:** implementado

## Cambio

- `customers_manage/_resultados.html`: el link de la columna Nombre pasa de `font-semibold` a
  `font-medium` -- mismo peso que ya usa `/paquetes` en su columna equivalente ("Cliente", el
  `<td>` trae `font-medium` en `packages/_resultados.html`), continuando la unificación de [[183]].

## Verificación

- Suite completa.
- Verificado en local (`localhost:8010`): la clase `font-medium` está compilada (ya usada en
  todo el proyecto), sin necesidad de rebuild de `tailwind.css`.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

# 184 — `/residentes`: quitar negrilla de la columna Nombre

**Pedido original:** "en la columna Nombre de la vista /residentes esta en negrilla, quitale las
negrillas"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Cambio

- `customers_manage/_resultados.html`: el link de la columna Nombre pasa de `font-semibold` a
  `font-medium` -- mismo peso que ya usa `/paquetes` en su columna equivalente ("Cliente", el
  `<td>` trae `font-medium` en `packages/_resultados.html`), continuando la unificación de [[183]].

## Verificación

- Suite completa.
- Verificado en local (`localhost:8010`): la clase `font-medium` está compilada (ya usada en
  todo el proyecto), sin necesidad de rebuild de `tailwind.css`.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

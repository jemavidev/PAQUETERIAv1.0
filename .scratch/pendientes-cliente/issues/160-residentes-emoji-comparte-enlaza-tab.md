# 160 — `/residentes`: el ícono 👫 enlaza a la tab Residentes

**Pedido original:** "Este emoji 👫 debería tener un acceso directo al tab de ese residente,
específicamente en la opción donde se visualizan los residentes."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Cambio

`customers_manage/search.html`: el `<span>👫</span>` de [[156]] pasa a `<a href="/residentes/<id>?tab=residentes">👫</a>` -- mismo mecanismo `?tab=` ya usado en el resto de la app (ver [[157]]/[[159]]). Sin
texto ni número visible, mismo criterio original de [[156]].

## Verificación

- Test extendido (`test_lista_muestra_icono_comparte_apartamento_con_dos_o_mas_ocupantes`): además
  de comprobar que el emoji aparece, comprueba el `href` correcto.
- Efecto colateral esperado y corregido: `test_resultados_no_se_duplican_si_varios_criterios_
  coinciden` contaba ocurrencias del ID de la Persona en el HTML para detectar filas duplicadas
  -- con el nuevo link, una Persona que comparte unidad ahora aparece 3 veces (Nombre + 👫 + Ver
  ficha) en vez de 2; el test se actualizó para reflejarlo, no es una fila duplicada real.
- Suite completa: 1046/1046.
- Verificado en vivo contra `localhost:8010`.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

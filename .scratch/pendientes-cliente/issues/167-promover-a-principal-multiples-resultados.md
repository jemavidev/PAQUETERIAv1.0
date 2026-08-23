# 167 — `promover_a_principal` revienta con `MultipleResultsFound` (efecto secundario de [[166]])

**Pedido original:** reporte en vivo -- "http://localhost:8010/residentes/e1dd0cdc-.../ocupantes"
con "Internal Server Error" al intentar mudar a ANGELICA ARRAZOLA a otro apartamento (vía "+
Agregar un nuevo Residente" en la ficha de otro residente, con el checkbox "Mudar residente acá").

**Status:** implementado

## Diagnóstico

Traceback real capturado en el log del servidor: `promover_a_principal` línea ~861,
`sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required`.

Mismo bug que [[166]], en una función hermana que no se tocó en ese fix: la consulta que busca "el
Principal anterior a degradar" tampoco filtraba `desvinculado_en IS NULL`. Antes del fix del
índice único en [[166]], la base de datos hacía **imposible** que existiera más de una fila
`es_principal=True` por unidad (activa o no) -- así que este bug quedaba tapado por accidente. Con
el índice ya corregido para permitir historial (una activa + viejas desvinculadas), una unidad con
2+ Principales históricos revienta esta consulta (`.one_or_none()` exige 0 o 1 resultado) en vez
de encontrar solo al activo.

Reproducido con los datos reales del cliente: la unidad de Angelica (Torre 2 · Apto 302) había
tenido antes a Jesús como Principal (ya desvinculado) -- al mover a Angelica (Principal actual) e
intentar promover a Daniela en su lugar, `promover_a_principal` buscó "el Principal anterior" y
encontró DOS filas (Jesús viejo + Angelica activa).

## Cambio

`promover_a_principal` (`ocupante_service.py`): agregado `Ocupante.desvinculado_en.is_(None)` a la
consulta de `anterior`. Barrido completo de las 6 consultas `es_principal.is_(True)` del dominio
para confirmar que no quedaba ninguna otra con el mismo filtro faltante -- las otras 4 ya lo
tenían (una desde antes, tres corregidas hoy en [[166]] y en la sesión previa de issue 163).

## Verificación

- 1 test nuevo (`test_promover_con_dos_principales_historicos_no_revienta`) que reproduce
  exactamente el patrón de datos real (Principal viejo desvinculado + Principal activo + alguien
  nuevo a promover).
- Suite completa: 1070/1070 (antes de sumar [[168]]).
- Verificado con el traceback real del servidor local antes y después del fix.

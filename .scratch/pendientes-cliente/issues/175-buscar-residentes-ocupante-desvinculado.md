# 175 — `_buscar_residentes`: buscar por Ocupante trae a Principales de unidades donde esa persona ya no vive

**Pedido original:** reportado en vivo -- al buscar "dan" en `/residentes` aparecían "ANGELICA
ARRAZOLA, DANIELA ARRAZOLA y JESUS VILLALOBOS". Analizado y confirmado con datos reales de la
base local: Angelica es correcta (Principal actual de la unidad donde Daniela vive HOY), pero
Jesus no tiene relación vigente con "dan" -- es Principal de una unidad donde Daniela vivió antes
(ya desvinculada). Mismo patrón exacto que [[166]]/[[167]] ("solamente en el caso que un
Ocupante se desvincule, deberían estar unidos por el HISTORIAL, no como si siguiera viviendo
ahí"), pero en una consulta con forma distinta (`Ocupante.nombre.ilike`, no `es_principal`) que el
barrido de esas issues no cubrió -- vive en la capa de rutas (`customers_manage.py`), no en el
dominio (`ocupante_service.py`) donde se hizo ese barrido. Confirmado con auditoría completa de
las 22 consultas contra `Ocupante` en todo el repo: esta es la ÚNICA que falta.

**Status:** implementado (superado por [[176]], ver esa issue -- el mecanismo completo que este fix
corregía se quitó en el seguimiento inmediato; el diagnóstico y el fix en sí siguen siendo
correctos mientras el mecanismo existió, se deja el registro tal cual)

## Diagnóstico

`_buscar_residentes` (`customers_manage.py`), 2 consultas sin filtrar `desvinculado_en IS NULL`:

1. `ocupantes_match = db.query(Ocupante).filter(Ocupante.nombre.ilike(f"%{termino}%")).all()` --
   matchea Ocupantes DESVINCULADOS (histórico), no solo activos. Un nombre que alguna vez pasó
   por una unidad (aunque se haya mudado hace meses) sigue "contaminando" esa unidad en la
   búsqueda para siempre.
2. `principales = db.query(Ocupante).filter(Ocupante.apartamento_id.in_(apto_ids_de_ocupantes),
   Ocupante.es_principal.is_(True)).all()` -- con el índice único de [[166]] ya corregido para
   permitir historial (una fila activa + viejas desvinculadas con `es_principal=True`), esta
   consulta podría devolver MÁS de un "principal" por unidad si alguna tuvo varios a lo largo del
   tiempo.

Reproducido con datos reales de la base local: Daniela Arrazola tuvo un Ocupante en TORRE 1 · APT
302 (Principal actual: Jesus Villalobos), desvinculado el 22 de agosto -- su unidad actual es
TORRE 2 · APT 302. Buscar "dan" sigue trayendo a Jesus por el registro viejo.

## Cambio

- `customers_manage.py` (`_buscar_residentes`): agregar `Ocupante.desvinculado_en.is_(None)` a
  ambas consultas (`ocupantes_match` y `principales`), mismo patrón exacto que el fix de [[166]]
  en `ocupante_service.py`.

## Verificación

- Tests nuevos en `test_customers_manage.py` reproduciendo el escenario exacto: Ocupante
  desvinculado con nombre que matchea el término, en una unidad DISTINTA a la actual -- confirmar
  que el Principal de la unidad vieja YA NO aparece en los resultados; confirmar que el Principal
  de la unidad ACTUAL de la persona sí sigue apareciendo (caso legítimo, no romperlo).
- Suite completa.
- Verificado en local (`localhost:8010`) reproduciendo el caso real ("dan" ya no trae a Jesus,
  sigue trayendo a Angelica).

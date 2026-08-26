# 179 — `/residentes`: padding superior igual al de `/paquetes`

**Pedido original:** "necesito que la parte superior de las vitas /paquetes y /residentes sea
igual en tamanos, espacios, margenes y demas, la idea es que se vea unificado el software"

**Status:** implementado

## Diagnóstico

Comparado línea por línea contra `packages/list.html`: el bloque superior (H1 mobile + barra de
búsqueda vía `busqueda_filtros()`) ya era estructuralmente idéntico desde issue 172 -- mismas
clases, mismo macro compartido. La única diferencia real era el padding vertical del contenedor
raíz, arrastrado de antes de esa unificación: `/residentes` tenía `pt-6 pb-16 md:pb-6`,
`/paquetes` tiene `pt-4 pb-16 md:pb-4`.

## Cambio

- `customers_manage/search.html`: `pt-6 pb-16 md:pb-6` → `pt-4 pb-16 md:pb-4` (mismas clases que
  `packages/list.html`, ya compiladas, sin rebuild de CSS necesario).

## Hallazgo NO aplicado (fuera de alcance de este pedido, informado al cliente)

`/paquetes` usa una fuente distinta (Nunito Sans, `#vista-paquetes` en `list.html`) al resto de la
app -- incluido `/residentes`, que usa la fuente default de `base.html`. Fue una decisión
deliberada y explícitamente acotada a esa sola vista (conversación 2026-08-17, comentario propio
del código: "Mismo alcance de siempre: SOLO acá, no en base.html"). No se tocó -- es un cambio más
grande (tipografía, no solo espaciado) que ameritaría confirmación explícita antes de extenderlo o
revertirlo.

## Verificación

- Suite completa.
- Verificado en local (`localhost:8010`): el contenedor raíz de ambas vistas trae exactamente
  `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 pb-16 md:pb-4`.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

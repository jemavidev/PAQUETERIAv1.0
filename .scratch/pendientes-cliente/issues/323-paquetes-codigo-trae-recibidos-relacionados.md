# 323 — `/paquetes`: buscar un código de acceso trae también los RECIBIDO relacionados

**Pedido original (cliente):** "Al consultar en la vista /paquetes por un codigo de acceso, la
idea es que el sistema muestre todos los paquetes con estado recibido de un mismo cliente, esto ya
que por lo general si tienen 3 paquetes recibidos, la idea es que al consultar uno de esos
paquetes se muestren los otros paquetes de este mismo cliente o los residentes del apartamento, se
esta forma se puedan mostrar todos los paquetes con una sola consulta."

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-06, commits `bf2e54f`/`3b4e544`
en PaqueteX) -- pendiente que el cliente lo confirme visualmente.

## Decisiones de alcance (confirmadas con el cliente antes de implementar)

1. "Mismo cliente" = mismo `recipient_phone` (no nombre -- evita falsos positivos de nombres
   repetidos, mismo criterio que ya usa el resto del módulo).
2. Los RECIBIDO del mismo destinatario Y los de otros residentes de su misma unidad se muestran
   SIEMPRE juntos (no uno como fallback del otro) -- cubre el caso real: entregar todo lo de un
   apartamento de una sola consulta.
3. Alcance acotado a `/paquetes` (staff autenticado) -- NO se extiende a `/consultar` (pública sin
   sesión): hacerlo ahí revelaría paquetes de terceros a partir de un solo código conocido,
   contradiciendo el trabajo de [[322]].

## Diseño

El patrón de "traer los paquetes relacionados de una persona" ya existía parcialmente:
`condiciones_busqueda_paquetes` (búsqueda por teléfono en `/paquetes`) ya trae todos los paquetes
de un destinatario, y `_persona_resuelta.html` (`/announce`) ya muestra "Ya tiene paquetes en
curso" con píldoras por código. Lo nuevo es que un código de acceso EXACTO (que por diseño solo
puede calzar con 1 Paquete, es único) dispare esa misma expansión, acotada a `RECIBIDO`.

`paquetes_relacionados_por_codigo` (nueva función de dominio) se activa SOLO con match EXACTO de
`access_code` -- un fragmento sigue la búsqueda de texto libre normal (parcial, sin relacionados).
Ignora a propósito el filtro de `estado`/pestaña activa de `/paquetes` en ese momento: es una
consulta puntual por código, no una navegación de listado, así que el filtro pasivo no debe
esconder el propio resultado buscado -- buscar el código de un paquete `ANUNCIADO` también revela
sus `RECIBIDO` relacionados. El paquete buscado va siempre primero.

## Implementación

- `app/domain/paquete_service.py::paquetes_relacionados_por_codigo(session, q)`: si `q` calza
  exacto con un `access_code`, devuelve `[principal, *relacionados]` -- relacionados = `RECIBIDO`
  con mismo `recipient_phone` O misma terna `snapshot_conjunto/torre/apartamento` (unión de los 2
  criterios, sin duplicar). `None` si `q` no calza con ningún código (el caller sigue con la
  búsqueda normal).
- `app/web/routes/packages.py::_listar`: antes de armar la consulta de texto libre de siempre,
  intenta la expansión; si aplica, la usa en vez de la consulta filtrada/paginada. De ahí para
  abajo, ambos caminos comparten la MISMA resolución batch y el mismo enriquecimiento por fila
  (candidatos de corrección, timeline, WhatsApp, etc.) -- el conjunto expandido son Paquetes
  reales como cualquier otro, la plantilla no distingue de dónde salieron. Devuelve un 4to valor,
  `agrupado_por_codigo: bool`, para que la plantilla sepa si vale la pena aclarar en pantalla de
  dónde salen los resultados "de más".
- `app/web/templates/packages/_resultados.html`: nota informativa ("Se muestran también los demás
  paquetes recibidos del mismo cliente o de su apartamento") solo cuando la expansión trajo más de
  un resultado.

## Verificación

- 8 tests nuevos en `tests/web/test_packages.py`: mismo destinatario, misma unidad (2 destinatarios
  distintos), estado no-RECIBIDO excluido, búsqueda parcial no dispara expansión, código de un
  ANUNCIADO también trae RECIBIDO relacionados, orden (principal primero), nota visible/ausente
  según corresponda.
- Suite completa `tests/web/test_packages.py`: 217/217 en verde (sin regresiones).
- En vivo contra el servidor real de dev (`localhost:8010`): 2 paquetes RECIBIDO del mismo
  teléfono (`3011112222`) -- buscar el código del primero (`Y3E6`) trajo también el segundo
  (`Y97Y`) y mostró la nota.

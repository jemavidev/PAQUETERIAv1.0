# Optimización: búsqueda de texto libre de /paquetes

**Origen:** pedido del cliente (2026-09-06) -- "verifica que todas las vistas carguen en tiempos
adecuados y optimizados, por ejemplo la vista de /paquetes ha estado bastante lenta últimamente" +
follow-up explícito: "separalo y vamos a implementar la mejor opción... necesito que las búsquedas
sean lo más optimizadas posibles... creo que se estarán agregando 20 a 30 paquetes diarios... unos
500 cambios diarios si incluimos todo."

**Por qué directorio aparte de `.scratch/pendientes-cliente/`:** eso es para pedidos puntuales
sobre vistas ya desplegadas (texto, color, comportamiento). Esto es una optimización de base de
datos real, diagnosticada con `diagnosing-bugs` (reproducción con `EXPLAIN ANALYZE` contra datos
sintéticos a escala, no solo lectura de código), con su propia migración de Alembic -- amerita
seguimiento propio.

## Diagnóstico (resumen -- ver issue 01 para el detalle completo)

`condiciones_busqueda_paquetes` (motor de búsqueda de `/paquetes`, reusado por la píldora "N
paquetes" de `/residentes` y por el badge "Mostrar conexiones") armaba un único `OR` que mezclaba
columnas de `paquetes` con columnas de `personas` después de un `outerjoin`. Un `ILIKE '%texto%'`
(comodín al inicio) nunca puede usar un índice B-tree; y un `OR` que cruza dos tablas tras un join
tampoco puede usar índices aunque existan (Postgres no puede decidir por-tabla qué descartar) --
confirmado con `enable_seqscan=off`. Resultado: cada búsqueda era un full table scan de `paquetes`,
repetido hasta 3 veces por petición en `/paquetes`, y una vez POR RESIDENTE en `/residentes`.

Medido contra 50.000 paquetes sintéticos (simulación de escala futura -- la tabla real solo tenía
31 filas, insuficiente para que doliera todavía, pero a 20-30 paquetes/día el crecimiento es real y
constante):

| Vista | Antes | Después del fix completo |
|---|---|---|
| `/paquetes` sin búsqueda | 368 ms | 92 ms |
| `/paquetes?q=<dígitos>` | 540 ms | 115 ms |
| `/paquetes?q=<nombre, match acotado>` | ~400 ms | 30 ms |
| `/residentes` (20 residentes/página) | **~2990 ms** | 162 ms |

## Estado

Implementado y verificado localmente (issue 01). Pendiente: revisión final del usuario, y decidir
plan de despliegue a test.papyrus.com.co / producción (la migración usa `CREATE INDEX
CONCURRENTLY`, pensada para no bloquear escrituras durante el despliegue).

## Issue 02 -- carga diferida del historial en el modal "Ver"

Problema distinto detectado en el mismo hilo: percepción de lentitud de `/paquetes` **en
localhost** (no test.papyrus.com.co), por el peso del HTML inicial -- cada fila incluye el
historial completo del modal "Ver", casi nunca abierto. Ver
[issue 02](issues/02-carga-diferida-historial-modal-ver.md) para el detalle completo (diagnóstico,
implementación, errores encontrados y verificación). Implementado y verificado localmente
(1450/1450 tests del repo en verde); **no desplegado** -- pedido explícito del cliente de solo
localhost.

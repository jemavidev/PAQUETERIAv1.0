# 77 — `/paquetes` y `/mis-paquetes` se sentían pesados al navegar (N+1)

**Pedido original (cliente):** "antes de realizar el deploy necesito que
analices porque en la version que tienes en test.papyrus.com.co la vista de
/paquetes o cualquier otra se sentia pesada al realizar consultar entre
ellas o de paquetes o de clientes, despues que soluciones el porque pasa,
quiero que lo apliques a esta version de localhost y por ultimo si desplega
todo en TEST.PAPYRUS.COM.CO"

**Status:** verificado

**Nota de proceso:** este pedido se enrutó por el skill `diagnosing-bugs`
(fila "algo va lento sin explicación" de la tabla de ruteo de CLAUDE.md) en
vez de pasar primero por este registro liviano, así que este archivo se
escribió retroactivamente al cerrar el trabajo — para que el rastro escrito
quede completo igual, sin depender de la memoria de la conversación.

## Diagnóstico

Causa raíz medida (no adivinada): `_listar()` en `/paquetes`
(`packages.py`) disparaba de 3 a 5 consultas SQL de
Persona/Usuario/Apartamento/Ocupante **por cada paquete** de la página — un
N+1 clásico (medido: 35 queries para 10 paquetes). Bajo navegación
concurrente esto agotaba el pool de conexiones por defecto de SQLAlchemy
(`pool_size=5` + `max_overflow=10` = 15), causando que las requests se
encolaran -- medido contra el sitio real: 10 requests concurrentes a
`/paquetes` escalaron de 0.98s a 19.9s.

Se investigó también "cualquier otra" vista (tal como pedía el cliente):
`/residentes` resultó ya optimizado de una auditoría previa (batch ya
aplicado en `customers_manage.py`), sin cambios necesarios. `/mis-paquetes`
(`customer_paquetes.py`) sí tenía el mismo patrón vía
`timeline_de_paquete`/`listar_fotos`, agravado por no paginar el historial
completo del apartamento.

## Implementación

Batch-resolución: en vez de una consulta por paquete, se resuelven TODAS
las Personas/Usuarios/Apartamentos/Ocupantes/fotos que la página/historial
completo necesita en un puñado fijo de consultas, luego lookups en memoria
por paquete -- mismo patrón ya usado en `customers_manage.py`.

- `packages.py`: `_personas_por_id`/`_usuarios_por_id` (batch por página).
- `paquete_correccion_service.py`: `candidatos_correccion_por_paquetes`
  (batch de `candidatos_correccion`), con `_construir_candidatos` compartido
  entre ambas versiones.
- `paquete_timeline_service.py`: `timelines_de_paquetes` (batch de
  `timeline_de_paquete`), con `_armar_timeline` compartido.
- `paquete_foto_service.py`: `fotos_por_paquetes` (batch de `listar_fotos`).
- `customer_paquetes.py`: usa las 2 versiones batch de arriba.

Commit: `3de01fb` (rama `PaqueteXv.2`).

## Verificación

- Suite completa: 802/802 tests pasando, incluyendo 2 tests de regresión
  nuevos que cuentan queries SQL reales (`test_lista_no_dispara_una_query_
  de_persona_o_usuario_por_paquete`, `test_lista_no_dispara_una_query_de_
  actor_o_foto_por_paquete`) -- confirmado RED antes del fix, GREEN
  después, en ambos.
- Local (`localhost:8010`): 10 requests concurrentes a `/paquetes` pasaron
  de escalar a ~0.79-0.81s parejos.
- Producción (`test.papyrus.com.co`): desplegado vía el flujo de `git
  worktree` documentado (`jemavidev/PaqueteX`), CI verde, contenedor
  reconstruido. La reproducción original (10 curl concurrentes) da ahora
  tiempos parejos (~0.5-1.7s), sin la escalada original.
- Code-review de dos ejes (Standards + Spec) corrido después del deploy
  (retroactivo, no bloqueante) -- sin hallazgos bloqueantes en ningún eje.

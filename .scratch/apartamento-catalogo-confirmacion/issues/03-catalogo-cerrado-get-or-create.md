# 03 — Catálogo cerrado: `get_or_create_apartamento` resuelve, ya no crea

**What to build:** `apartamento_service.get_or_create_apartamento` cambia de semántica: de "crear si no existe" a "resolver contra el catálogo ya sembrado (ticket 02), fallar explícitamente si la terna no está". Deja de tomar `conjunto` como argumento del llamador — lo resuelve internamente contra el nombre vigente (ticket 01). Ningún flujo puede volver a crear una fila en `apartamentos` fuera de la migración de seed. `buscar_apartamento_por_terna` (de solo lectura) no cambia.

**Blocked by:** 02.

**Status:** done

- [x] Resolver una terna Torre/Apartamento que sí está en el catálogo devuelve el Apartamento sembrado, sin crear ninguna fila nueva.
- [x] Resolver una terna que NO está en el catálogo lanza `ValueError` explícito y no crea nada.
- [x] Dos formatos de la misma terna válida (casing/espacios distintos) siguen resolviendo al mismo Apartamento (dedup ya existente, sin regresión).
- [x] La función ya no recibe `conjunto` como parámetro — lo resuelve internamente contra el Conjunto vigente (ticket 01). Renombrada `get_or_create_apartamento` → `resolver_apartamento` (la semántica vieja del nombre ya no aplicaba).
- [x] Los dos llamadores de producción (`customer_verify.py`, `announce_new.py`) se actualizan a la firma nueva, con `try/except ValueError` propio para no convertir un typo de catálogo en un 500 — siguen enviando texto libre de Torre/Apartamento hasta los tickets 04/05.
- [x] Suite de tests actualizada.

## Hallazgo que amplió el alcance real de este ticket

`get_or_create_apartamento` no la llamaban solo los 2 sitios de producción anticipados: la llamaban **~50 veces en ~19 archivos de test** de otras features (Ocupante, mudanza, declarar unidad, búsqueda de residentes, ciclo de vida de Paquete, notificaciones, OTP, anonimización) como fixture genérica (`"Las Flores"/"Torre A"/"101"`), sin ninguna relación con este ticket. Cerrar el catálogo rompía las ~50. Se corrigieron como parte de este mismo ticket (no se abrió uno nuevo — es la misma pieza, mecánica en casi todos los casos):

- Los literales se remapearon a unidades reales del catálogo (Torre A→TORRE 1, B→TORRE 2, C→TORRE 3, D→TORRE 4, Z→TORRE 5), preservando la distinción entre unidades que cada test necesitaba.
- Un test (`test_customers_manage.py::test_resultados_no_se_duplican_si_varios_criterios_coinciden`) dependía genuinamente de que la Torre fuera texto libre (`"Gómez"`, para coincidir con un nombre en una búsqueda) — no era mecánico. Se reescribió preservando el intento original (dos criterios de búsqueda distintos resolviendo a la misma Persona no deben duplicar el resultado) usando `Persona.nombre` + `Ocupante.nombre` en vez de `Persona.nombre` + `Torre`.
- Dos tests sobre el candado viejo "conjunto sin asignar por staff" (retirado en este mismo ticket, ver abajo) quedaron sin premisa — se reescribieron para probar el comportamiento real que lo reemplaza (rechazo por catálogo cerrado, y que enviar `conjunto` a mano no tiene ningún efecto).
- Varias aserciones con conteos absolutos (`Apartamento.count() == 0/1/2`) asumían la tabla vacía al arrancar — se corrigieron a medir por identidad de fila o línea base, no contra cero (mismo patrón que el ticket 02).

## Bug de infraestructura de tests encontrado y corregido

El fixture `client` (`tests/web/conftest.py`) truncaba `apartamentos` al final de cada test — pero el catálogo de 804 unidades solo lo siembra la migración **una vez por sesión** de test. El primer test web que corriera se llevaba el catálogo para siempre. Corregido: `apartamentos` sale de la lista de truncado (pasa a ser tabla de referencia inmutable, nunca crece ni se vacía); `configuracion_conjunto` sigue truncándose, pero el teardown ahora también resetea `apartamentos.conjunto` de vuelta al default (`UPDATE`, no truncate) para que ambos queden sincronizados para el siguiente test.

## Efecto colateral de UI (no corregido, fuera de alcance de este ticket)

`customer/paquetes.html` renderiza `Torre {{ p.snapshot_torre }}` crudo. Con el catálogo cerrado, `snapshot_torre` ahora contiene el nombre completo (`"TORRE 2"`), así que el texto se ve como "Torre TORRE 2" (redundante). Es un ajuste de plantilla, no de dominio — queda para cuando se toque esa vista (tickets 04/05 tocan formularios, no esta pantalla de solo lectura).

## Implementación

- `apartamento_service.resolver_apartamento(session, torre, apartamento)` reemplaza `get_or_create_apartamento` — resuelve contra el Conjunto vigente (`configuracion_conjunto_service.obtener_nombre_conjunto`) + la terna normalizada; `ValueError` si no hay match. `buscar_apartamento_por_terna` no cambia (Grupo 16 "Corregir" sigue pasando `conjunto` explícito, porque resuelve desde el snapshot congelado de un Paquete, no desde el Conjunto vigente).
- `customer_verify.py`: se retira el bloque de "conjunto no asignado por staff" (obsoleto — dead code una vez que `resolver_apartamento` no toma `conjunto`); `partes_apto` pasa a `[torre_v, apartamento_v]`; la llamada queda en `try/except ValueError`.
- `announce_new.py`: mismo `try/except`; el campo `conjunto` del formulario se sigue leyendo pero ya no se usa (retirarlo del formulario es trabajo del ticket 05).
- Docstrings desactualizadas corregidas: `apartamento.py`, `apartamento_service.py`, `0021_seed_catalogo_apartamentos.py`.
- **Suite completa:** 580 passed (6 deselected — mismos fallos preexistentes de `test_layout.py` de los tickets 01/02, confirmados no relacionados).

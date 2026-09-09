Status: ready-for-agent
Feature: migracion-por-anio
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, módulo 3 de 5) ·
CONTEXT.md (glosario) · `alembic/versions/0003_paquetes_usuarios.py` (origen de
`uq_paquetes_access_code`)

---

## Problem Statement

El `access_code` de un Paquete (4 caracteres, alfabeto de 31 símbolos sin ambigüedad visual,
923.521 combinaciones posibles) es único para siempre en toda la tabla — nunca se reutiliza. A un
volumen proyectado de 600.000-700.000 paquetes por año, el segundo año se queda sin códigos nuevos
disponibles. El cliente necesita que el residente siga tratando con un código corto de 4 caracteres
(fácil de leer/dictar/escribir) mientras su paquete está vigente, pero que ese espacio de 4
caracteres se pueda reciclar entre años sin comprometer la unicidad ni las consultas ya enviadas por
WhatsApp mientras el paquete sigue activo.

## Solution

Todo paquete nuevo sigue recibiendo un `access_code` de 4 caracteres, sin ningún cambio en cómo se
genera hoy. Una acción manual de administrador — **"Migrar año"**, bajo `/administracion` — le
agrega un sufijo de **2 dígitos del año** (ej. "25") al `access_code` de todo paquete que haya
llegado a un estado terminal (`Entregado` por `delivered_at`, o `Cancelado` por `cancelled_at`) en
el año calendario anterior al actual, dejándolo en 6 caracteres. Lo que sigue activo (`Anunciado`/
`Recibido`), sin importar su antigüedad, nunca se migra — su código de 4 caracteres puede seguir
siendo el enlace vigente que el cliente ya tiene guardado.

Al liberarse el código de 4 caracteres de un paquete migrado, queda disponible para asignarse de
nuevo a un paquete distinto en un año posterior — sin colisión posible con el código viejo de 6
caracteres (longitudes distintas). El cliente decidió, de forma explícita e informada, aceptar el
riesgo residual de que un enlace público muy viejo guardado por un residente pueda —si ese mismo
código de 4 caracteres se reasigna— terminar mostrando el paquete de otra persona; como mitigación
parcial se agrega un límite de intentos por minuto a la consulta pública, que hoy no tiene ninguno.

## User Stories

1. Como sistema, quiero que un paquete nuevo siga recibiendo un `access_code` de 4 caracteres sin
   ningún cambio en la generación actual, para que nada cambie para el cliente mientras su paquete
   está activo.
2. Como admin, quiero un botón "Migrar año" bajo `/administracion` que, al presionarlo, le agregue 2
   dígitos del año anterior al `access_code` de los paquetes elegibles, para liberar ese espacio de
   4 caracteres para el año siguiente.
3. Como sistema, quiero considerar elegible para migrar a un paquete `Entregado` cuya
   `delivered_at` caiga en el año anterior al actual.
4. Como sistema, quiero considerar TAMBIÉN elegible para migrar a un paquete `Cancelado` cuya
   `cancelled_at` caiga en el año anterior al actual — un paquete cancelado nunca tiene fecha de
   entrega, así que quedaría atrapado para siempre con un código de 4 caracteres si solo se mirara
   `delivered_at`.
5. Como sistema, NO quiero migrar nunca un paquete que sigue `Anunciado` o `Recibido` (activo, sin
   resolver), sin importar cuántos años lleve así — migrarlo le rompería el enlace público vigente a
   alguien que todavía está esperando su paquete.
6. Como admin, antes de confirmar la migración, quiero ver cuántos paquetes se verían afectados,
   para no ejecutar la acción a ciegas.
7. Como sistema, quiero que el botón siempre migre exactamente el año calendario anterior al
   actual (sin selector de año), para mantener la acción simple y predecible.
8. Como sistema, quiero que volver a presionar "Migrar año" para un año ya migrado sea un no-op
   seguro — solo toca paquetes cuyo `access_code` todavía tiene 4 caracteres, así que lo ya migrado
   no se vuelve a tocar ni se corrompe con un segundo sufijo.
9. Como sistema, al generar un `access_code` nuevo, quiero seguir comparando por igualdad exacta
   contra los códigos existentes (sin ningún cambio en esa lógica) — un código viejo ya migrado a 6
   caracteres nunca puede colisionar con uno nuevo de 4, por tener longitudes distintas.
10. Como miembro del staff, quiero poder seguir buscando un paquete migrado por su código de 6
    caracteres en la búsqueda de texto libre de `/paquetes`, sin que haga falta ningún cambio ahí —
    ya funciona por coincidencia de texto libre sobre cualquier longitud.
11. Como cliente que consulta `/consultar`, NO quiero que se me bloquee la consulta si intento
    razonablemente pocas veces por minuto, pero SÍ quiero (como negocio) que se limite a 10 intentos
    por minuto por origen, para reducir el riesgo de que alguien intente enumerar códigos al azar.
12. Como sistema, al superar el límite de 10 intentos por minuto en `/consultar`, quiero responder
    con el mismo patrón de rate-limit (mensaje + status 429) que ya usan `/otp/solicitar` y el login
    de staff, para mantener consistencia en todo el sistema.
13. Como cliente, entiendo y acepto (decisión explícita, informada) que un enlace público muy viejo
    que guardé podría, en un caso raro, terminar mostrando el paquete de otra persona si ese mismo
    código de 4 caracteres se reasignó — el sistema no bloquea la consulta pública por año para
    evitar esto.

## Implementation Decisions

- **Sin cambios en la generación de `access_code`** (`paquete_service.py`) — sigue generando
  siempre 4 caracteres del alfabeto actual, comparando por igualdad exacta contra
  `Paquete.access_code` para evitar colisiones. Esto ya es suficiente: un código migrado a 6
  caracteres no puede coincidir por igualdad con un candidato de 4.
- **Nueva función `migrar_codigos_del_anio(session, anio, ejecutar=True) -> ResumenMigracion`** en
  `paquete_service.py` — selecciona `Paquete` con `length(access_code) = 4` y (`estado = 'ENTREGADO'
  AND extract(year from delivered_at) = anio`) OR (`estado = 'CANCELADO' AND extract(year from
  cancelled_at) = anio`). Con `ejecutar=False` solo cuenta y devuelve el total (vista previa, sin
  tocar filas); con `ejecutar=True` además actualiza cada `access_code` agregándole los últimos 2
  dígitos de `anio` como sufijo.
- **Ruta nueva de admin** (`admin.py`): `/administracion/migrar-anio` — GET calcula y muestra el
  conteo de elegibles para el año calendario anterior al actual (`ejecutar=False`); POST ejecuta la
  migración real (`ejecutar=True`) y confirma cuántos se migraron. Exclusiva de `require_admin`.
- **Rate-limit en `/consultar`** (`search.py`): se agrega `Depends(rate_limit("consultar_publico",
  10, 60))`, mismo mecanismo genérico (`rate_limit.py`) ya usado en `password_reset.py`,
  `customer_auth.py` y `auth.py` — respuesta 429 con el mismo patrón de mensaje ya establecido en
  esas rutas.
- **Sin cambios** en el índice GIN de trigramas de `access_code`, en la búsqueda de staff de
  `/paquetes`, ni en `paquetes_relacionados_por_codigo` — todos ya operan por comparación/coincidencia
  de texto sin asumir una longitud fija.
- **Riesgo aceptado explícitamente por el cliente**: la consulta pública (`/consultar`) no distingue
  por año — un `access_code` de 4 caracteres reciclado en un año posterior podría, en un caso raro,
  coincidir con un enlace viejo guardado por otro residente. Se documenta como decisión consciente,
  no como omisión.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la función/ruta, qué queda en
`access_code` después, qué status HTTP responde) — nunca aserciones sobre el código interno.

- **Seam 1 — `migrar_codigos_del_anio`**: nuevo archivo o extensión de
  `tests/data_model/test_paquete_service.py` (o el que ya cubra `paquete_service.py`). Cubrir: un
  paquete `Entregado` del año anterior con código de 4 caracteres queda con 6 tras migrar; un
  paquete `Cancelado` del año anterior también migra (por `cancelled_at`); un paquete `Anunciado` o
  `Recibido` del año anterior NO migra, sin importar su antigüedad; un paquete ya migrado (6
  caracteres) no se vuelve a tocar en una segunda corrida; `ejecutar=False` cuenta correctamente sin
  modificar ninguna fila; un paquete `Entregado` del año VIGENTE no se incluye.
- **Seam 2 — `/administracion/migrar-anio`**: `tests/web/test_admin_*.py` (prior art de estilo:
  `test_admin_conjunto.py`). Cubrir: acceso exclusivo de admin (operador recibe 403); GET muestra el
  conteo esperado sin ejecutar nada; POST ejecuta y el conteo coincide con lo realmente migrado.
- **Seam 3 — rate-limit de `/consultar`**: extensión de `tests/web/test_search.py`. Cubrir: 10
  solicitudes en la ventana pasan con normalidad; la 11ª dentro del mismo minuto responde 429 con el
  mensaje esperado, igual patrón que ya cubren los tests existentes de rate-limit en
  `test_customer_auth.py`/`test_auth.py` (o el archivo equivalente que ya pruebe `rate_limit()` para
  esas rutas).

## Out of Scope

- Cualquier selector de año en el botón "Migrar año" — siempre migra el año calendario anterior al
  actual, sin excepción.
- Cualquier mecanismo para reducir el riesgo residual de colisión de enlaces públicos viejos más
  allá del rate-limit (ej. bloquear `/consultar` por año, exigir un dato adicional de verificación)
  — riesgo aceptado explícitamente por el cliente.
- Migrar paquetes que nunca llegan a un estado terminal (quedan `Anunciado`/`Recibido` para
  siempre) — caso raro, sin resolver en esta versión.
- Cualquier cambio a la búsqueda pública o de staff para exponer o filtrar explícitamente por año.
- Capturar o mostrar al staff/cliente el "año" de un paquete como un campo propio — el año se infiere
  del sufijo del `access_code` una vez migrado, no se agrega una columna nueva para esto.

## Further Notes

- El volumen real que motiva este módulo (600.000-700.000 paquetes/año) se confirmó directamente
  con el cliente durante el `/grilling` — no es una proyección especulativa del lado de Claude.
- Se descartó explícitamente, tras plantearlo, bloquear la consulta pública por año (opción que
  habría eliminado el riesgo de colisión por completo) — el cliente prefirió aceptar el riesgo y
  agregar solo el rate-limit, priorizando que la consulta de 4 caracteres siga funcionando sin
  fricción adicional para el cliente final.

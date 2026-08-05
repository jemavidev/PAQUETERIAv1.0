# 48 — `/mis-datos`: Torre/Apartamento pasan a ser de solo lectura, asignación exclusiva del staff

**Pedido original (cliente):** "en esta vista [Apartamento de /mis-datos], la
idea sería que este flujo no lo modifique el residente u ocupante, la idea es
que ellos puedan visualizar la torre y el apartamento que se les ha asignado
y autorizado, esta asignación solo la podrá hacer el staff, estos datos serán
de solo lectura para los residentes u ocupantes. Dime si el staff tiene la
opción de hacer esto? Adicional de qué forma podría mejorar la forma en que
se verá la torre y el apartamento... Por último siempre debe aparecer (solo
lectura) el nombre del conjunto."

**Status:** implementado

## Contexto

Antes de este pedido, `/mis-datos` dejaba que CUALQUIER residente (principal,
o quien aún no tenía apartamento) "declarara" su propia Torre/Apartamento vía
un picker (`resolver_apartamento` + `declare_unit`), lo cual además creaba su
Ocupante automáticamente. El staff (`/residentes/{id}`) no tenía ningún campo
ni ruta para asignar o cambiar la unidad de un cliente — se verificó
explícitamente antes de tocar código, respondiendo la pregunta del cliente:
**no, el staff no tenía esa opción.**

Se prototipó la representación visual (skill `prototype`, sub-shape A,
embebido en el header/tabs reales de `/mis-datos`) con 3 conceptos: A) placa
tipográfica, B) edificio esquemático + marcador, C) ficha con avatar. El
cliente eligió **B** ("Edificio + marcador"), con un ajuste: que el marcador
resalte solo UNA ventana (el apartamento específico), no toda la fila/piso.

## Implementación

**`/mis-datos` (residente) — `customer_verify.py` + `verify.html`:**
- Se retiró por completo el auto-declare: ya no se leen `torre`/`apartamento`
  del POST, ni se llama `resolver_apartamento`/`declare_unit` desde acá. El
  tab "Apartamento" es siempre de solo lectura, sin excepción (antes solo lo
  era para el Ocupante no-principal).
- Nuevo contexto `nombre_conjunto` (`configuracion_conjunto_service.
  obtener_nombre_conjunto`) — visible siempre, con o sin apartamento asignado.
- Tarjeta rediseñada (concepto B elegido): edificio SVG con una sola ventana
  resaltada en azul + marcador "Apto {número}", Torre como título, Conjunto y
  Apartamento como filas debajo. Estado vacío: edificio en gris/punteado +
  aviso "Aún no tienes un apartamento asignado por el personal de Papyrus."
- El panel "Apartamento" salió del `<form>` de Datos/Notificaciones (ya no
  hay nada que "Guardar" le mande).

**`/residentes/{id}` (staff) — `customers_manage.py` + `detail.html`:**
- Nueva ruta `POST /residentes/{persona_id}/apartamento`: resuelve la terna
  contra el catálogo cerrado (`resolver_apartamento`) y aplica con
  `move_resident` (ya existía en el dominio, sin cambios). Soporta asignar,
  cambiar, y desvincular (dejando ambos campos vacíos).
- Mismo guard que tenía el autoservicio del residente: si la Persona sigue
  siendo Ocupante activo de OTRA unidad, la reasignación se rechaza con un
  mensaje claro (evita dejar el roster de Ocupantes huérfano).
- Nueva tarjeta "Torre y Apartamento" en la ficha, con el mismo picker
  Torre→Apartamento en cascada que antes vivía en `/mis-datos`.
- No se tocó la gestión de Ocupantes existente (`agregar_ocupante`,
  confirmar, promover, etc.) — sigue siendo un paso separado y deliberado del
  staff, ahora desbloqueado porque ya puede asignar el apartamento primero.

Sin migraciones nuevas (no se tocó el modelo de datos, solo qué actor puede
escribir `apartamento_actual_id` y desde dónde).

## Verificación

599 → 606 tests pasan (598 + 8 nuevos en `test_customers_manage.py` para la
ruta de asignación/guard/invariante de snapshot; `test_customer_verify.py`
reescrito para reflejar que Torre/Apartamento ya no se autodeclaran — los
fixtures de setup pasan a usar `agregar_ocupante` directo en vez de pasar por
la ruta retirada). 6 fallos preexistentes de `test_layout.py` sin relación
(mismo problema de elegibilidad OTP documentado desde antes de este pedido).

Prototipo visual verificado interactivamente por el cliente antes de
implementar (3 conceptos, eligió B, pidió el ajuste de una sola ventana
resaltada — aplicado).

Desplegado y confirmado visualmente por el cliente en vivo (2026-08-05) --
encontró y se corrigió un problema real: el edificio SVG no se veía porque
Tailwind es un paso de build en este proyecto (no JIT), y las clases
arbitrarias nuevas no estaban en el CSS ya compilado (mismo patrón que
issues 39/45). Recompilado + cache-bust `?v=28`→`?v=29`.

Segunda vuelta de ajustes pedidos tras ver la tarjeta en vivo:
- Reordenar Conjunto → Torre → Apartamento (antes Torre era el título grande
  y Conjunto/Apartamento filas chicas); Conjunto ahora un poco más grande que
  Torre/Apartamento, los 3 en negrilla.
- Quitar "Estos datos los asigna el personal de Papyrus." -- irrelevante
  para el cliente.

De paso, a pedido del cliente ("necesito que analices, verifiques y puedas
corregir lo relacionado a git, github, ci/cd"): se encontró y corrigió que
CI llevaba en rojo desde el 2026-08-04 en TODOS los commits (incluso los que
no tocaban nada de esto) -- causa raíz: tests huérfanos/desactualizados en el
repo de deploy (ver commit `9c7c4ad` en jemavidev/PaqueteX), sin relación
con esta feature salvo coincidir en el tiempo. CI y Deploy to Staging quedan
ambos en verde por primera vez desde esa fecha.

Pendiente: que el cliente confirme esta segunda vuelta visualmente (cambia
`Status` a `verificado`).

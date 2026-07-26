# Anunciar simplificado + resolución de destinatario por staff

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 1.

## Problem Statement

Hoy, para anunciar un paquete, el residente debe decidir explícitamente "a nombre de quién" llega (a mi nombre / otra persona registrada / solo un nombre) — una decisión que le añade fricción y que además expone si un teléfono está o no registrado en el sistema (filtración de información entre residentes). El residente solo quiere avisar rápido que espera un paquete; decidir con precisión a nombre de quién queda mejor en manos del staff, que puede cruzar el nombre anunciado contra lo que ya está registrado para ese teléfono y corregir errores (typos, personas distintas en el mismo apartamento) sin que el cliente se entere de nada de eso.

Además, hoy el sistema genera dos códigos al anunciar (`tracking_number` y `access_code`) pero ninguno de los dos cumple bien su función: `access_code` se genera y se muestra pero nunca se usa para nada, y `tracking_number` es un código interno que no corresponde a lo que el negocio realmente necesita (la guía del transportador, que ya existe como `guide_number` y la captura el staff al recibir).

## Solution

`/anunciar` se reduce a 3 campos: Nombre, Teléfono, Aceptar Términos y Condiciones. El sistema registra (o reutiliza) la Persona del anunciante por su teléfono, y crea el Paquete con el nombre tal cual lo escribió el cliente — sin pedirle que elija "a nombre de quién". Si ese nombre no coincide con el nombre ya registrado para ese teléfono, el Paquete queda marcado con una **advertencia visual** en la lista de staff (`/paquetes`) para que el staff lo revise y corrija — la corrección en sí (asociar a la persona correcta, cambiar destinatario, completar apartamento) se resuelve en la vista de staff `/announce` (ver ticket separado, fuera de esta rebanada).

Se elimina `tracking_number` de todos los flujos. `access_code` se conserva como el único código de consulta del cliente, con un formato corto y sin ambigüedad: 4 caracteres, sin los caracteres que se confunden visualmente (`0`, `1`, `O`, `I`, `L`), y nunca con la secuencia `666`.

La pantalla de éxito muestra Nombre, Teléfono, código de acceso, Torre y Apartamento (si el anunciante ya tiene uno asignado), y dos enlaces: consultar el paquete y actualizar datos personales (este último lleva a `/otp` para verificarse, ya que el cliente no tiene sesión en `/anunciar`).

## User Stories

1. Como residente, quiero anunciar un paquete escribiendo solo mi nombre y mi teléfono, para no tener que decidir detalles que no me competen.
2. Como residente, quiero aceptar los Términos y Condiciones al anunciar, para que el anuncio sea válido.
3. Como residente, quiero recibir un código de acceso corto y fácil de leer/dictar por teléfono, para poder consultar mi paquete después sin confundirme con caracteres ambiguos.
4. Como residente, nunca quiero ver el teléfono de otra persona asociado a un nombre al anunciar, para que mi privacidad y la de otros residentes se respete.
5. Como residente, quiero ver en la pantalla de éxito mi nombre, teléfono, código de acceso, torre y apartamento (si aplica), para confirmar que el anuncio quedó bien.
6. Como residente, quiero un enlace directo para actualizar mis datos personales desde la pantalla de éxito, para completar mi perfil sin fricción justo después de anunciar.
7. Como residente, quiero un enlace directo para consultar mi paquete desde la pantalla de éxito, para no tener que recordar navegar a `/consultar` por mi cuenta.
8. Como miembro del staff, quiero ver en `/paquetes` una advertencia visual cuando el nombre anunciado no coincide con el nombre ya registrado para ese teléfono, para saber cuáles anuncios necesitan revisión.
9. Como miembro del staff, no quiero que un anuncio con advertencia bloquee las acciones normales del paquete (recibir/entregar/cancelar), para poder seguir operando aunque la advertencia esté pendiente de resolver.
10. Como desarrollador, quiero que `tracking_number` deje de existir en el esquema y en el código, para no mantener un campo que no cumple ninguna función de negocio.
11. Como desarrollador, quiero que el generador de `access_code` nunca produzca un código con la secuencia "666" al inicio o al final, para respetar la sensibilidad cultural pedida.
12. Como desarrollador, quiero que la función de dominio `announce` siga aceptando los tres modos de `Destinatario` existentes (`yo_mismo`, `persona_registrada`, `solo_nombre`) para los llamadores que ya los usan (tests de otras rebanadas, y el futuro flujo completo de staff en `/announce`), y que la simplificación de `/anunciar` sea un nuevo modo agregado, no un reemplazo que rompa a los demás.
13. Como miembro del staff, quiero que la advertencia de nombre-no-coincide se calcule al mostrar la lista (comparando contra el nombre actual de la Persona), no que se guarde congelada, para que si el staff corrige el nombre de la Persona la advertencia desaparezca sola sin una acción extra.
14. Como residente, quiero que mi teléfono anunciante quede como el teléfono de contacto de notificación por defecto de este paquete (hasta que el staff lo corrija), para que si nadie más se identifica como destinatario, al menos yo me entere de las novedades.

## Implementation Decisions

- **Nuevo modo en `Destinatario`** (`paquete_service.py`): un cuarto constructor (p.ej. `Destinatario.declarado_por_cliente(nombre)`) que resuelve a `recipient_name = nombre` (tal cual lo escribió el cliente) y `recipient_phone = anunciante.telefono` (el mismo teléfono que anuncia) — distinto de `yo_mismo()` (que usa el nombre YA REGISTRADO de la Persona, ignorando lo que se escriba) y de `solo_nombre()` (que deja `recipient_phone = None`). Los tres constructores existentes NO cambian de comportamiento — evita romper los tests de otras rebanadas (recibir/entregar/cancelar/notificaciones/mudanza) que usan `Destinatario.yo_mismo()` como fixture.
- **Ruta `/anunciar` (web)**: se elimina el campo `a_nombre_de` y los campos `destinatario_telefono`/`destinatario_nombre` del formulario y de la ruta. Solo quedan `nombre`, `telefono`, `acepta_tyc`. Internamente llama a `announce(...)` con el nuevo modo `Destinatario.declarado_por_cliente(nombre)`.
- **`access_code`**: nuevo generador con alfabeto reducido — dígitos `2-9` (se excluyen `0` y `1`) + letras mayúsculas excluyendo `O`, `I`, `L` (23 letras válidas: alfabeto de 31 caracteres en total). Genera 4 caracteres al azar; si el resultado contiene la subcadena `"666"` en cualquier posición, se regenera (con solo 4 caracteres, `"666"` solo puede aparecer al inicio o al final, cubriendo el caso pedido). Mantiene su `UniqueConstraint` actual — en el caso (raro, ~1 en 130 mil de espacio) de colisión con un código ya existente, reintentar la generación.
- **`tracking_number`**: se elimina la columna de `Paquete` (migración Alembic nueva, `000X_eliminar_tracking_number`), su generador (`_generar_tracking_number`), su `UniqueConstraint`, y toda referencia en `announce.py`, `search.py`, y las plantillas (`announce/confirmacion.html`, `search/form.html`).
- **Advertencia de nombre no coincide**: no es una columna nueva — se calcula al leer, comparando `paquete.recipient_name` (normalizado a minúsculas/trim para la comparación, no para el guardado) contra el `nombre` actual de la Persona identificada por `paquete.announced_by_persona_id`. Se expone como una propiedad/helper de solo lectura (no persistida) consumida por la plantilla de `/paquetes`. Nota: la comparación es contra el Anunciante, no contra un "Destinatario" separado — hoy el destinatario declarado por el cliente ES el nombre que se compara.
- **Plantilla `announce/confirmacion.html`**: agrega Teléfono, Torre y Apartamento (si `snapshot_apartamento` existe) junto a lo que ya muestra (nombre, código de acceso). Agrega dos enlaces: "Consultar mi paquete" (`/consultar`) y "Actualizar mis datos" (`/otp`, ya que no hay sesión de cliente en este punto).
- **Fuera de esta rebanada, delegado al ticket de `/announce`** (Grupo 6, dependiente de este): la UI/acción real para que el staff corrija un anuncio con advertencia (asociar a la Persona/Ocupante correcta, completar apartamento, editar destinatario). Aquí solo se calcula y se muestra la advertencia.

## Testing Decisions

- Seam de dominio (`tests/data_model/test_announce_paquete.py`): agregar casos para el nuevo modo `Destinatario.declarado_por_cliente` (recipient_name = lo declarado, recipient_phone = el del anunciante), y para el generador de `access_code` (longitud 4, alfabeto correcto, nunca contiene "666", no reutiliza `0/1/O/I/L`). Los tests existentes de `yo_mismo`/`persona_registrada`/`solo_nombre` no deben cambiar — son la prueba de que no se rompió nada al agregar el modo nuevo.
- Seam de dominio nuevo, archivo propio o agregado a `test_announce_paquete.py`: la advertencia de nombre-no-coincide — probar que aparece cuando el nombre anunciado difiere del registrado, y que NO aparece cuando coincide o cuando la Persona es nueva (recién creada por este mismo anuncio, nada que comparar).
- Seam web (`tests/web/test_announce.py`, hoy prueba `/anunciar`): actualizar para el formulario de 3 campos — eliminar los casos que prueban `a_nombre_de`/`destinatario_telefono`/`destinatario_nombre`, agregar el caso feliz simplificado y la pantalla de éxito con los campos nuevos.
- Seam web (`tests/web/test_packages.py`): agregar un caso que confirma que la advertencia se muestra en la lista cuando corresponde.
- Seam web (`tests/web/test_search.py`): eliminar cualquier aserción sobre `tracking_number`; confirmar que la búsqueda exacta ahora es por `access_code`.
- Migración: `tests/data_model/test_migration_graph.py` y `test_parity_esquema_orm.py` (ya existentes, genéricos) deben seguir pasando sin cambios — son el guardrail de que el esquema y el ORM no divergen tras quitar la columna.

## Out of Scope

- La UI/acción de que el staff corrija un anuncio con advertencia — eso es la rebanada de `/announce` (Grupo 6), que depende de esta.
- Fotos/tipo de paquete en la línea de tiempo de `/consultar` — Grupo 2, rebanada separada.
- El botón "anunciar a nombre de un cliente" en `/paquetes` — también Grupo 6/5, depende de esta.
- Cambiar cómo se resuelve el destinatario cuando ya existe un Ocupante sin teléfono — eso lo cablea la rebanada de `/announce` (Grupo 6), que sí conocerá el modelo de Ocupante (ADR-0006).

## Further Notes

- Esta rebanada bloquea a los Grupos 2 (Consultar, que pasa a buscar por `access_code`), 5 (botón "anunciar como staff" en `/paquetes`), 6 (`/announce` completo) y 8 (notificación en `ANUNCIADO`) — implementarla primero y completa antes de continuar con esas.
- El nombre del nuevo modo de `Destinatario` (`declarado_por_cliente`) es una propuesta de esta spec, no viene literal de las notas del usuario — el `/to-tickets`/`/implement` puede ajustarlo si un nombre más claro surge durante la implementación, siempre que preserve el comportamiento descrito.

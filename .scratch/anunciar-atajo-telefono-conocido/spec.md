Status: ready-for-agent
Feature: anunciar-atajo-telefono-conocido
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · issue 314 (`.scratch/pendientes-cliente`, "primera entrega", se reutiliza) · CONTEXT.md (glosario, término "Anuncio" se matiza, ver Further Notes)

---

## Problem Statement

Hoy, en `/anunciar` (vista pública, sin sesión), CUALQUIER cliente que quiera anunciar un paquete tiene que escribir su Nombre y su Teléfono, aunque ya sea un cliente conocido -- alguien a quien el conjunto ya le entregó al menos un paquete antes, y de quien el sistema ya tiene el nombre correcto registrado. Para ese cliente que repite, volver a escribir su nombre cada vez es un paso de más, sin ningún beneficio: el sistema ya sabe quién es.

## Solution

Cuando el Teléfono que el cliente escribe en `/anunciar` ya tiene al menos un paquete `ENTREGADO` histórico a su nombre, el formulario deja de pedir el Nombre por completo -- el cliente solo escribe su Teléfono, acepta los Términos y Condiciones, y el paquete queda anunciado a su nombre YA REGISTRADO. Si el Teléfono nunca recibió un paquete entregado (cliente nuevo, o cliente con solo anuncios pendientes/cancelados), el flujo sigue exactamente como hoy: se le pide el Nombre antes de poder anunciar.

El mecanismo de detección ("¿este teléfono ya recibió algo entregado antes?") ya existe en el sistema -- es la misma pregunta que responde `es_primera_entrega_a_telefono` (issue 314, usada hoy para la bandera "primera entrega" en el modal Entregar de `/paquetes`). Este spec la reutiliza tal cual, negada, en vez de definir un criterio nuevo.

## User Stories

1. Como cliente que ya ha recibido paquetes con este conjunto antes, quiero anunciar un nuevo paquete escribiendo solo mi teléfono y aceptando los términos, sin volver a escribir mi nombre, para que el trámite sea más rápido.
2. Como cliente nuevo (mi teléfono nunca recibió un paquete entregado), quiero que se me siga pidiendo mi nombre al anunciar, igual que hoy, para que el staff sepa quién soy.
3. Como cliente, quiero que el formulario inicial de `/anunciar` muestre solo el campo Teléfono y la aceptación de Términos y Condiciones, sin el campo Nombre visible desde el principio, para no ver un campo que probablemente no necesito llenar.
4. Como cliente cuyo teléfono no es reconocido, quiero que el campo Nombre aparezca automáticamente después de mi primer intento -- sin perder lo que ya escribí en Teléfono ni mi aceptación de Términos -- para completar el trámite sin tener que empezar de cero.
5. Como cliente conocido, quiero que el paquete quede anunciado a mi nombre YA REGISTRADO (no a un nombre que yo escriba), para que no haya discrepancias entre lo que el staff ve y quién soy realmente.
6. Como desarrollador, quiero que "cliente conocido" se determine reutilizando `es_primera_entrega_a_telefono` (negada), para no duplicar la definición de "primera entrega" que ya existe en el sistema.
7. Como desarrollador, quiero que la detección de "conocido" mire `recipient_phone` (a quién le llegó el paquete), no `announced_by_phone` (quién lo anunció), para que el criterio sea "este teléfono ya recibió algo alguna vez" -- decisión explícita del cliente durante el grilling.
8. Como cliente, quiero que un paquete con estado `ANUNCIADO`, `RECIBIDO` o `CANCELADO` (pero nunca `ENTREGADO`) para mi teléfono NO me cuente como "conocido" -- solo un `ENTREGADO` real habilita el atajo.
9. Como cliente, quiero que aceptar los Términos y Condiciones siga siendo siempre obligatorio, sin importar si soy un cliente conocido o no.
10. Como cliente, quiero que el Teléfono siga siendo siempre obligatorio y validado con el mismo formato de hoy, sin importar el camino que tome el formulario.
11. Como cliente, quiero que si mi teléfono tiene un formato inválido, vea ese error de formato de inmediato, antes de que el sistema intente decidir si soy conocido o no.
12. Como cliente, quiero que el límite existente de máximo 10 anuncios activos por teléfono (y su pantalla intermedia "ya tienes N, ¿continuar?") se siga aplicando igual, sin importar si fui reconocido por mi teléfono o no, para que el atajo no debilite esa protección existente.
13. Como negocio, quiero que NO exista ninguna pantalla adicional de "¿Eres [nombre]?" antes de anunciar con el atajo -- decisión explícita, aceptando el riesgo residual de que alguien conozca el teléfono de otra persona y le anuncie un paquete sin su consentimiento.
14. Como desarrollador, quiero que la elección de Destinatario para el camino "conocido" use `Destinatario.yo_mismo()` explícitamente, para que el código sea claro sobre la intención sin depender de que otro constructor se comporte igual por casualidad.
15. Como cliente cuyo teléfono no fue reconocido y que ya está viendo el campo Nombre (2do intento), quiero que el envío funcione exactamente igual que el flujo de hoy (`Destinatario.declarado_por_cliente(nombre)`), sin ningún cambio de comportamiento en ese camino.
16. Como desarrollador, quiero que la ruta de staff (`/announce`, `announce_new.py`) NO se vea afectada por este cambio -- el atajo es exclusivo de la vista pública `/anunciar`.
17. Como desarrollador, quiero que ningún paquete anunciado antes de este cambio, ni ninguno anunciado por staff, se vea afectado retroactivamente -- el atajo solo decide qué campos pedir AL MOMENTO de anunciar, no reescribe nada existente.
18. Como cliente, quiero que no se guarde ninguna marca/bandera especial indicando que anuncié por este atajo -- el cliente lo pidió durante el grilling y luego lo retiró explícitamente del alcance.

## Implementation Decisions

### Detección de "cliente conocido"

- Reutiliza `es_primera_entrega_a_telefono(session, recipient_phone)` (ya existe en `paquete_service.py`, issue 314) negada: `conocido = not es_primera_entrega_a_telefono(db, telefono_canonico)`.
- Mira `recipient_phone` + `estado == ENTREGADO` -- NO `announced_by_phone`. Decisión explícita del cliente: el criterio es "a este teléfono ya le entregamos algo", no "este teléfono ya anunció algo".
- El teléfono se normaliza (`normalizar_telefono`, ya existe) ANTES de este chequeo -- un formato inválido debe seguir fallando la validación de formato existente antes de intentar resolver "conocido".

### Formulario (`announce/form.html`)

- El campo Nombre deja de estar siempre visible/`required` en el HTML -- pasa a un condicional server-side (variable de contexto nueva, ej. `mostrar_nombre`) que la ruta le pasa a la plantilla.
- Carga inicial (`GET /anunciar`): `mostrar_nombre=False` -- el cliente ve solo Teléfono + Términos y Condiciones.
- Re-render tras un POST donde el teléfono NO es "conocido" y Nombre vino vacío: `mostrar_nombre=True`, con el mismo mecanismo de error ya existente (`_error(mensaje, campo="nombre")`) ancorado al campo Nombre, y Teléfono/aceptación de Términos preservados (mismo patrón `valores` que ya existe hoy).

### Ruta (`announce.py::announce_submit`)

- Reordena la validación: Teléfono (obligatorio + formato válido) y Términos (obligatorio) se validan PRIMERO -- igual que hoy, pero antes que Nombre (antes Nombre se validaba primero).
- Con el teléfono ya normalizado, calcula `conocido`.
- `conocido == False` y Nombre vacío → re-renderiza el formulario con `mostrar_nombre=True` + error en el campo Nombre. No crea ningún Paquete.
- `conocido == True` → continúa sin exigir Nombre, usa `Destinatario.yo_mismo()`.
- `conocido == False` y Nombre SÍ viene → continúa exactamente igual que hoy, `Destinatario.declarado_por_cliente(nombre)`.
- El límite de anuncios activos (`contar_anunciados_activos_de_telefono` / `MAX_ANUNCIADOS_ACTIVOS_POR_TELEFONO` / pantalla `confirmar_multiple`) se evalúa en el mismo punto del flujo que hoy, DESPUÉS de resolver Nombre/conocido -- aplica igual para ambos caminos, sin cambios en su lógica interna.
- Sin pantalla de confirmación de identidad adicional, sin endpoint nuevo, sin JS/AJAX nuevo -- decisión explícita del cliente durante el grilling.
- Sin bandera/columna nueva para distinguir estos anuncios de los del flujo completo -- pedida y luego retirada explícitamente del alcance por el cliente.

## Testing Decisions

Un buen test acá verifica comportamiento observable por HTTP -- qué campos aparecen en el formulario devuelto, qué Paquete queda anunciado y con qué `recipient_name` -- no la forma interna de la query. Mismo criterio que el resto de `test_announce.py`.

### Seam único — HTTP vía `TestClient` (extiende `tests/web/test_announce.py`)

- `GET /anunciar` sin nada previo no muestra el campo Nombre -- arranca solo con Teléfono + Términos.
- `POST /anunciar` con un teléfono que YA tiene un paquete `ENTREGADO` histórico, sin Nombre, con Términos aceptados → crea el Paquete `ANUNCIADO` con `recipient_name` igual al nombre YA REGISTRADO de esa Persona.
- `POST /anunciar` con un teléfono SIN ningún paquete `ENTREGADO` histórico, sin Nombre → NO crea ningún Paquete; re-renderiza el formulario CON el campo Nombre visible y el mensaje de error correspondiente.
- Ese mismo teléfono, reenviando ahora CON Nombre → crea el Paquete igual que el flujo actual (comportamiento ya cubierto por tests existentes, sin cambios).
- Un teléfono con solo paquetes `ANUNCIADO`/`RECIBIDO`/`CANCELADO` histórico (nunca `ENTREGADO`) sigue tratándose como NO conocido -- pide Nombre igual que un teléfono totalmente nuevo.
- El límite de 10 anuncios activos y la pantalla `confirmar_multiple` se disparan igual para un teléfono conocido que anuncia sin Nombre (regresión sobre los tests ya existentes de ese límite, ahora también ejercitados por el camino sin Nombre).
- `test_post_sin_nombre_no_crea_paquete` (ya existente) se actualiza: el caso que cubre pasa a ser explícitamente "teléfono NO conocido, sin nombre" (agregar un comentario aclarando por qué el nombre ya no es universalmente obligatorio); se agrega como test nuevo el caso hermano "teléfono SÍ conocido, sin nombre", verificando que SÍ crea el Paquete.
- Teléfono con formato inválido sigue fallando con el mismo mensaje de error de hoy, antes de llegar a evaluar "conocido" (test ya existente, sin cambios esperados en su resultado).

## Out of Scope

- **Bandera/columna para distinguir anuncios hechos por este atajo** de los del flujo completo -- pedida y luego retirada explícitamente por el cliente durante el grilling.
- **Pantalla de confirmación de identidad** ("¿Eres [nombre]?") antes de anunciar con el atajo -- decisión explícita de no agregar fricción.
- **Cualquier cambio a `/announce` (staff) o `announce_new.py`** -- el atajo es exclusivo de la vista pública `/anunciar`.
- **Cambiar o relajar el límite de 10 anuncios activos por teléfono** -- sigue exactamente igual, para ambos caminos.
- **Detección "en vivo" mientras se escribe el teléfono** (JS/AJAX, endpoint de chequeo nuevo) -- descartada a favor del mismo patrón Post/Redirect/Get + re-render-con-error que la vista ya usa hoy.

## Further Notes

- El glosario de `CONTEXT.md` define hoy **Anuncio** como "el acto/registro por el que un cliente declara que espera un paquete (nombre + teléfono + a nombre de quién)". Este spec matiza esa definición: el nombre pasa a ser condicional (obligatorio solo si el teléfono no es ya conocido). Vale la pena actualizar esa línea de `CONTEXT.md` en la misma rebanada de implementación, no como afterthought.
- `Destinatario.declarado_por_cliente(nombre)` con `nombre=None` YA se comporta, por una cadena de fallbacks existente (`_resolver_ocupante_por_nombre` nunca matchea con `nombre_declarado=None`), igual que `Destinatario.yo_mismo()` -- pero la decisión de implementación es usar `yo_mismo()` explícitamente para el camino "conocido", para no depender de esa coincidencia como si fuera parte del contrato.
- Riesgo aceptado explícitamente por el cliente: alguien que conozca el teléfono de un cliente conocido puede anunciarle un paquete sin su consentimiento, disparando una notificación real a esa persona. Se decidió no mitigar esto con una pantalla extra -- el tope de 10 anuncios activos por teléfono ya acota el daño posible, y el flujo actual (sin el atajo) ya tiene un riesgo equivalente (con más fricción: hoy hace falta además escribir *algún* nombre).

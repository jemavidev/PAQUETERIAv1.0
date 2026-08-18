# 124 — `/consultar`: botón "Entregar" visible solo para staff

**Pedido original (cliente):**
"en la vista de '/consultar?q=' necesito agregar un boton para poder
entregar paquetes desde esta vista, pero solo sera visible para el
personal de staff, como crees que puedes hacerlo y donde lo vas a
incluir."

**Ampliación (cliente, tras ver el botón funcionando):** "lo que veo es
que el flujo de entregar debia permitir de forma opcional el reescaneo
de un numero de guia a ver si corresponde con el que se escaneo
inicialmente" -- portar también el paso "Confirmar guía" (escaneo ZXing
+ comparación visual contra la guía registrada al Recibir) que ya tenía
el modal "Entregar" de `/paquetes`, que la primera versión de este issue
había dejado fuera de alcance a propósito.

**2da ampliación (cliente, tras probar la guía):** "no veo que se
realice ningun tipo de validacion" -- 3 situaciones esperadas: (1) sin
guía → entrega normal; (2) guía tecleada coincide con la registrada; (3)
guía tecleada NO coincide. Bug real encontrado: la comparación (`✅`/`⚠️`)
solo se disparaba dentro del callback del escaneo por CÁMARA -- tecleando
la guía a mano (ambas veces el cliente probó así) nunca se comparaba
nada, aunque `data-guia-esperada` ya tuviera el valor correcto. Este bug
existía TAMBIÉN en `/paquetes` desde antes de este issue (mismo macro
compartido) -- no era exclusivo de `/consultar`.

**Status:** implementado

## Diseño acordado

`/consultar` es una vista pública sin sesión (`search.py`) -- el botón se
resuelve enteramente por template, sin tocar la ruta:
`search/form.html` extiende `base.html`, donde `SESSION_KEY` ya es un
global de Jinja (`templating.py`), así que `{% if
request.session.get(SESSION_KEY) %}` alcanza para mostrarlo solo a staff
logueado, igual que ya hace `base.html` para su propio nav. El endpoint
que muta (`POST /paquetes/{id}/entregar`) sigue protegido por `Depends
(current_staff)` como siempre -- la visibilidad del botón es cosmética,
la autorización real no cambia.

## Implementación

- `packages.py`, `deliver_action`: nuevos `Form` opcionales `origen` y
  `q`. Si `origen == "consultar"`, redirige (éxito y error) a
  `/consultar?q=<q>` en vez de `/paquetes`. Sin `origen`, comportamiento
  intacto (compatibilidad total con `/paquetes`).
- `search/form.html`: botón "Entregar" + modal de confirmación (mismo
  componente `modal(...)` que ya usa `/paquetes`), visible solo si
  `request.session.get(SESSION_KEY)` **y**
  `paquete.estado.value == 'RECIBIDO'` (única precondición real de
  `deliver()`). Form oculto con `origen=consultar` y `q=<termino
  buscado>` para el redirect de vuelta.
- Reescaneo de guía (ampliación): el JS de escaneo ZXing + comparación
  (`.scan-btn`, `.guia-check-msg`) en realidad vive en el macro
  COMPARTIDO `recursos_recibir()` (`components/_recibir_paquete.html`),
  no en `list.html` como se asumió al principio -- delegado sobre
  `document`, seguro de incluir en cualquier página. `search/form.html`
  ahora importa `recursos_recibir` (reemplaza el script de toggle
  hecho a mano) y el modal "Entregar" agrega, solo si
  `paquete.guide_number` existe, el mismo bloque de
  input+data-guia-esperada+botón de cámara+video+mensajes que ya usa
  `/paquetes`. El input NO tiene `name` (igual que en `/paquetes`): es
  puramente una verificación visual del staff, nunca viaja al servidor
  ni bloquea la entrega.

## Verificación

- `tests/web/test_search.py`: botón ausente sin sesión de staff, ausente
  si el paquete no está en RECIBIDO, presente y funcional si hay sesión
  de staff + estado RECIBIDO; POST exitoso redirige a
  `/consultar?q=<termino>` (no a `/paquetes`).
- `tests/web/test_packages.py`: `deliver_action` sigue redirigiendo a
  `/paquetes` cuando no se manda `origen` (regresión, test existente sin
  cambios sigue pasando).
- Playwright contra el servidor local real (`localhost:8010`): sin
  sesión el botón no aparece; con sesión de staff aparece solo si el
  paquete está en RECIBIDO; clic abre el mismo modal "Entregar paquete"
  que usa `/paquetes`; confirmar deja al staff en `/consultar?q=<código>`
  con el badge y el timeline ya en "Entregado".
- Playwright (ampliación): con guía registrada, "Confirmar guía" +
  botón "📷 Escanear con cámara" aparecen dentro del modal; sin guía,
  no aparece nada de esa sección.
- `components/_recibir_paquete.html`, `recursos_recibir()`: la
  comparación se extrae a `compararGuia(input)` y se dispara desde DOS
  lugares -- el callback de escaneo (como antes) y un listener `input`
  delegado sobre `[data-guia-esperada]` (nuevo, cubre tecleo manual).
  Vacío → mensaje oculto; coincide → "✅ Coincide con la guía
  registrada."; no coincide → "⚠️ Guía distinta a la registrada (X).
  Puedes entregar igual si estás seguro." Sigue sin bloquear el submit
  a propósito (decisión ya tomada en Grupo 14/Ronda 2 -- una guía
  dañada/mal impresa no debe trabar la entrega física real). Al ser un
  macro compartido, el fix aplica a la vez a `/paquetes` y `/consultar`.
- Playwright (2da ampliación): tecleando la guía a mano en
  `/consultar` -- vacío sin mensaje, coincide con check verde, no
  coincide con aviso ámbar, y vuelve a vacío sin mensaje.

**3ra ampliación (cliente):** "la idea es que en los mensaje que
aparezcan no se muetre la guia en caso que no coincida, para reforzar
que si sea la guia correcta o en su defecto que solo la dejen en blanco
si no quiren validar" -- el mensaje de no-coincidencia mostraba la guía
real registrada entre paréntesis, lo que le quitaba sentido al check
(cualquiera podía "corregir" lo tecleado copiando el valor que el
mensaje ya revelaba). `compararGuia` ya no interpola `esperada` en el
texto de error. Ajuste posterior (mismo pedido, "más corto y conciso"):
el mensaje completo queda solo "⚠️ Guía distinta a la registrada." (se
quita "Puedes entregar igual si estás seguro." -- el comportamiento de
no bloquear sigue igual, solo ya no hace falta decirlo). Quien no
quiera validar, deja el campo en blanco (sigue sin ser obligatorio).

- Playwright (3ra ampliación): con una guía que no coincide, el mensaje
  ya no contiene la guía real registrada.
**4ta ampliación (cliente):** acortar el mensaje de no-coincidencia a
solo "⚠️ Guía distinta a la registrada." (se quita "Puedes entregar
igual si estás seguro." -- el comportamiento de no bloquear sigue
igual, solo ya no hace falta decirlo).

- Bug propio encontrado al correr la suite completa tras la 3ra
  ampliación: el comentario del código en `compararGuia` citaba
  textualmente la frase de advertencia de nombre ("no coincide") --
  como `recursos_recibir()` se incluye también en `/paquetes`, ese
  comentario quedaba en el HTML servido y rompía en falso 3 tests que
  verifican por substring que esa advertencia está apagada
  (`test_advertencia_no_aparece_cuando_el_nombre_coincide` y 2 más).
  Corregido reescribiendo el comentario sin citar la frase literal;
  los 3 tests vuelven a pasar.
- Suite completa (tras todos los ajustes de este issue): 1010 passed.
- Pendiente: deploy a test.papyrus.com.co.

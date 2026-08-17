# 92 — `clasificar_contacto` acepta `+57` (y cualquier país) además del celular colombiano pelado

**Pedido original (cliente):**
Tras analizar `/announce` a pedido del cliente ("analiza esta vista y su
formulario /announce"), se encontró que el campo único de esa vista (y el
campo "contacto" de residente nuevo en `/paquetes`, `/residentes` y la
verificación OTP de cliente) no reconocía el formato `"+57300..."` — solo
el celular colombiano pelado de 10 dígitos. El cliente confirmó el arreglo
y preguntó explícitamente cómo se manejarían otros países más allá de
Colombia: "Sí, ajústalo para que acepte +57 también. Ten presente que +57
es colombia, pero existen mas paises, ejemplo (+1, +58, +34,...) USA,
Venezuela, España... entre otros muchos paises, como manejaras esto."

**Status:** verificado

## Implementación

- `domain/contacto.py`, `clasificar_contacto`: en vez de reimplementar su
  propia regla de "qué es un teléfono" (que solo reconocía "empieza en 3,
  10 dígitos exactos"), ahora delega en `telefono.normalizar_telefono` —
  la ÚNICA fuente de verdad para esa regla en todo el sistema, usada al
  persistir. Esa función YA tenía la regla correcta: sin `+`, solo celular
  colombiano (10 dígitos empezando en 3, o el equivalente con indicativo
  "57" sin `+`); con `+`, cualquier número de 10 a 15 dígitos (rango
  E.164) se acepta tal cual, **sin necesitar una lista de indicativos por
  país** — así "+13002596319" (EE.UU.), "+584121234567" (Venezuela) o
  "+34612345678" (España) clasifican como teléfono exactamente igual que
  "+573001234567" (Colombia), sin que `contacto.py` tenga que saber que
  esos países existen.
- Efecto colateral correcto (no un cambio de alcance): también empieza a
  reconocer el celular colombiano con indicativo SIN `+` ("573001234567")
  y con espacios/guiones ("300 123 4567"), porque `normalizar_telefono` ya
  los aceptaba — antes `clasificar_contacto` exigía `valor.isdigit()`
  estricto, más angosto que la regla real de persistencia.
- Se preserva la garantía "exige el valor completo, no a medio teclear"
  (`+57300` a medio teclear sigue devolviendo `"ninguno"`) gratis, porque
  `normalizar_telefono` ya lanza `ValueError` para cualquier cantidad de
  dígitos que no calce.
- Al ser la única fuente de verdad (`clasificar_contacto` se usa en
  `announce_new.py`, `packages.py`, `customers_manage.py` y
  `customer_verify.py`), el arreglo cubre los 4 puntos con un solo cambio.

## Verificación

- `tests/data_model/test_clasificar_contacto.py`: casos nuevos para
  Colombia con `+`/sin `+`, EE.UU., Venezuela, España, y casos de "a medio
  teclear"/fuera de rango E.164 que deben seguir siendo `"ninguno"` — 24
  tests, todos pasan (los 15 preexistentes sin cambios de resultado).
- Playwright contra el servidor local real: tecleado `"+573101110001"` en
  el campo único de `/announce` — antes del fix no devolvía nada; después
  del fix resuelve correctamente la unidad TORRE 3 · Apto 302 con sus 5
  residentes.
- Suite completa: ver commit para el conteo final.
- Desplegado a test.papyrus.com.co (2026-08-17), confirmado en el contenedor real (`docker exec paquetex-app-1`).

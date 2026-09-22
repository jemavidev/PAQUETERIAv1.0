Status: ready-for-agent
Feature: captura-guia-lector-camara
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con Jesús (conversación del 2026-09-21, decisiones D1–D10 en
`.scratch/captura-guia-lector-camara/decisiones-grilling.md`) · investigación contra fuentes primarias en
`.scratch/captura-guia-lector-camara/investigacion-oficial.md` (Farset F7, cámara en navegador móvil, guías
colombianas) · análisis de comportamiento del modal Recibir hecho y verificado en navegador el mismo día ·
CONTEXT.md (glosario: Guía, Staff, Recibir, Entregar) · `.scratch/packages-staff/issues/04-recibir-escaner-zxing-camara.md`
(escáner de cámara original) · `.scratch/doble-escaneo-guia-entregar/spec.md` ("Confirmar guía" de Entregar) ·
`.scratch/announce-rapido/issues/06-recibir-desde-announce.md` (Recibir reusado desde /announce) · issue 284
(`.scratch/pendientes-cliente`, autofocus retirado de vistas de Staff)

---

## Problem Statement

El Staff (Operador o Admin) captura la **Guía** del transportador al **Recibir** un paquete: teclea el número o lo lee
del código de barras de la etiqueta. Hoy, en la vida real, el conjunto trabaja con dos tipos de dispositivo: celulares
normales, que solo tienen la cámara, y equipos **Farset F7**, handhelds Android con un lector de códigos de barras
dedicado (Honeywell N6603) integrado. La captura de la Guía tiene que funcionar bien en los dos, y hoy no lo hace:

- **Un lector que actúa como teclado y manda un Enter al final recibe el paquete al instante.** El campo Guía vive
  dentro del formulario de Recibir, así que ese Enter lo envía: el paquete queda Recibido con Tipo Normal y Condición
  Buena por defecto, sin fotos, sin elegir a qué Residente corresponde y sin registrar un posible pago contra entrega.
  Una lectura equivocada o de otro código recibe un paquete a ciegas.
- **La lectura se pierde si el Operador no toca antes el campo.** Al abrir el modal Recibir, el foco queda en el botón
  de la fila que lo abrió, detrás del modal, no en el campo Guía. Un lector que escribe en el campo enfocado no tiene
  dónde escribir, y no avisa nada.
- **El F7 de fábrica no escribe en ninguna página web.** Su servicio de escaneo viene en modo de envío `BROADCAST`
  (según el documento del fabricante publicado en su listado), que una página en Chrome no puede recibir. Hay que
  cambiarlo por equipo a un modo que escriba en el campo enfocado.
- **La cámara falla en silencio.** Si el permiso se niega o no hay cámara, queda un cuadro de video negro visible, sin
  mensaje y con un error de consola. Si el script del lector no carga, el botón no hace nada. Un doble clic en
  "Escanear" abre dos flujos de cámara y al cerrar el modal solo se libera uno: la cámara queda encendida hasta recargar.
  Sin restricciones de resolución, Chrome entrega 640x480, una entrada pobre para códigos lineales, y el bucle de
  lectura reintenta sin pausa mientras no hay código a la vista.
- **Un código largo rompe la recepción.** La Guía admite 50 caracteres en la base de datos y ninguna validación lo
  revisa: un QR con una URL, leído por la cámara o inyectado por el lector, termina en un error 500 sin explicación.
- **Una guía repetida rompe la consulta pública.** No hay unicidad ni aviso (correcto por diseño: en el glosario la Guía
  es una referencia, no una llave, y un envío de varias cajas comparte guía), pero la búsqueda pública por guía
  asume "cero o un paquete" y con dos paquetes de la misma guía falla con un error 500.

## Solution

La captura de la Guía funciona igual de bien desde un celular con la cámara y desde un F7 con su lector, con una regla
simple para el Operador: **leer solo escribe la guía; recibir siempre lo confirma el Operador con el botón "Recibir"**.

- Una lectura (cámara o lector) únicamente llena el campo Guía. Un Enter o Tab que el lector mande al final nunca envía
  el formulario.
- Cada F7 se marca una sola vez, desde el menú de cuenta, con un interruptor **"Este equipo tiene lector"**. Con el
  interruptor activo, al abrir Recibir (y "Confirmar guía" de Entregar, si el paquete tiene guía) el foco va al campo
  correcto sin teclado en pantalla, y basta apretar el gatillo. Apagado por defecto: celulares normales no cambian nada.
- La cámara de los celulares deja de fallar en silencio: mensajes claros, un solo flujo de cámara, botón para detener,
  mejor resolución y linterna cuando el celular la ofrece.
- Una guía de más de 50 caracteres se rechaza con un mensaje claro, nunca se corta en silencio y nunca produce un 500.
- Una guía que ya existe en otro paquete se acepta con un aviso que no bloquea, y la consulta pública deja de romperse:
  el Staff ve la lista de coincidencias y el público, un mensaje neutro.

## User Stories

**Celular normal, captura con la cámara**

1. Como Operador con un celular, quiero tocar "Escanear con cámara" y apuntar a la etiqueta, para que la guía se escriba
   sola en el campo Guía sin teclearla.
2. Como Operador, quiero que la cámara trasera sea la que se abra, para apuntar a la etiqueta sin girar el celular.
3. Como Operador, quiero que la cámara pida una resolución mayor a la mínima, para que los códigos de barras lineales
   pequeños o algo lejanos se lean a la primera.
4. Como Operador en un lugar con poca luz, quiero un botón de linterna cuando mi celular la ofrezca, para leer etiquetas
   en un depósito oscuro.
5. Como Operador cuyo celular no tiene linterna, quiero que ese botón no aparezca, para no ver un control que no hace
   nada.
6. Como Operador, quiero ver en el campo exactamente lo que leyó la cámara, para revisarlo o corregirlo antes de recibir.
7. Como Operador, quiero que la cámara lea cualquier tipo de código de la etiqueta (lineales, QR y otros 2D), para no
   quedar bloqueado con una etiqueta que solo trae un QR.
8. Como Operador, quiero que al leer un código el video se oculte y la cámara se apague sola, para no gastar batería ni
   dejar la cámara encendida.
9. Como Operador, quiero un botón para detener la cámara sin haber leído nada, para cancelar el escaneo y teclear la guía
   a mano.
10. Como Operador, quiero que cerrar el modal (con la X, tocando el fondo o con Escape) apague la cámara, para no dejarla
    encendida detrás del modal.
11. Como Operador, quiero que el botón "Escanear" quede deshabilitado mientras la cámara está abierta, para no abrir dos
    flujos de cámara por un doble toque.
12. Como Operador que niega el permiso de cámara, quiero ver un mensaje claro que me lo diga, para saber por qué no
    funciona y poder teclear la guía.
13. Como Operador cuyo celular no tiene cámara utilizable, quiero un mensaje claro, para no ver un cuadro negro sin
    explicación.
14. Como Operador que abre la página sin HTTPS, quiero seguir viendo el mensaje "Cámara no disponible; escribe la guía a
    mano", para saber que debo teclearla.
15. Como Operador con mala conexión, quiero un mensaje cuando el lector de códigos no logra cargarse, para no quedarme
    tocando un botón que no responde.
16. Como Operador, quiero que después de cualquiera de esos fallos el campo Guía siga editable, para no quedar bloqueado
    nunca.
17. Como Operador, quiero que la cámara gaste menos batería mientras busca un código, para poder trabajar un turno
    completo con el mismo celular.
18. Como Operador con un iPhone, quiero que el escaneo con cámara siga funcionando como hoy, para no depender de un
    equipo Android.

**Equipo Farset F7, captura con el lector integrado**

19. Como Operador con un F7, quiero activar una sola vez el interruptor "Este equipo tiene lector" desde el menú de
    cuenta, para que ese equipo quede preparado sin configurar nada más en la web.
20. Como Operador con un F7, quiero que el interruptor recuerde su estado en ese equipo, para no reactivarlo en cada
    sesión.
21. Como Operador con un F7, quiero ver en el menú de cuenta si el modo lector está activado o desactivado, para saber en
    qué estado está el equipo.
22. Como Operador con un F7, quiero poder desactivar el modo lector en cualquier momento, para volver al comportamiento
    de un celular normal.
23. Como Operador con un celular normal, quiero que el modo lector esté apagado por defecto y no me afecte, para que mis
    modales se comporten como hoy.
24. Como Operador con un F7 y el modo lector activo, quiero que al abrir Recibir el foco vaya al campo Guía, para apretar
    el gatillo y que la guía aparezca sin tocar nada.
25. Como Operador con un F7, quiero que al enfocar el campo Guía no aparezca el teclado en pantalla, para que no tape
    el modal justo cuando voy a leer.
26. Como Operador con un F7, quiero que al tocar yo mismo el campo Guía sí aparezca el teclado normal, para poder teclear
    una guía que el lector no logra leer.
27. Como Operador con un F7, quiero que leer una segunda vez reemplace la guía anterior en vez de sumarse a ella, para no
    terminar con dos guías pegadas por un doble disparo.
28. Como Operador con un F7, quiero que un Enter que mande el lector al final no reciba el paquete, para no recibir un
    paquete a ciegas con los valores por defecto.
29. Como Operador con un F7, quiero que un Tab que mande el lector al final no rompa el flujo, para que el campo quede
    lleno y yo confirme con "Recibir".
30. Como Operador con un F7, quiero seguir teniendo el botón "Escanear con cámara" disponible, para usar la cámara de 13
    MP cuando el lector no pueda leer una etiqueta dañada.
31. Como Operador con un F7, quiero que al abrir Entregar en un paquete con guía el foco vaya a "Confirmar guía", para
    verificar el paquete leyendo su etiqueta sin tocar nada.
32. Como Operador con un F7, quiero que si el paquete no tiene guía Entregar no enfoque ningún campo extra, para no
    estorbar el resto del flujo de cobro.
33. Como Operador con un F7, quiero seguir viendo el aviso ✅ o ⚠️ al confirmar la guía en Entregar, para saber si es el
    paquete correcto.
34. Como Operador que activó el modo lector en un F7, quiero que ese ajuste no afecte al celular de otro Operador, para
    que cada equipo se configure por separado.

**Validación del largo de la guía**

35. Como Operador, quiero que una lectura de la cámara de más de 50 caracteres no se escriba y me muestre cuántos
    caracteres tiene y cuál es el máximo, para saber que ese código no es la guía y probar con otro de la etiqueta.
36. Como Operador con un F7, quiero que una lectura del lector de más de 50 caracteres marque el campo con un error visible
    con el largo actual, para saber que hay algo mal en lo que se escribió.
37. Como Operador, quiero que mientras la guía tenga más de 50 caracteres el botón "Recibir" no deje enviar, para no
    provocar un error del servidor.
38. Como Operador, quiero que al corregir la guía el error desaparezca y pueda recibir normalmente, para no quedarme
    atascado.
39. Como Operador, quiero que la guía nunca se corte en silencio, para no registrar un número que no es el de la etiqueta.
40. Como Operador, quiero que si de todas formas llega al servidor una guía de más de 50 caracteres reciba el mismo
    mensaje dentro del modal Recibir, para no ver una pantalla de error genérica.
41. Como Operador, quiero que ese rechazo del servidor no deje el paquete a medias, para que siga Anunciado y pueda
    reintentar.

**Guías repetidas**

42. Como Operador, quiero que un paquete de varias cajas con la misma guía se pueda recibir completo, para no quedar
    bloqueado con un envío legítimo.
43. Como Operador, quiero ver un aviso "Ya hay N paquete(s) con esta guía" cuando la guía que leí o escribí ya existe, para
    distinguir un error de lectura de un envío de varias cajas.
44. Como Operador, quiero que el aviso indique en qué estado están esos otros paquetes, para juzgar si se trata del mismo
    envío o de una lectura repetida por error.
45. Como Operador, quiero que ese aviso nunca bloquee el botón "Recibir", para no trabar una recepción física real.
46. Como Operador, quiero que el aviso no muestre nombres ni datos de otros destinatarios, para no ver información de
    Residentes ajenos.
47. Como Operador, quiero que si dejo la guía vacía no aparezca ningún aviso, para no ver ruido cuando no la uso.
48. Como Operador, quiero que el aviso compare la guía tal como se guardaría (mayúsculas, espacios normalizados), para que
    "abc 123" y "ABC 123" cuenten como la misma.
49. Como Operador, quiero que el aviso no cuente el propio paquete que estoy recibiendo, para no advertirme de mí mismo.

**Consulta por guía**

50. Como Residente o visitante, quiero que consultar una guía que pertenece a un solo paquete funcione exactamente como
    hoy, para no notar ningún cambio.
51. Como Staff con sesión iniciada, quiero que al consultar una guía que coincide con varios paquetes se me muestre la
    lista de coincidencias (código de acceso, destinatario y estado), para elegir el que necesito.
52. Como Staff, quiero abrir cualquiera de esos paquetes desde la lista y ver el mismo detalle y acciones que hoy, para no
    perder ninguna función.
53. Como Residente o visitante sin sesión, quiero un mensaje neutro cuando la guía corresponde a más de un paquete, que me
    pida consultar con el código de acceso de cada uno, para que una coincidencia por error no muestre el paquete de otra
    persona.
54. Como visitante sin sesión, quiero que ese mensaje no revele datos de ningún paquete, para proteger la privacidad de los
    Residentes.
55. Como Staff o visitante, quiero que ninguna consulta por guía termine en error 500, para no ver una pantalla rota.
56. Como Residente, quiero que consultar por código de acceso siga funcionando igual (es único), para no depender de la guía.

**Reutilización en otras pantallas**

57. Como Staff en /announce que presiona "Recibir", quiero el mismo campo Guía, la misma guardia del Enter, el mismo modo
    lector y los mismos avisos, para no aprender un comportamiento distinto.
58. Como Staff que recibe desde /consultar, quiero el mismo comportamiento que en /paquetes, para que Recibir sea
    consistente en todas las pantallas.
59. Como Staff en /consultar o /paquetes, quiero que los arreglos de la cámara (mensajes, un solo flujo, botón detener)
    también apliquen a "Confirmar guía", para que la cámara se comporte igual en Recibir y en Entregar.

**Documentación y despliegue**

60. Como Operador nuevo, quiero una sección corta en el manual del Operador sobre cómo capturar la guía con la cámara y con
    el lector, para aprender el flujo sin preguntar.
61. Como Admin o encargado de los equipos, quiero instrucciones para configurar un F7 (modo de envío que escribe en el
    campo enfocado, terminador y el interruptor del menú de cuenta), para dejar cada equipo listo.
62. Como Admin, quiero que quede escrito que el F7 viene de fábrica en un modo que no escribe en la web, para no pensar que
    la aplicación está rota cuando un equipo nuevo no captura nada.

**Calidad y validación**

63. Como desarrollador, quiero pruebas automáticas HTTP para lo que decide el servidor y una prueba en navegador real para
    el Enter, el foco y la cámara, para que estos comportamientos no dependan de una verificación manual.
64. Como Jesús, quiero un protocolo de prueba de campo para el F7 y los celulares reales, para confirmar lo que ninguna
    prueba automática puede: que el lector escribe en un campo de Chrome, que el gatillo funciona con un formulario web y
    cómo lee la cámara etiquetas reales.
65. Como Jesús, quiero que lo específico del F7 quede aislado y pequeño, para poder ajustarlo tras la prueba de campo sin
    rehacer el resto.

## Implementation Decisions

**Regla de lectura.** Una lectura, sea de la cámara o del lector, solo escribe la Guía en el campo. Ningún camino de esta
feature recibe un paquete por sí solo. Cambiar esto exigiría reabrir esta decisión, no un ajuste de configuración.

**Guardia del Enter en el modal Recibir.** El Enter (o el Tab) que llega al campo Guía no envía el formulario. La guardia
opera en dos niveles: al detectar la tecla dentro del campo y también al enviar el formulario, por si el lector inyecta su
terminador de una forma que no dispara la tecla. El botón "Recibir" pulsado por el Operador sigue enviando normalmente. La
guardia aplica solo al campo Guía de Recibir: el campo "Confirmar guía" de Entregar y de /consultar está fuera del
formulario que entrega el paquete, así que un Enter allí no envía nada y no necesita cambios.

**Modo lector (interruptor por equipo).**
- Es una preferencia del equipo/navegador, guardada localmente (no en la base de datos ni ligada al Usuario staff), apagada
  por defecto. Cada F7 se activa una sola vez.
- Vive como un ítem con estado (activado/desactivado) en el menú de cuenta del encabezado, junto a los demás ítems de ese
  menú. No agrega nada al modal Recibir.
- Con el modo activo, al abrir el modal Recibir el foco se coloca en el campo Guía; al abrir Entregar en un paquete que
  tiene guía, el foco se coloca en "Confirmar guía". Si el paquete no tiene guía, Entregar no enfoca nada.
- El campo enfocado por esta vía no muestra el teclado en pantalla; si el Operador lo toca, el teclado normal aparece para
  teclear a mano.
- Al recibir el foco en modo lector, el contenido existente del campo queda seleccionado, de modo que una nueva lectura lo
  reemplaza en vez de anexarse (el modo de envío del F7 que solo escribe en el campo enfocado anexa sobre lo existente).
- Con el modo apagado no se enfoca nada por código: se respeta el pedido del issue 284 de no forzar foco en vistas de
  Staff.

**Cámara (celulares y F7).**
- Se mantiene el motor de lectura y la versión actuales; no se cambia de librería ni de versión.
- Se pide una resolución ideal de 1280x720 (ideal, no exacta, para no fallar en cámaras que no la dan) en vez de la
  resolución por defecto del navegador; se conserva la cámara trasera por defecto.
- Se ofrece un botón de linterna solo cuando la cámara activa reporta esa capacidad; nunca se asume.
- Se espacian los reintentos de decodificación mientras no hay código a la vista, para reducir CPU y batería.
- No se restringen los formatos: se aceptan todos los que el lector soporta hoy (lineales, QR, DataMatrix, Aztec, PDF417).
  El campo siempre muestra lo leído para que el Operador lo revise.
- Mensajes visibles, reutilizando el elemento de mensaje que ya existe junto al botón, para cada fallo: sin soporte de
  cámara o contexto inseguro (texto existente), permiso negado, sin dispositivo, error al iniciar y el lector de códigos que
  no carga. En todos los casos el video se oculta y el campo queda editable.
- Ciclo de vida: mientras hay un escaneo en curso el botón "Escanear" queda deshabilitado (no se permiten dos flujos en el
  mismo campo); hay un botón para detener; cerrar el modal por cualquier vía, incluida la tecla Escape, apaga la cámara y
  libera todos los flujos, incluidos los abiertos por un doble toque.
- Todo este comportamiento vive en el bloque de comportamiento compartido del navegador que ya incluyen las páginas con Recibir
  y Entregar, así que llega por igual a Recibir (en /paquetes, /announce y /consultar) y a "Confirmar guía" de Entregar (en
  /paquetes y /consultar). No se duplica por página.

**Largo de la guía (máximo 50 caracteres, sin cambios de esquema).**
- No se agrega un tope de longitud al campo, a propósito: cortaría en silencio lo que inyecta el F7.
- En el navegador, lectura por cámara: si el texto leído supera 50 caracteres no se escribe y se muestra un mensaje con el largo
  leído y el máximo.
- En el navegador, lector o teclado: si el valor del campo supera 50 caracteres el campo marca un error visible con el largo actual
  y el envío de "Recibir" queda bloqueado hasta corregirlo (validación nativa del formulario).
- Servidor: Recibir valida el largo de la Guía ya normalizada (la misma normalización con la que se guarda) y, si supera 50,
  responde con el mecanismo de error de modal que Recibir ya usa (reabre el modal Recibir del paquete con el mensaje), con
  estado 400, sin cambiar el estado del Paquete ni persistir nada. La validación ocurre antes de cualquier efecto.
- Nunca se trunca. Sin migración: la columna sigue siendo de 50 caracteres.

**Aviso de guía repetida.**
- Un servicio de consulta solo para Staff recibe una guía y devuelve cuántos paquetes la tienen y en qué estado (todos los
  estados), sin ningún dato del destinatario ni identificador que permita ver esos paquetes. Puede recibir el paquete
  actual para no contarlo.
- La comparación normaliza la guía igual que al guardar (mayúsculas, espacios colapsados, recortada), para que la
  coincidencia sea la misma que vería la base de datos.
- El navegador lo consulta al terminar de leer o escribir (con una pausa breve para no consultar cada tecla) y muestra el
  aviso junto al campo. Con la guía vacía no consulta ni avisa.
- El aviso es solo informativo: no bloquea el envío, no se persiste, no cambia la política de la base de datos (sigue sin
  unicidad; en el glosario la Guía es una referencia, no una llave de emparejamiento).

**Consulta pública por guía.**
- La búsqueda por término (código de acceso o guía) pasa de "cero o uno" a "cero, uno o varios". Un solo paquete: exactamente
  el comportamiento actual, incluidas las acciones de Staff sobre él. Ninguno: igual que hoy.
- Varios paquetes con esa guía: con sesión de Staff, se muestra una lista de coincidencias (código de acceso, destinatario y
  estado) y cada fila lleva al detalle habitual; sin sesión, un mensaje neutro que indica que la guía corresponde a más de un
  paquete y pide consultar con el código de acceso de cada uno, sin mostrar ningún dato.
- El código de acceso es único y sigue siendo una consulta directa; ninguna combinación de coincidencias produce un error 500.

**Coherencia con el resto del sistema.**
- El comportamiento del campo Guía de Recibir se hereda en /announce y en el Recibir de /consultar, que ya reutilizan el mismo
  componente de modal; no se reimplementa.
- Se actualiza el manual del Operador con una sección de captura de guía (cámara, lector, interruptor y cómo configurar el
  F7).
- No hay cambios de modelo de datos ni migraciones. No hay conflicto con los ADR existentes: la Guía sigue siendo una
  referencia opcional, no una llave (ver glosario).

**Configuración del F7 (fuera del código).** El modo de envío de cada F7 se cambia en la aplicación de escáner del propio
equipo, no desde la web. De fábrica, según el documento del fabricante, está en un modo que no escribe en páginas web; hay que
ponerlo en el modo que escribe en el campo enfocado sobrescribiendo el contenido, con terminador Ninguno (Enter y Tab también
se toleran por la regla de lectura). La feature no configura ni administra los equipos.

**Riesgo aceptado.** Jesús decidió entregar todo junto y probar el F7 al final, en lugar de dos entregas. Por eso lo
específico del F7 (interruptor, foco, teclado, selección) se mantiene pequeño, aislado y sin dependencias del resto, para
ajustarlo tras la prueba de campo sin tocar la cámara ni las validaciones.

## Testing Decisions

**Qué es un buen test aquí.** Prueba solo comportamiento externo: lo que el Operador ve y puede hacer, y lo que el servidor
responde y persiste. No prueba nombres de funciones internas del navegador, la estructura del bloque compartido ni la
librería de lectura. Un test del navegador debe fallar si el Operador ya no puede completar la acción, no si se renombra
una función.

**Puntos de prueba (seams), confirmados con Jesús.** Dos, no más:

1. **HTTP sobre el servidor (existente, el más alto para lo que decide el servidor).** Pruebas con `TestClient` sobre el
   Postgres efímero de la suite de la capa web. Cubren: Recibir con una guía de más de 50 caracteres (error de modal 400, el
   Paquete sigue Anunciado, nada se persiste, sin 500) y con guía normal, vacía y con mayúsculas/espacios a normalizar; el
   servicio de aviso de guía repetida (Staff sí, anónimo no; cantidad y estados; normalización; excluye el paquete actual;
   guía vacía; ningún dato personal en la respuesta); la consulta por guía con cero, uno y varios paquetes (Staff ve la
   lista, el público ve el mensaje neutro y ninguno de los dos recibe un 500; código de acceso sin cambios); y el contrato
   del HTML renderizado que el navegador necesita (campo Guía de Recibir con sus ganchos, el interruptor en el menú de cuenta
   solo para Staff, "Confirmar guía" de Entregar solo cuando el paquete tiene guía, y que esto llegue a /announce y a
   /consultar).
2. **Navegador real (nuevo, único).** Chromium real con Playwright contra la aplicación levantada sobre ese mismo Postgres
   efímero, con teclado sintético (eventos de teclado confiables) y cámara simulada (un flujo de video tomado de un lienzo
   donde se dibuja un QR, generado con el propio lector). Corre aparte, identificado por un marcador, y no forma parte de
   la suite por defecto (necesita Chromium instalado); se salta si no está disponible. Cubre lo que solo existe en un
   navegador real: un Enter después de tecleado rápido no envía el formulario y el botón "Recibir" sí; el interruptor del
   menú de cuenta mueve el foco al abrir Recibir y Entregar sin teclado en pantalla y respeta el apagado por defecto; una
   segunda lectura reemplaza a la primera; una lectura de cámara llena el campo, oculta el video y apaga el flujo; una
   lectura de más de 50 no se escribe y avisa; un rechazo de la cámara muestra el mensaje y oculta el video; un doble clic
   deja un único flujo vivo; cerrar con la X, el fondo o Escape apaga todos los flujos; y el aviso de repetida aparece sin
   bloquear el envío.

**Prior art.**
- Seam 1: las pruebas de la capa web de paquetes (en especial las que ya verifican que el modal Recibir incluye el disparador
  de escaneo y que el modal Entregar solo incluye "Confirmar guía" cuando hay guía), las de Recibir con campos extra (pago
  contra entrega), las de búsqueda pública (/consultar), el `client` de la capa web y los auxiliares `_login_staff`/
  `_anunciar`, sobre el arnés de Postgres efímero compartido.
- Seam 2: no hay antecedente activo. La carpeta de pruebas end-to-end existente pertenece al monolito anterior (puerto 8000,
  fuera de las rutas de la suite del rebuild) y no es reutilizable tal cual. La técnica sí está probada: durante el análisis
  de esta feature se verificaron en Chromium real con Playwright el Enter que envía el formulario, el foco perdido, el rechazo
  de la cámara sin mensaje, la lectura simulada de un QR y el flujo huérfano tras un doble clic.

**No se prueba automáticamente.** Que el F7 escriba en un campo de Chrome, que su gatillo funcione con un formulario web y la
calidad de lectura de las cámaras y de las etiquetas reales: eso lo cubre el protocolo de prueba de campo (última sección de
la investigación), con al menos un F7, un Android y un iPhone, después de desplegar a `test.papyrus.com.co` cuando Jesús lo
pida.

## Out of Scope

- Cambiar de librería o de versión de lectura (lector nativo del navegador, ZXing 0.23, ZXing en WebAssembly): se reevalúa con
  datos de la prueba de campo.
- Restringir formatos por transportadora, reglas de normalización de códigos largos o de QR, o cualquier lógica específica de
  una transportadora. Tampoco investigar más qué código trae cada etiqueta: no hay fuente primaria.
- Promover la Guía a llave de emparejamiento o exigir unicidad (queda "a futuro" en el glosario), y bloquear guías repetidas.
- Ampliar la columna de 50 caracteres o cualquier migración de base de datos.
- Recibir automáticamente al leer, o cualquier flujo en que un Enter reciba el paquete.
- Detección automática del F7 por el navegador o por ráfagas de teclas, y foco automático general en vistas de Staff (el
  issue 284 se mantiene).
- Una aplicación nativa o envoltorio, receptores de broadcast de Android, Web Serial/WebHID, configuración remota o
  administración de flota de los F7, y cambiar la configuración del F7 desde la web.
- Editar la Guía después de recibir (no existe hoy) y auditar si la guía vino de una lectura o de teclado.
- Corregir la comparación de "Confirmar guía" con espacios internos (detalle menor, hoy compara recortando pero sin colapsar).

## Further Notes

- **Lo que NO se pudo verificar sin el equipo:** si el modo del F7 que escribe en el campo enfocado realmente lo hace en un
  campo de Chrome y con qué mecanismo; si el equipo trae Chrome y Google Play; si el gatillo funciona con un formulario web; y
  el modelo exacto (F7, F7-Pro o F7T). El estado de fábrica del envío (no escribe en la web) sale de un documento del listado
  del fabricante en Amazon que no lleva marca ni modelo y del FAQ del propio fabricante, que habla de otro nombre de modo;
  hay que confirmarlo en el equipo (protocolo de prueba de campo).
- **Decisión de orden:** Jesús eligió entregar todo junto y probar el F7 al final, en contra de la recomendación de dos
  entregas. El riesgo está aceptado y por eso lo del F7 debe quedar aislado.
- **Hallazgos previos que motivan el trabajo, todos verificados el 2026-09-21:** el Enter del lector recibe el paquete; el
  foco no queda en Guía al abrir el modal; el rechazo de la cámara no muestra mensaje; un doble clic deja un flujo vivo tras
  cerrar el modal; una guía de 60 caracteres entra al campo y Postgres la rechaza; la búsqueda pública falla con varias
  coincidencias (comprobado el comportamiento de la consulta "cero o uno" de forma aislada, no de punta a punta).
- **Coincidencia mixta en /consultar (no decidido en el grilling):** si el mismo término coincidiera con el código de acceso de
  un paquete y con la guía de otro, se propone que el código de acceso, que es único, tenga prioridad.
- **Aviso de repetida (supuesto, no decidido en el grilling):** se asume considerar todos los estados (incluido Cancelado) y
  mostrarlos, porque ayuda al Operador a juzgar; es informativo y no bloquea. Jesús solo acordó "cantidad y estados".
- **Glosario:** "Modo lector" (interruptor por equipo) es un término nuevo; candidato a `CONTEXT.md` vía `/domain-modeling` al
  cerrar la feature. Usar Staff/Operador para quien captura y Residente/Persona para el cliente final, como define el glosario.
- **Siguiente paso:** `/to-tickets` para desglosar en tickets verticales; conviene que el seam de navegador sea su propio ticket
  temprano, para que los demás tickets lo usen como prueba de aceptación.

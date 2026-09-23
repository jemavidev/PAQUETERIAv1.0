Status: ready-for-agent
Feature: estadisticas-cobro-dashboard
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, decisiones D1–D16 en
`.scratch/estadisticas-cobro-dashboard/notas-grilling.md`) · prototipo visual en la rama
`prototipo/estadisticas-cobro-dashboard` (variante C, ganadora) · `.scratch/cobro-bodegaje/spec.md` y
`.scratch/estadisticas-cobro-interactivas/spec.md` (módulo y pantalla que este rediseño reemplaza) ·
issues 361, 363 y 364 (`.scratch/pendientes-cliente`) · CONTEXT.md (glosario) · ADR-0001, ADR-0003,
ADR-0005, ADR-0007

---

## Problem Statement

`/administracion/estadisticas-cobro` hoy responde una sola pregunta -- "¿cuánto se recaudó en un rango
de fechas?" -- y la responde con tres totales y tres **listas** (por cliente/apartamento, por usuario y
serie diaria, cada una paginada). El administrador no puede, de un vistazo, saber cómo va la operación:
cuánto dinero entró hoy, esta semana y este mes; cuántos paquetes se cerraron; qué se está quedando
trabado en la bodega y cuánto se cobraría por ello; cuánto se debe por dinero contra entrega; cómo se
comportan los clientes; cuánto tarda cada etapa; ni cuánto le cuestan los SMS de aviso. Tiene que sumar
mentalmente filas de listas o directamente no tiene la respuesta.

Hay además tres problemas de fondo. **Uno:** el sistema no guarda ningún registro de los mensajes que
envía (los proveedores de SMS solo devuelven éxito o excepción, sin decir cuál de la cadena AWS → LIWA →
Twilio lo entregó), así que "SMS enviados" y "costo de SMS con AWS" son imposibles de calcular. **Dos:**
las estadísticas cuentan cada "día" en UTC, que cambia a las 7:00 p. m. hora de Colombia -- con tarjetas
fijas de "Hoy", a las 8 p. m. el tablero ya estaría midiendo el día siguiente. **Tres:** los cobros no
guardan cuánto servicio se perdonó al anular ni por primera entrega, solo el resultado (0), de modo que
las fugas de dinero no se pueden ver.

## Solution

Reemplazar la pantalla por un **tablero de tarjetas, sin listas**, con la barra de filtros de arriba tal
cual está hoy (siete atajos de fecha, Tipo, Cobrado/Anulado) y debajo **tres zonas** identificadas por un
carril vertical de color, con el diseño de la variante C del prototipo (mosaico de 12 columnas):

1. **Panorama** (azul) -- cifras **fijas** Hoy | Semana | Mes en una sola tarjeta por métrica: Ingresos,
   Entregados, Cancelados, SMS enviados por AWS (con su costo estimado) y Tiempos promedio. Con la
   variación ▲▼ contra el mismo tramo del periodo anterior y un minigráfico de 7 días. **No cambia con
   los filtros.**
2. **Ahora** (ámbar) -- la **foto del momento**: paquetes pendientes, qué hay en bodega y desde cuándo,
   cuánto se cobraría por lo que está en bodega, cuánto se debe por dinero contra entrega, cuántos
   clientes hay registrados. **No cambia con los filtros.**
3. **Periodo seleccionado** (verde) -- recaudo (con lo que se dejó de cobrar), paquetes, ritmo y tasas,
   clientes (el cliente #1 por **nombre**, no por teléfono), operación y calidad, y SMS del periodo.
   **Responde a las píldoras**; sin ninguna activa se ven **todos los datos**. Las tarjetas a las que un
   filtro activo no puede acotar se ven atenuadas con la nota «no depende de Tipo» / «no depende de
   Cobrado/Anulado».

Para poder mostrar SMS se agrega un **registro de envíos** (avisos de paquete, códigos de acceso y
mensajes de prueba, con el proveedor que finalmente los entregó), y en la sección de **AWS SNS** de
`/administracion/proveedores` un campo nuevo, "Costo promedio por SMS (COP)", que se guarda en la base de
datos (sin reiniciar nada). Todos los días, semanas y meses del tablero se miden en **hora de Colombia**.

## User Stories

**Acceso y estructura**

1. Como administrador del conjunto, quiero abrir `/administracion/estadisticas-cobro` y ver un tablero de
   tarjetas en vez de listas, para entender el estado de la operación de un vistazo.
2. Como administrador, quiero que la pantalla siga siendo exclusiva del rol ADMIN, para que un Operador
   no vea el recaudo del conjunto.
3. Como administrador, quiero que la barra de filtros de arriba siga igual (Hoy, Ayer, Esta semana, Este
   mes, 3 últimos meses, Semestre, Último año, más Tipo y Cobrado/Anulado), para no tener que reaprender
   nada.
4. Como administrador, quiero ver tres zonas en este orden -- Panorama, Ahora y Periodo seleccionado --
   cada una con su carril de color, para saber al instante si una cifra es fija, de este momento o
   filtrada.
5. Como administrador, quiero que al abrir la pantalla sin filtros el «Periodo seleccionado» muestre
   **todos los datos existentes**, para ver primero el panorama histórico completo.
6. Como administrador, quiero que al cambiar cualquier filtro solo se recalcule la zona «Periodo
   seleccionado» sin recargar la página, para explorar rápido sin perder mi lugar.
7. Como administrador, quiero ver, encima de las tarjetas de «Periodo seleccionado», unos chips con los
   filtros activos (por ejemplo «Este mes» · «Anulado» o «Todos los datos»), para no olvidar qué estoy
   mirando.
8. Como administrador, quiero quitar un atajo de fecha volviendo a hacer clic sobre él, para regresar a
   «todos los datos» sin un botón aparte.
9. Como administrador, quiero que Panorama y Ahora **no** cambien cuando uso los filtros, para tener
   siempre una referencia estable del conjunto completo.
10. Como administrador, quiero que las listas actuales desaparezcan y que cada pregunta que respondían
    tenga una tarjeta equivalente (el cliente #1, el operador con más entregas, el día y la hora
    pico), para no perder información al ganar claridad.

**Panorama (fijo)**

11. Como administrador, quiero una tarjeta «Ingresos» con el dinero cobrado Hoy, en la Semana y en el
    Mes, para ver de un vistazo cómo va el recaudo.
12. Como administrador, quiero una tarjeta «Entregados» con los paquetes entregados Hoy, Semana y Mes,
    para saber cuántos paquetes se cerraron con éxito.
13. Como administrador, quiero una tarjeta «Cancelados» con los paquetes cancelados Hoy, Semana y Mes
    -- separada de «Entregados» --, para ver por aparte cuántos se cerraron sin entregarse.
14. Como administrador, quiero una tarjeta «SMS enviados por AWS» con Hoy, Semana y Mes y su costo
    estimado, para controlar cuánto gasto en mensajes.
15. Como administrador, quiero una sola tarjeta «Tiempos promedio» con tres filas (anuncio → recepción,
    permanencia en bodega y bodegaje cobrado) y las columnas Hoy, Semana y Mes, para comparar cuánto
    tarda cada etapa.
16. Como administrador, quiero que junto a cada cifra de Ingresos, Entregados, Cancelados y SMS aparezca
    una variación porcentual ▲▼ contra el **mismo tramo** del periodo anterior (hoy hasta esta hora vs.
    ayer hasta esa misma hora; la semana a la fecha vs. la anterior hasta el mismo día y hora; el mes a
    la fecha vs. el anterior hasta el mismo día y hora), para no ver un ▼ falso a media mañana.
17. Como administrador, quiero que la flecha use el color según convenga -- más ingresos o más entregados
    en verde, más cancelados en rojo, y los SMS en neutro --, para leer bueno/malo sin pensar.
18. Como administrador, quiero que cuando el periodo anterior valió cero no se muestre un porcentaje
    engañoso (ni «infinito»), para no malinterpretar un arranque desde cero.
19. Como administrador, quiero un minigráfico de los últimos 7 días en Ingresos, Entregados, Cancelados y
    SMS, para ver la tendencia reciente de cada uno.
20. Como administrador, quiero que «Hoy» sea el día de Colombia (00:00–23:59 hora local), para que a las
    8 p. m. «Ingresos Hoy» siga midiendo el día que estoy viviendo.
21. Como administrador, quiero que «Semana» empiece el lunes y «Mes» el día 1, ambos en hora de Colombia,
    para que coincidan con cómo pienso el calendario.
22. Como administrador, quiero que las cifras del Panorama no se afecten por Tipo ni por Cobrado/Anulado,
    para que sean siempre el total del conjunto.

**Ahora (foto del momento)**

23. Como administrador, quiero ver cuántos paquetes están **pendientes** (anunciados + recibidos), con el
    desglose «X anunciados · Y recibidos», para saber cuánto trabajo abierto hay.
24. Como administrador, quiero ver cuántos paquetes hay **en bodega** (recibidos sin entregar), para
    conocer la ocupación real.
25. Como administrador, quiero ver cuántos están **en gracia** (48 horas o menos), para distinguir lo que
    todavía no genera bodegaje.
26. Como administrador, quiero ver cuántos tienen **bodegaje corriendo** (pasaron las 48 horas), para
    saber cuántos ya están acumulando cobro.
27. Como administrador, quiero ver cuántos llevan **más de 7 días** en bodega, para detectar los que se
    están quedando.
28. Como administrador, quiero ver cuántos están **abandonados** (más de 30 días en bodega), para actuar
    sobre ellos.
29. Como administrador, quiero ver el **paquete más antiguo** en bodega (cuántos días lleva, a qué
    apartamento pertenece y su código), para ir directo al que más tiempo lleva.
30. Como administrador, quiero ver cuántos **anuncios nunca llegaron** (anunciados hace más de 7 días sin
    recibirse), para depurar anuncios que no se cumplieron.
31. Como administrador, quiero ver **cuánto se cobraría hoy por lo que está en bodega** (servicio +
    bodegaje acumulado, con la exención de primera entrega), calculado igual que el modal Entregar, para
    saber cuánto dinero espera en bodega.
32. Como administrador, quiero ver la **deuda contra entrega** (suma de los saldos negativos) y cuántos
    clientes la deben, para saber cuánto dinero me deben.
33. Como administrador, quiero ver cuántos **clientes registrados** hay (sin eliminar ni de baja), para
    dimensionar la base de residentes.
34. Como administrador, quiero un semáforo por tarjeta (verde lo sano, ámbar lo que requiere atención,
    rojo lo crítico, azul lo que es dinero), para priorizar sin leer todo.

**Periodo seleccionado -- Recaudo**

35. Como administrador, quiero ver el **total de ingresos** del periodo, para saber cuánto se recaudó.
36. Como administrador, quiero ver el **promedio recaudado por paquete**, para conocer el ticket medio.
37. Como administrador, quiero ver lo **recaudado por bodegaje** y qué porcentaje del recaudo es, para
    saber cuánto pesa el almacenamiento frente al servicio.
38. Como administrador, quiero ver lo **recaudado por servicio** y su porcentaje, para completar la
    mezcla del recaudo.
39. Como administrador, quiero ver cuánto se **exoneró por anulaciones** (con cuántas fueron y su tasa
    sobre los cobros), para vigilar las fugas de dinero.
40. Como administrador, quiero ver cuántas **exenciones por primera entrega** hubo y cuánto se dejó de
    cobrar por ellas, para medir el costo de esa promoción.
41. Como administrador, quiero saber que el monto exonerado y el dejado de cobrar son **estimados con las
    tarifas vigentes** (los cobros no guardan lo perdonado), para no tomarlos como un dato contable.
42. Como administrador, quiero ver el **cobro más alto** del periodo, para identificar los casos
    extremos de bodegaje.

**Periodo seleccionado -- Paquetes, ritmo y tasas**

43. Como administrador, quiero ver el **total de paquetes** con movimiento en el periodo, para dimensionar
    la carga.
44. Como administrador, quiero ver cuántos se **anunciaron**, **recibieron**, **entregaron** y
    **cancelaron** en el periodo (cada uno por la fecha de su propio evento), para ver el flujo completo.
45. Como administrador, quiero ver el **ritmo** de anunciados, recibidos y entregados por día, por
    semana y por mes dentro del periodo, para conocer el volumen habitual.
46. Como administrador, quiero ver la **tasa de entrega** (entregados ÷ cerrados) y la **tasa de
    cancelación** (cancelados ÷ cerrados), para medir la efectividad del proceso.
47. Como administrador, quiero que cuando no hay paquetes cerrados las tasas muestren «—» y no un
    error, para no leer un 0 % falso.

**Periodo seleccionado -- Clientes**

48. Como administrador, quiero ver cuántos **clientes activos** hubo en el periodo (con al menos un
    paquete con movimiento), para saber cuánta gente usa el servicio.
49. Como administrador, quiero ver cuántos **clientes nuevos** hubo (su primera entrega cae en el
    periodo), para medir el crecimiento.
50. Como administrador, quiero ver cuántos **clientes recurrentes** hubo (dos o más paquetes en el
    periodo), para medir la fidelidad.
51. Como administrador, quiero ver el **cliente con más paquetes** del periodo con su **nombre**, su
    apartamento y cuántos paquetes, para conocer a quien más usa el servicio sin tener que reconocer un
    teléfono.
52. Como administrador, quiero ver el **cliente con mayor gasto** (nombre, apartamento y monto), para
    conocer a quien más aporta al recaudo.
53. Como administrador, quiero que el apartamento mostrado sea el que tenía el paquete al anunciarse
    (snapshot), para que un residente que se mudó no reescriba su historia (ADR-0001).
54. Como administrador, quiero que los paquetes dirigidos a un «nombre sin teléfono» no cuenten como un
    cliente, para no inflar la cifra con destinatarios sin identidad.
55. Como administrador, quiero que un empate en «cliente con más paquetes» o «mayor gasto» se resuelva
    siempre igual (por el monto y luego por el nombre), para que la cifra no cambie sola entre cargas.

**Periodo seleccionado -- Operación y calidad**

56. Como administrador, quiero ver el **operador con más entregas** del periodo (nombre y cuántas), para
    reconocer la carga por persona sin una lista.
57. Como administrador, quiero ver el **día de la semana más activo** y qué porcentaje de las entregas
    concentra, para planear turnos.
58. Como administrador, quiero ver la **hora pico** en hora de Colombia (por ejemplo «6 – 7 p. m.»), para
    saber cuándo se concentra la atención.
59. Como administrador, quiero ver qué porcentaje de lo entregado salió **dentro de las 48 horas**, para
    medir cuántos evitan el bodegaje.
60. Como administrador, quiero ver qué porcentaje de lo recibido es **extra-dimensionado**, para conocer
    la mezcla de tipos.
61. Como administrador, quiero ver qué porcentaje de lo recibido llegó **abierto o en mal estado**, para
    vigilar la calidad del servicio de las transportadoras.

**Periodo seleccionado -- SMS**

62. Como administrador, quiero ver los **SMS enviados por AWS** en el periodo con el desglose «X avisos
    · Y códigos de acceso», para entender en qué se va el gasto.
63. Como administrador, quiero ver el **costo estimado** de esos SMS (cantidad × el costo promedio
    configurado hoy), para saber cuánto gasto.
64. Como administrador, quiero ver cuántos SMS **fallaron en todos los proveedores**, para detectar
    problemas de entrega.
65. Como administrador, quiero ver el **costo de SMS por paquete**, para medir cuánto cuesta avisar cada
    paquete.
66. Como administrador, quiero que las tarjetas de SMS indiquen **desde cuándo** hay registro, para no
    tomar un conteo parcial como si fuera histórico.
67. Como administrador, quiero que si todavía no configuré un costo se muestren igual las cantidades y
    el costo diga «Configura el costo en Proveedores» (con enlace), para saber qué falta.
68. Como administrador, quiero que si aún no hay ningún SMS registrado las tarjetas muestren 0 y lo
    aclaren, y no un error.

**Filtros y «no aplica»**

69. Como administrador, quiero que el filtro Tipo (Normal / Extra-dimensionado) acote las tarjetas de
    paquetes con tipo (recibidos, entregados, recaudo, tiempos y calidad), para analizar cada tipo por
    separado.
70. Como administrador, quiero que el filtro Cobrado/Anulado acote solo las tarjetas de cobro, para
    comparar lo cobrado contra lo anulado.
71. Como administrador, quiero que las tarjetas a las que un filtro activo no puede acotar (por ejemplo
    «Anunciados» con Tipo, o cualquier SMS con Cobrado/Anulado) se vean atenuadas con la nota «no depende
    de …», para no confundir un total sin filtrar con uno filtrado.
72. Como administrador, quiero que una tarjeta atenuada muestre su valor **sin filtrar**, para seguir
    teniendo el dato completo a mano.
73. Como administrador, quiero que los atajos de fecha significen: Hoy, Ayer, Esta semana (desde el
    lunes), Este mes (desde el día 1), 3 últimos meses, Semestre (últimos 6 meses) y Último año (últimos
    12 meses), todos terminando hoy y en hora de Colombia, para que el rango sea predecible.
74. Como administrador, quiero que las píldoras de Tipo y Cobrado/Anulado conserven su aspecto de tres
    estados (suave, activo, opacado), para reconocerlas.

**Configuración del costo por SMS (`/administracion/proveedores`)**

75. Como administrador, quiero un campo «Costo promedio por SMS (COP)» dentro de la sección de AWS SNS
    de `/administracion/proveedores`, para que el tablero pueda calcular lo que gasto en mensajes.
76. Como administrador, quiero que ese campo exista **solo para AWS**, no para LIWA ni Twilio, para que
    el costo corresponda al proveedor que se factura.
77. Como administrador, quiero que al guardar el costo se aplique **al instante y sin reiniciar el
    servidor** (a diferencia de las credenciales), para poder ajustarlo cuando cambie la tarifa o el
    dólar.
78. Como administrador, quiero poder escribir decimales y dejar el campo vacío (= sin configurar), y que
    un valor negativo o no numérico se rechace con un mensaje claro, para no romper el cálculo.
79. Como administrador, quiero que al cambiar el costo **todos** los periodos se recalculen con el
    precio nuevo, para que el tablero refleje siempre el precio de hoy.

**Registro de envíos de SMS**

80. Como administrador, quiero que cada SMS de aviso de un paquete quede registrado con su fecha, su
    evento y el paquete, para poder contarlos.
81. Como administrador, quiero que cada código de acceso (OTP) enviado por SMS también quede registrado,
    diferenciado de los avisos, para que el conteo y el costo coincidan con la factura de AWS.
82. Como administrador, quiero que los mensajes de prueba que envío desde la administración de
    plantillas también queden registrados (como avisos sin paquete), para que el conteo no subestime el
    gasto.
83. Como administrador, quiero que el registro anote **qué proveedor entregó** cada mensaje (AWS SNS,
    LIWA o Twilio), para contar solo los de AWS.
84. Como administrador, quiero que si AWS falló y el mensaje salió por otro proveedor **no cuente como
    de AWS**, para no pagar en el tablero un mensaje que AWS no entregó.
85. Como administrador, quiero que un mensaje que ningún proveedor logró entregar quede como **fallido**,
    para medir los fallos.
86. Como administrador, quiero que un mensaje enviado con el remitente de desarrollo/consola (sin
    proveedor real) **no se registre**, para que mi entorno local no contamine los conteos.
87. Como administrador, quiero que el registro de envíos **nunca** frene ni haga fallar un envío ni una
    transición de paquete, para que una falla al anotar no le cueste un aviso a un residente.
88. Como administrador, quiero que el registro **no guarde el texto del mensaje ni el teléfono
    completo**, para no acumular datos personales que no se necesitan.

**Calidad general**

89. Como administrador, quiero que el tablero se vea bien en celular, tableta y escritorio (las tarjetas
    se reacomodan en 1, 2 o más columnas), para consultarlo desde cualquier dispositivo.
90. Como administrador, quiero que las cifras usen el mismo formato del resto de la aplicación (comas de
    miles, «$» pegado), para que no haya dos convenciones.
91. Como administrador, quiero que el tablero cargue en un tiempo razonable aun con decenas de miles de
    paquetes, para poder usarlo a diario.
92. Como administrador, quiero que con la base vacía (sin paquetes ni cobros) el tablero muestre ceros y
    «—» sin errores, para que un ambiente nuevo no se vea roto.
93. Como administrador, quiero que un parámetro de filtro inválido o desconocido se ignore en silencio
    (sin error 400), para que un enlace viejo no rompa la pantalla.
94. Como desarrollador, quiero poder fijar el reloj al probar los periodos y comparativos, para que las
    pruebas no dependan de la hora en que corran (ni fallen cerca de la medianoche).
95. Como desarrollador, quiero que la aritmética del tablero viva en un servicio de dominio probado
    contra Postgres real, para que la ruta web solo cablee y renderice.
96. Como desarrollador, quiero retirar los agregados y las pruebas de las tres listas que ya nadie
    consulta, para no dejar código muerto.

## Implementation Decisions

**Estructura, zonas y diseño (variante C del prototipo)**

- La pantalla se rehace como tablero de tarjetas. Se conserva la barra de filtros con sus tres grupos de
  controles; se eliminan las tres tablas paginadas y toda su paginación.
- Tres zonas en este orden, cada una con un **carril vertical de color** a la izquierda y **sin
  encabezados de sección**: Panorama (azul), Ahora (ámbar) y Periodo seleccionado (verde). Cuadrícula de
  12 columnas; por debajo de ~900 px las tarjetas pasan a 2 por fila y en celular a 1.
- Anatomía de la tarjeta: borde superior en el color de su zona, etiqueta pequeña arriba (la categoría, o
  «foto» / «dinero» en Ahora), título, cifra grande, detalle pequeño y, si corresponde, la nota «no
  depende de …».
- **Panorama:** Ingresos (6 columnas), Entregados (3), Cancelados (3), SMS enviados por AWS (6, con el
  costo estimado debajo) y Tiempos promedio (6, **una** tarjeta con tres filas × Hoy/Semana/Mes). Cada
  trío con etiquetas ▲▼ y, en Ingresos, Entregados, Cancelados y SMS, un minigráfico de los últimos 7
  días (día actual incluido, en hora de Colombia). *Nota: el minigráfico lo trae el prototipo y no estaba
  en las decisiones D1–D15; se incluye porque el cliente aprobó la variante C tal como se le mostró y su
  costo es una consulta agrupada por día por métrica.*
- **Ahora:** tarjetas de 2 columnas (6 por fila) con un punto de semáforo (gris, verde, ámbar, rojo) y la
  etiqueta «foto»; las dos de dinero (Por cobrar en bodega, Deuda contra entrega) de 3 columnas con punto
  azul y etiqueta «dinero».
- **Periodo seleccionado:** un solo mosaico de tarjetas de 3 columnas (4 por fila) con su categoría como
  etiqueta -- Recaudo, Paquetes, Ritmo y tasas, Clientes, Operación y calidad, SMS del periodo --; encima,
  los chips de filtros activos. Tarjeta atenuada = opacidad ~40 %, escala de grises y la nota.
- Formato de cifras como el resto de la aplicación (comas de miles, «$» pegado; horas con un decimal por
  debajo de 10). La primera carga se renderiza completa en el servidor; los cambios de filtro reemplazan
  solo la zona «Periodo seleccionado» mediante el mismo mecanismo de actualización en vivo que ya usa la
  pantalla (petición marcada como en segundo plano que devuelve solo ese fragmento).
- El prototipo (rama `prototipo/estadisticas-cobro-dashboard`) es la **referencia visual**, no código a
  promover: sus cifras son inventadas y sus filtros se simulan en el navegador.
- Como el sistema compila el CSS a mano y el despliegue no lo recompila, las clases nuevas del tablero
  exigen reconstruir y versionar el CSS compilado antes de desplegar.

**Tiempo: hora de Colombia en todo el tablero**

- Todo límite de día, semana, mes o rango, el agrupamiento por día, el ritmo por día y la hora pico se
  calculan en **hora de Colombia (UTC-5 fijo, sin horario de verano)**, la misma zona que el sistema ya
  usa para mostrar fechas -- no en UTC ni dependiendo de tablas de zonas horarias del sistema operativo.
  Esto **desplaza 5 horas** los límites de día respecto de la pantalla actual: los números por día
  cambian un poco y es lo esperado.
- El servidor calcula «hoy» en hora local; el parámetro `hoy` que hoy manda el navegador deja de hacer
  falta y se retira.
- El servicio del tablero recibe el instante actual como **dato inyectable** (no lee el reloj por su
  cuenta), para poder fijarlo en pruebas.
- Periodos: **Hoy** = el día local en curso; **Ayer** = el día local anterior; **Esta semana** = desde el
  lunes 00:00 hasta ahora; **Este mes** = desde el día 1 00:00 hasta ahora; **3 últimos meses**,
  **Semestre** (= últimos 6 meses) y **Último año** (= últimos 12 meses) son ventanas móviles que empiezan
  el día siguiente a la misma fecha N meses atrás (ajustando a fin de mes) y terminan hoy, ambas fechas
  incluidas. Sin atajo activo no hay rango: todos los datos.
- **Comparativos** (solo Panorama): contra el mismo tramo del periodo anterior -- Hoy contra ayer hasta la
  misma hora; Semana contra la anterior hasta el mismo día de la semana y hora; Mes contra el anterior
  hasta el mismo día del mes y hora (si el mes anterior es más corto se recorta a su último día).
  Variación = (actual − anterior) ÷ anterior; con anterior en cero no se calcula porcentaje. Sentido: para
  Ingresos y Entregados subir es bueno; para Cancelados, bajar es bueno; SMS es neutro.

**Definiciones de las tarjetas (glosario del dominio: Persona, Paquete, Estados, Usuario = Staff)**

- *En la interfaz se dice «Clientes» (copy que pidió el cliente); en el dominio la entidad es la
  **Persona**.* Una Persona se identifica por su Teléfono (o su usuario de WhatsApp, ADR-0007); el
  agrupamiento por cliente sigue usando el **Teléfono del destinatario** del Paquete. Los Paquetes de
  «nombre sin teléfono» no pertenecen a ninguna Persona y **no cuentan** en ninguna cifra de clientes.
  Las Personas eliminadas (anonimizadas, ADR-0005) o de baja no cuentan como registradas.
- **Ingresos / Total de ingresos:** suma del total de todos los Cobros cobrados en el periodo (un cobro
  anulado aporta su bodegaje, que nunca se exonera). **Promedio por paquete:** total de ingresos ÷
  cantidad de cobros. **Recaudado por bodegaje / por servicio:** sumas de los componentes de bodegaje y de
  servicio (base) de esos cobros, con su porcentaje del total. **Cobro más alto:** el mayor total de un
  cobro del periodo, con sus días en bodega.
- **Exonerado por anulaciones** y **lo dejado de cobrar por primera entrega:** son **estimaciones con las
  tarifas de servicio vigentes** (la tarifa del Tipo del paquete), porque el cobro solo guarda el
  resultado (servicio en 0), no lo perdonado. La tarjeta lo dice. **Exenciones por primera entrega** =
  cobros con servicio en 0 y sin motivo de anulación. La tasa de anulación = anulados ÷ cobros.
- **Procesados = cerrados:** Entregados (por fecha de entrega) y Cancelados (por fecha de cancelación),
  siempre por separado.
- **Total de paquetes** = Paquetes con **cualquier movimiento** (anuncio, recepción, entrega o
  cancelación) en el periodo. **Anunciados / Recibidos / Entregados / Cancelados** = los que tienen esa
  marca de tiempo dentro del periodo.
- **Tasa de entrega** = entregados ÷ (entregados + cancelados); **tasa de cancelación** = cancelados ÷
  (entregados + cancelados), por fecha de cierre, en el periodo. Suman 100 %.
- **Ritmo** (por día / semana / mes) = total del periodo ÷ días locales del periodo × 1, × 7 y × 30. Con
  «todos los datos», los días van desde el primer movimiento hasta hoy.
- **Tiempos:** *anuncio → recepción* = promedio de (recibido − anunciado) de los paquetes recibidos en el
  periodo; *permanencia en bodega* = promedio de (entregado − recibido) de los entregados en el periodo;
  *bodegaje cobrado* = promedio de horas de permanencia solo de los cobros con bloques de bodegaje (la
  métrica que ya existe hoy).
- **Ahora:** *Pendientes* = Anunciados + Recibidos actuales; *En bodega* = Recibidos actuales; *En
  gracia* = recibidos hace 48 h o menos; *Con bodegaje corriendo* = más de 48 h; *Más de 7 días* y
  *Abandonados (más de 30 días)* = por antigüedad de la recepción; *Paquete más antiguo* = el recibido con
  la recepción más antigua (días, Apartamento del snapshot y código); *Anuncios que nunca llegaron* =
  anunciados hace más de 7 días sin recibirse; *Por cobrar en bodega* = suma, sobre los Recibidos, del
  cobro que se calcularía si se entregaran ahora (misma aritmética y misma exención de primera entrega que
  el modal Entregar); *Deuda contra entrega* = suma de los saldos **negativos** de las Personas (los
  positivos no se compensan) y cuántas Personas los tienen; *Clientes registrados* = Personas sin
  eliminar y sin baja administrativa.
- **Clientes del periodo:** *activos* = Personas con al menos un Paquete con movimiento en el periodo;
  *nuevos* = Personas cuya **primera** entrega histórica cae en el periodo; *recurrentes* = activos con
  dos o más Paquetes con movimiento en el periodo; *cliente con más paquetes* y *cliente con mayor gasto*
  = un solo cliente con su **nombre** (el de la Persona; si no hubiera, el nombre congelado en el paquete),
  su Apartamento del **snapshot** más reciente del periodo (ADR-0001) y la cifra; empates por monto y
  luego por nombre.
- **Operación y calidad:** *operador con más entregas* = el Usuario (staff) con más entregas del periodo;
  *día más activo* = el día de la semana con más entregas y su porcentaje; *hora pico* = la franja de una
  hora local con más entregas; *entregados dentro de 48 h*; *% extra-dimensionados* y *% abiertos o en mal
  estado* sobre los recibidos del periodo (condición ABIERTO o REGULAR). Los empates se resuelven de forma
  determinista (primer día en orden lunes → domingo; primera hora del día).

**Filtros y matriz de «no aplica»**

- Parámetros de la ruta: el atajo de fecha (clave), Tipo y Cobrado/Anulado. Se retiran `desde`, `hasta`,
  `hoy`, el filtro por usuario y los tres números de página. Valores desconocidos o inválidos se ignoran
  en silencio, sin error.
- Panorama y Ahora **ignoran los tres filtros**. Solo «Periodo seleccionado» los aplica, según esta
  matriz (1 = el filtro puede acotar la tarjeta; 0 = no puede, y con ese filtro activo la tarjeta se
  atenúa y muestra su valor **sin filtrar**). *Fuente: el prototipo aprobado.*

  | Categoría | Tarjeta | Tipo | Cobrado/Anulado |
  |---|---|---|---|
  | Recaudo | Total de ingresos, Promedio por paquete, Recaudado por bodegaje, Recaudado por servicio, Exonerado por anulaciones, Cobro más alto | 1 | 1 |
  | Recaudo | Exenciones por primera entrega | 1 | 0 |
  | Paquetes | Total de paquetes, Anunciados, Cancelados | 0 | 0 |
  | Paquetes | Recibidos, Entregados | 1 | 0 |
  | Ritmo y tasas | Ritmo de anunciados; Tasa de entrega; Tasa de cancelación | 0 | 0 |
  | Ritmo y tasas | Ritmo de recibidos; Ritmo de entregados | 1 | 0 |
  | Clientes | Activos, Nuevos, Recurrentes, Cliente con más paquetes | 1 | 0 |
  | Clientes | Cliente con mayor gasto | 1 | 1 |
  | Operación y calidad | Operador con más entregas, Día más activo, Hora pico, % dentro de 48 h, % abiertos o en mal estado | 1 | 0 |
  | Operación y calidad | % extra-dimensionados | 0 | 0 |
  | SMS del periodo | Enviados, Costo estimado, Fallidos, Costo por paquete | 0 | 0 |

- «Cobrado» = cobro sin motivo de anulación; «Anulado» = cobro con motivo. Tipo se resuelve por el Tipo
  del paquete (los anunciados y los cancelados antes de recibirse no tienen Tipo, de ahí sus 0).

**Módulos a construir o modificar**

- **Servicio de estadísticas del tablero (dominio):** reemplaza al servicio de estadísticas orientado a
  listas. Expone una consulta que recibe los filtros y el instante actual y devuelve una estructura con
  las tres zonas (valores, variaciones, series de 7 días, banderas de aplicabilidad por tarjeta y la
  fecha desde la que existe registro de SMS). Ejecuta un **número fijo de consultas agregadas** (sin
  recorrer paquetes uno a uno, salvo el cálculo de «por cobrar» que se resuelve en lote, como ya lo hace
  la lista de paquetes), y agrupa día y hora en hora de Colombia. Reutiliza la aritmética de cobro ya
  existente para «por cobrar en bodega» y el cálculo de saldos negativos ya existente.
- **Ruta y plantillas de la pantalla:** delgadas -- arman los filtros, llaman al servicio, renderizan las
  tres zonas y, ante la petición en segundo plano, devuelven solo el fragmento de «Periodo seleccionado».
  Solo ADMIN.
- **Registro de envíos de SMS (dominio + esquema nuevo):** tabla append-only con: momento del envío, **tipo**
  (aviso de paquete / código de acceso), evento del paquete (solo avisos), paquete (solo avisos, sin
  restricción cuando es prueba), **proveedor** que lo entregó (AWS SNS, LIWA o Twilio) y **resultado**
  (enviado / fallido). Sin texto del mensaje y sin teléfono. Índices para contar por proveedor, resultado
  y fecha. Un servicio de dominio para registrar y para contar por periodo, tipo y resultado, y para
  saber cuál fue el primer registro (la fecha «desde»).
- **Ruta de envío:** cada remitente SMS real declara su proveedor; la cadena de failover informa **cuál
  de sus remitentes entregó** el mensaje (o que todos fallaron); un envoltorio de registro, armado donde
  hoy se arma la cadena de remitentes, anota el resultado. Cubre los **tres caminos** que envían SMS: los
  avisos de estado (que se envían en segundo plano), los códigos de acceso y los mensajes de prueba de
  plantillas. El registro se escribe con **su propia sesión/transacción** (los avisos se envían fuera del
  request) y es **tolerante a fallos**: si anotar falla se ignora y el envío o la transición del paquete
  no se ven afectados. Los remitentes de consola/desarrollo no registran. Cada mensaje cuenta **una vez**,
  aunque el failover haya intentado varios proveedores; si todos fallan, una fila «fallido».
- **Configuración de proveedores:** un valor nuevo, numérico opcional (decimales, ≥ 0), «costo promedio por
  mensaje en COP», guardado en la **base de datos** sobre la configuración del proveedor AWS SNS del canal
  SMS -- no en el `.env`, porque esa pantalla escribe el `.env` del servidor por SSH y **reinicia el
  contenedor** al cambiar una credencial, y un precio no es un secreto. El campo se dibuja **solo en la
  sección de AWS SNS**, se aplica al instante y deja constancia de quién y cuándo lo cambió con los campos
  de actualización que la configuración ya tiene.
- **Cálculo del costo:** costo estimado = cantidad de SMS enviados por AWS × el costo promedio **vigente
  hoy**. No se guarda un precio por mensaje: al cambiarlo, todos los periodos se recalculan. Un mensaje
  = una unidad, sin importar cuántos segmentos consuma (el promedio ya lo absorbe). Sin costo configurado,
  se muestran cantidades y el costo indica cómo configurarlo.
- **Cambios de esquema:** dos migraciones Alembic (la tabla del registro con sus índices y la columna de
  costo en la configuración del proveedor), con el ORM alineado (hay una prueba de paridad
  esquema↔ORM) y respetando el árbol de migraciones de raíz única (ADR-0002); el identificador de
  revisión no puede superar los 32 caracteres.
- **Retiro:** se elimina de la pantalla y del servicio lo específico de las tres listas (por
  cliente/apartamento, por usuario, serie diaria) y sus pruebas obsoletas.

## Testing Decisions

- **Qué es una buena prueba aquí:** describe comportamiento externo -- dado un conjunto de paquetes,
  cobros, personas, saldos y envíos sembrados y un **reloj fijo**, qué cifra, variación, bandera o
  atenuado produce el tablero -- y nunca la estructura interna (cuántas consultas, nombres de funciones
  privadas, clases CSS). Las pruebas con tiempo **inyectan el reloj y usan fechas fijas**: ya hubo una
  falla real en CI por una prueba relativa a «ahora» cerca de la medianoche UTC.
- **Seams acordados con el cliente (tres):**
  1. **Servicio de estadísticas del tablero (dominio), contra Postgres real y con reloj inyectable.**
     Aquí va casi toda la lógica: cada tarjeta y su definición; los límites de Hoy/Ayer/Semana/Mes/3
     meses/Semestre/Año **en hora de Colombia** (incluidos los casos justo antes y después de las 19:00
     locales y la medianoche local); los comparativos del «mismo tramo» (incluido un mes anterior más
     corto y periodo anterior en cero); tasas sobre cerrados (y sin cerrados); la foto de Ahora (por
     cobrar con exención de primera entrega, deuda solo de saldos negativos, bodega por antigüedad,
     abandonados, más antiguo); clientes (nombre, snapshot de apartamento, exclusión de «nombre sin
     teléfono» y de Personas eliminadas, empates deterministas); operación (día/hora pico, empates);
     estimaciones de exonerado y dejado de cobrar con las tarifas vigentes; los filtros Tipo y
     Cobrado/Anulado y la **matriz de «no aplica»**; y la base vacía.
  2. **Ruta web por HTTP, delgada.** Solo ADMIN (sin sesión redirige; Operador recibe 403); se renderizan
     las tres zonas y los chips; la petición en segundo plano devuelve solo el fragmento de «Periodo
     seleccionado»; las tarjetas atenuadas llegan marcadas; los parámetros inválidos se ignoran; ya no
     existen las tres listas ni el paginado. **No** se re-prueba aquí la aritmética.
  3. **Entrega de SMS y su configuración.** (a) El servicio de registro de envíos: registrar y contar por
     periodo, tipo, proveedor y resultado, y la fecha del primer registro. (b) La ruta de envío con
     **proveedores falsos**: la cadena de failover informa quién entregó; un fallo del primero con éxito
     del segundo cuenta como del segundo, no de AWS; todos fallando deja «fallido»; el remitente de
     consola no registra; una falla al anotar **no** rompe el envío ni la transición; se registran los
     avisos, los códigos de acceso y los mensajes de prueba. (c) La pantalla de proveedores: el campo de
     costo aparece solo en AWS SNS, se guarda sin reinicio, acepta decimales, rechaza negativos y texto, y
     acepta vacío.
- **Prior art:** las pruebas de integración del servicio de cobro contra Postgres real (patrón de este
  seam, incluida la estrategia de fechas fijas), las pruebas web de la pantalla de estadísticas actual, las
  pruebas del failover de SMS, del servicio de notificaciones y del cableado de OTP, las de la pantalla de
  proveedores y del servicio de configuración de proveedores, y las de saldos contra entrega.
- Las pruebas de las tres listas retiradas se eliminan junto con su código; lo aprovechable
  (semántica de filtros por rango, Tipo y Cobrado/Anulado) se migra a las del servicio nuevo.
- La aritmética de periodos, comparativos y tasas es lógica delicada: buena candidata para desarrollarla
  con pruebas primero.

## Out of Scope

- Exportar el tablero (CSV, PDF, imagen) o imprimirlo.
- Actualización automática periódica de Panorama y Ahora (se calculan al cargar la página o al cambiar un
  filtro).
- Cualquier lista, ranking o detalle por fila (top N de clientes, tabla por operador, serie diaria); el
  tablero solo consolida.
- Gráficos más allá del minigráfico de 7 días.
- **Recuperar el histórico de SMS** anterior a la activación del registro: no existe y no se puede
  reconstruir.
- Contar o costear mensajes por otros canales (WhatsApp, correo) o de otros proveedores distintos de AWS;
  el costo solo se configura para AWS SNS.
- Precios por versión, por segmento de mensaje o conciliación contra la factura de AWS; el costo es un
  promedio único recalculado con el precio actual.
- Guardar, dentro de cada cobro, cuánto servicio se perdonó (hoy se estima con las tarifas vigentes).
- Cambiar las reglas del cobro y el bodegaje, las tarifas, los motivos de anulación o el dinero contra
  entrega.
- Un historial completo de cambios del costo por SMS (basta con quién y cuándo lo cambió por última vez).
- Vistas distintas del tablero por rol; sigue siendo solo ADMIN.
- Umbrales, alertas o notificaciones a partir de las cifras.

## Further Notes

- **Vocabulario:** la interfaz dice «Clientes» (pedido del cliente); el glosario evita «cliente» como
  entidad y usa **Persona**; «Usuario» significa staff. La spec y el código de dominio usan Persona/Usuario;
  solo el texto de pantalla dice «Clientes».
- **Entregas sugeridas** (las afina `/to-tickets`): **A** -- el tablero con todo lo que ya tiene datos (las
  tres zonas sin las tarjetas de SMS), incluyendo el cambio a hora de Colombia, la matriz de «no aplica»,
  los comparativos y el retiro de las listas; **B** -- el registro de envíos, sus ganchos en avisos,
  códigos y pruebas, el campo de costo en Proveedores y las tarjetas de SMS de Panorama y del Periodo.
  Con esa separación, el cambio en la ruta de notificaciones (lo único que toca algo ya en producción)
  queda aislado del rediseño visual.
- **Consecuencia visible del cambio de zona horaria:** los totales por día de esta pantalla cambian
  respecto de la versión actual porque los límites de día se corren 5 horas; es intencional.
- **Decisiones del cliente que conviene recordar:** el costo de SMS **se recalcula con el precio actual**
  (el cliente eligió esa opción sobre guardar el precio vigente al enviar); las tasas son **sobre
  cerrados**; «procesados» son cerrados con entregados y cancelados **separados**.
- **Supuestos pendientes de confirmar con el cliente al revisar la implementación:** el minigráfico de 7
  días, la matriz de «no aplica» tal como estaba en el prototipo, y que «Costo de SMS por paquete» divide
  el costo del periodo entre el total de paquetes con movimiento.
- El script de datos de demostración para el ambiente local (`scripts`, sin commitear) imprime su resumen
  con el servicio de estadísticas actual: habrá que adaptarlo al servicio nuevo o quitarle ese resumen al
  retirar el anterior.
- El ambiente local ya puede llenarse con ~1.600 paquetes de 15 meses (script de datos de demostración
  con `--reiniciar`) para revisar el tablero con volumen real; no incluye envíos de SMS, así que las
  tarjetas de SMS se ven vacías hasta que el registro exista y haya envíos.

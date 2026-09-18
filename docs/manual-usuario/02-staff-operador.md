# 2. Guía para el staff operador

Esta guía es para vos si trabajás con un usuario de staff en PaqueteX —
Operador o Administrador— y querés saber cómo se usa cada pantalla en el
día a día: recibir paquetes, atender residentes, resolver dudas en
portería. Si sos Administrador, además tenés funciones extra que están en
la [Guía de Administrador](03-staff-admin.md) — es un complemento de esta
guía, no un reemplazo: todo lo de acá también es tuyo.

A lo largo del documento vas a encontrarte siempre con el mismo grupo de
vecinos inventados en los ejemplos, para que sea fácil seguir el hilo:

- **Angélica Ramírez** — vive en la Torre 5, Apto 302, y es la Principal
  de esa unidad.
- **Daniel Ramírez** — su hijo, vive con ella en el mismo apartamento.
- **Carlos Pérez** — vecino de la Torre 2, Apto 105, a quien más adelante
  "mudamos" de unidad como ejemplo.

## Cómo usar esta guía

La armamos en el orden en que normalmente se aprende el rol — cada bloque
da algo por sentado del anterior, así que si sos nuevo, conviene leerlos en
orden la primera vez:

| # | Bloque | De qué se trata |
|---|---|---|
| 1 | [Iniciar sesión y tu perfil](#1-iniciar-sesión-y-tu-perfil) | Entrar, tu perfil, cerrar sesión |
| 2 | [Paquetes — la bandeja principal](#2-paquetes--la-bandeja-principal-paquetes) | Buscar, filtrar, entender los 4 estados |
| 3 | [Recibir un paquete](#3-recibir-un-paquete) | Lo que más vas a usar |
| 4 | [Entregar un paquete](#4-entregar-un-paquete) | Cobro, anulación, saldo contra entrega |
| 5 | [Cancelar un paquete](#5-cancelar-un-paquete) | — |
| 6 | [Resolver quién es el destinatario](#6-resolver-quién-es-el-destinatario) | La parte que más cuesta al principio: asignar unidad, corregir a quién corresponde, promover a un residente |
| 7 | [Anunciar un paquete por lote](#7-anunciar-un-paquete-por-lote-announce) | Cuando alguien llama o llega avisando que espera algo |
| 8 | [Residentes — buscar](#8-residentes--buscar-residentes) | Las 4 formas de buscar en el padrón |
| 9 | [La ficha de un residente](#9-la-ficha-de-un-residente) | Datos, Dirección, Notificaciones, Residentes de la unidad |
| 10 | [Baja, reactivación y bloqueos](#10-baja-administrativa-reactivar-bloquear-liberar-bloqueo) | Cuando alguien se va, vuelve, o hay que bloquearlo |
| 11 | [Saldos contra entrega](#11-saldos-contra-entrega) | Plata a favor o en contra de un residente |
| 12 | [Consultar en modo staff](#12-consultar-en-modo-staff-vista-híbrida) | La pantalla pública, con tus mismos botones de siempre |

Si estás entrenando a alguien para su primer turno y el tiempo apremia, con
los bloques **1 a 6** ya tiene lo esencial — recibir y entregar paquetes es
la mayor parte del día. Todo lo que tiene que ver con residentes (8 a 11) se
usa menos seguido, pero como toca datos sensibles, mejor leerlo con calma
antes que con alguien esperando en portería.

## Todo lo que podés hacer, de un vistazo

| Querés... | Lo encontrás en... |
|---|---|
| Entrar, salir, editar tu perfil o cambiar tu contraseña | La pantalla de ingreso, y el menú de cuenta → Mi perfil |
| Ver, buscar y filtrar todos los paquetes | La bandeja de Paquetes |
| Recibir, entregar o cancelar un paquete puntual | Los botones en la fila de cada paquete |
| Asignarle unidad a un paquete, o corregir a quién le corresponde | Los botones "Asignar apartamento" y "Modificar" de cada fila |
| Anunciar un paquete a nombre de un residente | La pantalla de Anunciar para staff |
| Buscar residentes y abrir su ficha completa | El buscador de Residentes |
| Editar datos, apartamento, notificaciones u ocupantes de un residente | Las tabs dentro de la ficha de cada residente |
| Dar de baja, reactivar, bloquear o liberar el bloqueo de un residente | La ficha de cada residente |
| Ver y registrar movimientos de saldo contra entrega | La vista de Saldos, o la ficha de cada residente |
| Resolver un paquete puntual por su código, con las mismas acciones de siempre | La pantalla de Consultar |

---

## 1. Iniciar sesión y tu perfil

### Cómo entrar

Email + contraseña. Un par de cosas para tener presentes:
- Si alguno de los dos está mal, el sistema marca **ambos** campos en
  rojo con el mismo mensaje — nunca te dice cuál de los dos falló, para no
  revelar si ese email existe en el sistema.
- Hay un límite de intentos por minuto; si lo superás, te va a pedir que
  esperes un momento.
- Al entrar bien, caés directo en la bandeja de Paquetes — la pantalla que
  de verdad vas a usar primero.

**¿Olvidaste tu contraseña?** En la misma pantalla de ingreso hay un link
para pedir que te llegue un correo de recuperación — el enlace que te
manda es válido por 30 minutos y se puede usar una sola vez. Por seguridad
el mensaje en pantalla es siempre el mismo, exista o no ese email en el
sistema.

### Tu perfil

Sin importar tu rol, siempre podés:
- Editar tu propio nombre, teléfono y WhatsApp.
- Cambiar tu propia contraseña (te la pide dos veces; si no coinciden, te
  avisa antes de guardar).

**Ojo:** tu propio rol no lo podés tocar acá — ni siquiera existe ese
campo en tu formulario. Eso solo lo cambia un Administrador, desde
Personal. Editar tus datos y cambiar tu contraseña son dos formularios
separados en la misma pantalla — guardar uno no afecta al otro.

### Cerrar sesión

Un único botón te cierra la sesión de staff y, si además tenías abierta una
sesión de residente en el mismo navegador, cierra las dos juntas.

---

## 2. Paquetes — la bandeja principal (`/paquetes`)

Acá vas a pasar la mayor parte del turno: la lista completa de paquetes,
con un buscador y filtros por estado.

### Buscar

Un solo campo te alcanza para casi todo — probá con cualquiera de estos:

- Código de acceso o número de guía
- Nombre del destinatario
- Teléfono (con los últimos 4 dígitos alcanza, no hace falta escribirlo
  completo)
- Torre y Apartamento
- Nombre, email o WhatsApp de quien **anunció** el paquete

Por defecto, la búsqueda solo mira los datos del destinatario — no vas a
encontrar el paquete de otra persona solo porque alguien más lo anunció
por ella. Si necesitás ver esas conexiones (quién anuncia para quién),
activá el interruptor **Conectados**.

> **Ejemplo:** Angélica llama preguntando por un paquete. En vez de
> pedirle el código completo, escribís `1234` (los últimos 4 dígitos de
> `3011234567`) y aparece en la lista — o escribís `5 302` (Torre y
> Apartamento) si no tenés el teléfono a mano.

**Tip:** si en cambio tenés el código de acceso completo (ej. `AB4X9K`),
escribirlo trae ese paquete puntual más cualquier otro `RECIBIDO` de la
misma unidad o el mismo destinatario, sin importar qué filtro de estado
tenías puesto.

### Filtrar por estado

Cuatro colores, se pueden combinar con la búsqueda de texto:

| Estado | Color | Qué significa |
|---|---|---|
| Anunciado | Ámbar | Alguien avisó que espera el paquete — todavía no llegó a portería. |
| Recibido | Azul | Ya está en portería, esperando que lo retiren. |
| Entregado | Verde | Ciclo cerrado, ya se lo llevaron. |
| Cancelado | Rojo | Se dio de baja sin llegar a entregarse (anuncio erróneo, duplicado, etc.). |

### Qué tiene cada fila

Además de los datos del paquete, cada fila tiene accesos rápidos:
- WhatsApp y llamada al destinatario (apagados si no tiene el dato, o si
  desactivó ese canal).
- Llamada/email a quien **anunció** el paquete, cuando es alguien
  distinto del destinatario.
- **Modificar**, para corregir a quién corresponde (ver
  [bloque 6](#6-resolver-quién-es-el-destinatario)).
- Según el estado: **Recibir**, **Entregar** o **Cancelar**.
- **Eliminar** (borrado real, no una cancelación) — solo la ven los
  Administradores.

El botón **Ver** te abre el detalle completo, con la línea de tiempo del
paquete (quién hizo cada paso, y cuándo). Esa línea de tiempo carga un
instante después de abrir el modal, para que el resto de la pantalla no se
sienta lenta esperándola.

---

## 3. Recibir un paquete

Botón **Recibir**, en cualquier paquete que esté Anunciado — o desde
Consultar, o como parte del flujo doble de Anunciar
([bloque 7](#7-anunciar-un-paquete-por-lote-announce)).

1. Completá número de guía (opcional), tipo de paquete y condición en que
   llegó.
2. Podés agregar hasta **3 fotos** — se suben solas en segundo plano, no
   hace falta esperar a que terminen para seguir.
3. Si el paquete todavía no tiene Torre y Apartamento, podés resolverlo ahí
   mismo, sin salir del modal (ver [bloque 6](#6-resolver-quién-es-el-destinatario)).
4. Si hace falta confirmar a qué residente exacto corresponde, el sistema
   **no completa la recepción todavía** — te muestra la lista de
   candidatos reales de esa unidad para que elijas uno, o declares a
   alguien nuevo. Lo que ya avanzaste no se pierde; solo queda pendiente
   confirmar la persona.
5. Si el destinatario tiene saldo a favor y pagó algo al mensajero en
   efectivo, hay un campo para registrar ese pago ahí mismo.

**Importante:** si alguna vez el sistema no te deja terminar de recibir un
paquete, no es un error — significa que falta confirmar a qué residente
real corresponde. Recién ahí se dispara la notificación al residente.

> **Ejemplo:** llega un paquete a nombre de "Carla Gómez" con destino
> Torre 5 - 302 (nadie lo anunció antes, lo trae el mensajero directo).
> Abrís Recibir y asignás la unidad — pero esa Torre 5 - 302 ya tiene a
> Angélica y Daniel como residentes reales, y "Carla Gómez" no coincide
> con ninguno. El sistema te deja en el mismo modal, mostrando
> `[Angélica Ramírez, Daniel Ramírez, + Nuevo residente]` para que
> confirmes a cuál de ellos corresponde en realidad.

---

## 4. Entregar un paquete

Botón **Entregar**, en cualquier paquete que esté Recibido.

1. El cobro (servicio + bodegaje acumulado) lo calcula siempre el sistema,
   con las tarifas vigentes — nunca confía en un monto que venga de otro
   lado.
2. Si es la primera vez que se le cobra a ese teléfono, el servicio se
   exonera solo.
3. **Anular cobro**: exonera el Servicio, pero te va a pedir elegir un
   **motivo del catálogo**. El **bodegaje nunca se exonera**, aunque
   anules — es un costo real de almacenamiento, no negociable desde acá.
4. Si el destinatario te debe (saldo contra entrega negativo), hay un
   campo opcional para registrar cuánto pagó en este mismo momento — si lo
   dejás vacío, la entrega ocurre igual y la deuda queda pendiente.

La entrega, el cobro y el ajuste de saldo (si aplica) quedan registrados
todos juntos, en el mismo paso — nunca vas a terminar con la entrega hecha
pero el cobro sin registrar.

> **Ejemplo:** el paquete de Angélica lleva 3 días en bodega antes de que
> lo retire. Con tarifa vigente de $2.000/día de bodegaje + $1.500 de
> servicio, el sistema calcula $6.000 + $1.500 = **$7.500**. Si es la
> primera vez que se le cobra a su teléfono, el servicio se exonera solo
> ($6.000 total). Si en cambio el retraso fue culpa de portería y anulás
> el cobro con motivo "Demora imputable a portería", el Servicio ($1.500)
> se exonera igual — pero el bodegaje ($6.000) se cobra de todos modos.

---

## 5. Cancelar un paquete

Botón **Cancelar**, disponible en Anunciado o Recibido. Te pide un motivo
del catálogo; **Otro** es la única opción que no depende de esa lista — te
deja escribir el motivo real a mano.

> **Ejemplo:** Angélica anuncia un paquete por error, dos veces seguidas
> por un doble clic. Cancelás el duplicado con el motivo del catálogo
> "Duplicado". Si el motivo real no está en la lista (ej. "era para el
> apartamento vecino"), elegís **Otro** y escribís esa frase — queda
> guardada tal cual, no como el texto genérico "Otro".

---

## 6. Resolver quién es el destinatario

Esta es la parte que más cuesta al principio, porque tres botones
distintos —**Asignar apartamento**, **Corregir destinatario**, y el paso
opcional dentro de **Recibir**— terminan resolviendo lo mismo, con la
misma lógica de fondo. Vale la pena entenderla una vez; sirve para los
tres.

### La idea de fondo

Un paquete puede tener **una unidad asignada** (Torre + Apartamento) y,
aparte, **un destinatario confirmado** (qué persona real de esa unidad lo
recibe). El sistema nunca deja que un paquete quede mostrando una unidad
"de adorno" sin nadie real detrás — si eso llegara a pasar, un ícono en la
fila te avisa que falta ese paso, y no te deja recibir de verdad hasta
resolverlo.

### Asignar apartamento

Un ícono aparte en la fila, para paquetes sin unidad todavía — sirve para
poner Torre y Apartamento **sin** recibir el paquete a la vez.

1. Elegí Torre y Apartamento.
2. Si ya sabés a quién corresponde, podés completar "+ Nuevo residente"
   ahí mismo (nombre + contacto) — así te ahorrás un segundo viaje a
   Corregir.
3. Si dejás ese paso vacío y la unidad ya tiene residentes reales sin que
   ninguno calce con el destinatario, el sistema te lleva directo a
   Corregir destinatario, ya con los candidatos listos.

> **Ejemplo:** un paquete llega sin unidad asignada, a nombre de "C.
> Pérez". Asignás Torre 5 - Apto 302 y dejás "+ Nuevo residente" vacío
> (no sabés si es Angélica, Daniel, o alguien nuevo). Como esa unidad ya
> tiene residentes reales y "C. Pérez" no coincide con ninguno, el sistema
> te lleva directo a Corregir destinatario, ya con
> `[Angélica Ramírez, Daniel Ramírez]` listos para elegir.

### Corregir destinatario

Botón **Modificar**, en cualquier fila de Anunciado o Recibido.

- Si la unidad **ya tiene** residentes reales, tenés que elegir a uno de
  la lista — el formulario deja de aceptar texto libre. Si hace falta,
  abrís "+ Nuevo residente" para declarar a alguien que todavía no está
  registrado ahí.
- Si el paquete **no tiene** unidad resuelta todavía, sigue aceptando
  nombre y teléfono en texto libre, como siempre.
- Si la persona que elegís ya vive en **otra** unidad, te aparece la
  opción de **mudarla** ahí mismo en vez de crear un registro duplicado —
  incluso si es la Principal de esa otra unidad.

> **Ejemplo:** Carlos Pérez se mudó de Torre 2 - 105 a Torre 5 - 302, pero
> el sistema todavía lo tiene registrado en la unidad vieja. Llega un
> paquete a su nombre con destino Torre 5 - 302; al escribir su contacto
> en "+ Nuevo residente", el sistema detecta el conflicto y te ofrece el
> checkbox **"Mudar residente a Torre 5 - 302"** en vez de bloquear el
> formulario — lo marcás, y Carlos queda vinculado a la unidad nueva en el
> mismo paso.

### Promover a principal

Si el candidato con el que querés seguir es Principal de **otra** unidad,
mudarlo requiere primero liberar ese rol ahí. El mismo modal te ofrece un
atajo: **Promover a otro residente** de esa unidad como su nuevo
Principal, sin salir de Corregir ni de Recibir — un clic y listo, y volvés
al modal de origen con el contacto ya cargado.

> **Ejemplo:** si Carlos Pérez fuera el **Principal** de Torre 2 - 105 (no
> secundario, como en el ejemplo anterior), el checkbox de "mudar" no
> alcanza mientras siga siendo Principal ahí. El modal te muestra el atajo
> **Promover a otro residente** — elegís a otro ocupante de la 105 para
> que pase a ser el nuevo Principal, y volvés automáticamente a Corregir
> con el contacto de Carlos ya cargado, listo para completar la mudanza.

---

## 7. Anunciar un paquete por lote (`/announce`)

La otra forma de dar de alta un paquete, además del formulario público —
la usás cuando alguien llama o llega a portería avisando que espera algo.

Un único campo de texto se encarga de detectar qué escribiste:

| Empieza con | Se interpreta como |
|---|---|
| `3` + 10 dígitos | Teléfono |
| `0` o `1` + solo dígitos | Torre y Apartamento (los primeros 2 dígitos son la Torre) |
| Una letra (mínimo 3 caracteres) | Usuario de WhatsApp |

Según lo que resuelva, hay tres caminos:

1. **Teléfono o WhatsApp directo** — esa persona es anunciante y
   destinatario al mismo tiempo. Si vive con otros residentes, el sistema
   no asume que el paquete es para ella sola: te muestra la unidad
   completa para que confirmes para quién es.
2. **Un residente ya existente** de una unidad — elegís Torre y
   Apartamento, y después a la persona de la lista.
3. **Un residente nuevo** dentro de una unidad — Torre, Apartamento,
   nombre y contacto opcional. Queda dado de alta y el paquete se anuncia
   en el mismo paso.

En los tres caminos tenés **dos botones**: **Anunciar** (como siempre) y
**Recibir** (hace lo mismo, pero además te abre de una vez el modal de
Recibir sobre ese paquete recién creado). El botón Recibir solo aparece si
la persona ya autorizó recepción automática; si no, en su lugar ves un
link de WhatsApp para pedirle esa autorización.

> **Ejemplos, los tres caminos:**
> - Escribís `3011234567` (teléfono de Angélica) → como ella vive con
>   Daniel, el sistema te muestra la unidad completa con "Angélica Ramírez
>   (Anunciante)" ya marcada, para que confirmes si es para ella o para él.
> - Escribís `05302` (Torre 05 + Apto 302, sin saber quién llama) → te
>   lista directo a `[Angélica Ramírez, Daniel Ramírez]` para elegir.
> - Escribís `05302` y abrís "+ Nuevo residente" con "Valentina Ramírez"
>   (una hija que se acaba de mudar ahí) → queda dada de alta y el
>   paquete se anuncia para ella en el mismo paso.
>
> En cualquiera de los tres, si hacés clic en **Recibir** en vez de
> **Anunciar** y la persona ya autorizó recepción automática, el modal de
> Recibir se abre de inmediato.

---

## 8. Residentes — buscar (`/residentes`)

Cuatro formas de mirar el padrón, combinables con el buscador de texto:

| Vista | Qué muestra |
|---|---|
| (sin filtro) | Todos los residentes activos, paginado. También avisa si hay huecos de datos que vale la pena revisar. |
| **Principales** | Solo quienes son Principal de su unidad. |
| **Agrupar por apartamento** | Los resultados organizados por Torre/Apartamento en vez de en lista plana. Si escribís un número exacto (ej. `apt102`), te muestra ese número repetido en las **10 torres** del conjunto, para comparar de un vistazo quién vive en cada una. |
| **Sin apartamento asignado** | Residentes que todavía no tienen unidad en el sistema. |

El buscador acepta nombre, teléfono, email, WhatsApp, Torre/Apartamento —
igual de flexible que el de Paquetes.

> **Ejemplo:** querés comparar quién vive en el apartamento 302 de cada
> torre del conjunto. Activás **Agrupar por apartamento** y escribís
> `apt302` — el sistema te muestra las 10 torres una al lado de la otra,
> cada una con su 302 (con gente, o vacío si nadie vive ahí todavía).

---

## 9. La ficha de un residente

Cuatro pestañas, cada una con su función.

### Tab Datos

Nombre, email, WhatsApp y teléfono. Cosas para tener presentes:
- El **teléfono nunca se puede dejar vacío** una vez tiene un valor — solo
  se reemplaza por otro, ni siquiera si queda WhatsApp de respaldo.
- El checkbox **"Autoriza recepción automática"** es el mismo que habilita
  el botón "Recibir" directo en Anunciar — desactivarlo acá tiene efecto
  inmediato ahí.
- Guardar es todo o nada: si un campo falla la validación, no se guarda
  ninguno de los cambios de ese envío.

> **Ejemplo:** en la ficha de Angélica intentás borrar el teléfono
> `3011234567` dejando el campo vacío para "empezar de cero" — el sistema
> lo rechaza, incluso si ella tiene WhatsApp de respaldo. Lo correcto es
> escribir el número nuevo directo encima del viejo.

### Tab Dirección

Asignar, mover o desvincular la Torre y Apartamento de este residente —
la única vía para tocar ese dato, ahora que el residente ya no puede
hacerlo por su cuenta. Como staff, **podés asignar a una unidad que ya
tiene gente** sin que nada te lo impida. Si la persona ya vive en otra
unidad, marcás "mudar de la otra unidad" para confirmarlo.

> **Ejemplo:** en vez de resolverlo desde Corregir destinatario de un
> paquete puntual ([bloque 6](#6-resolver-quién-es-el-destinatario)),
> podés hacer la misma mudanza de Carlos Pérez directo desde su ficha —
> tab Dirección, elegís Torre 5 - 302, y como ya vive en Torre 2 - 105,
> marcás "mudar de la otra unidad" para confirmar. Mismo resultado, dos
> caminos distintos según desde dónde arranques.

### Tab Notificaciones

Una matriz de casillas: canal (SMS, WhatsApp, Email, Llamada) por estado
del paquete (Anunciado, Recibido, Entregado, Cancelado). La columna
**Llamada** todavía no tiene proveedor conectado, así que aparece pero no
se puede tocar. Como Operador, solo podés prender o apagar **SMS en
Anunciado** — el resto queda bloqueado para vos; un Administrador controla
la matriz completa.

> **Ejemplo:** como Operador, en la ficha de Angélica podés marcar o
> desmarcar el SMS de Anunciado. Si intentás tocar el SMS de Entregado o
> el WhatsApp de Cancelado, esos checkboxes van a estar bloqueados — hace
> falta que un Administrador entre a esa misma ficha para activarlos.

### Tab Residentes (ocupantes de la unidad)

Acá gestionás quién vive en la unidad de este residente:
- **Agregar residente**: nombre + contacto opcional. Hasta **10 personas
  activas** por unidad.
- **Asociar teléfono/WhatsApp** a alguien que todavía no tiene contacto
  propio, o editarlo si ya lo tiene.
- **Dar de baja**: como staff, **podés dar de baja al Principal** aunque
  queden otros activos — el sistema promueve automáticamente al más
  antiguo de los que quedan con contacto propio.
- **Confirmar**: un ocupante nuevo declarado desde Anunciar nace
  "pendiente" — confirmarlo lo vuelve activo.
- **Promover a principal**: pasa el rol a cualquier otro activo de la
  unidad.

> **Ejemplo:** Daniel Ramírez (el hijo de Angélica) todavía no tiene
> teléfono propio en el sistema. Desde la tab Residentes, le das
> **Asociar teléfono** y le cargás un número — a partir de ahí puede
> recibir notificaciones directo, no solo a través de su madre.

---

## 10. Baja administrativa, reactivar, bloquear, liberar bloqueo

Todas estas acciones viven en la ficha del residente, y cualquier rol de
staff las puede usar, salvo donde se indique lo contrario:

- **Baja administrativa** / **Reactivar** — reversible, no toca ningún
  dato personal. Al dar de baja, se desvincula primero al ocupante activo
  (promoviendo a un sucesor si corresponde). Reactivar **no** reconecta a
  nadie automáticamente — eso queda a tu criterio, aparte.
- **Bloquear** — te pide un motivo del catálogo. Reversible, no toca
  paquetes existentes.
- **Liberar bloqueo** — lo destrabás vos directamente, sin esperar a que
  el propio residente entre por su cuenta y acepte los Términos — para
  cuando alguien no puede o no quiere hacerlo solo.
- **Autorizar desbloqueo** (**exclusivo de Administrador**) — habilita que
  un residente bloqueado pueda **reintentar** el login; no restaura el
  servicio de paquetes por sí solo, es un paso distinto de "Liberar
  bloqueo".

**Eliminar** residente (borrado real) también vive acá, pero es
**exclusivo de Administrador** — lo vas a ver en la ficha, pero el botón
no funciona para tu rol. Todo el detalle está en la
[Guía de Administrador](03-staff-admin.md).

> **Ejemplo:** Angélica avisa que se va del conjunto por 6 meses y pide
> pausar el servicio sin perder sus datos — le das **Baja
> administrativa**; el sistema desvincula su ocupante activo (promoviendo
> a Daniel si tiene contacto propio) y ella queda inactiva pero
> recuperable. Cuando vuelva, **Reactivar** la restaura. Caso distinto: un
> residente reporta que alguien más está usando su código de acceso para
> reclamar paquetes — ahí **Bloquear**, con motivo "Sospecha de uso
> indebido".

---

## 11. Saldos contra entrega

Plata que queda a favor o en contra de un residente por cobros contra
entrega que no se saldaron en el momento.

- Hay una **vista global** de saldos y otra de movimientos, para revisar
  el estado general sin ir ficha por ficha.
- Desde la **ficha** de un residente podés registrar un movimiento manual
  en cualquier momento (depósito, o recuperación de deuda) — siempre como
  **monto positivo**. El único movimiento negativo automático es el pago
  al mensajero que se descuenta durante **Recibir**
  ([bloque 3](#3-recibir-un-paquete)).
- El saldo también aparece, de solo lectura, dentro del modal
  **Entregar** ([bloque 4](#4-entregar-un-paquete)) para saldarlo en el
  mismo momento de la entrega.

> **Ejemplo:** Angélica te paga $10.000 en efectivo en portería,
> adelantado para su próximo cobro contra entrega. Desde su ficha,
> registrás el movimiento como **+$10.000**. Meses después, cuando reciba
> un paquete y el mensajero le cobre de más, esos $10.000 (o parte) se
> descuentan solos durante Recibir — no hace falta que lo registres de
> nuevo a mano.

---

## 12. Consultar en modo staff (vista híbrida)

Es la misma pantalla que cualquier visitante usa para rastrear un paquete
por código de acceso o guía — pero si tenés sesión de staff abierta en el
mismo navegador, se ve distinta: aparecen los mismos botones **Recibir** y
**Entregar** que ya conocés de la bandeja, sobre ese paquete puntual, sin
tener que ir a buscarlo. Útil cuando alguien llega directo con su código
en la mano — resolvés todo en la misma pantalla. Las mismas reglas de los
bloques [3](#3-recibir-un-paquete) y [4](#4-entregar-un-paquete) aplican
acá tal cual.

> **Ejemplo:** Angélica se presenta en portería con el código `AB4X9K`
> que le llegó por WhatsApp. En vez de ir a la bandeja a buscarlo, entrás
> a Consultar, pegás el código, y como tenés sesión de staff abierta ves
> el mismo botón **Entregar** que verías en la bandeja — lo usás ahí
> mismo, sin cambiar de pantalla.

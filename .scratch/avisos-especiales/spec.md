# Avisos especiales: avisar a los clientes de los días sin servicio

Fuente: pedido de Jesús, 2026-10-11 (`.scratch/pendientes-cliente/issues/446-vista-mensaje-especial-dias-sin-servicio.md`).
El diseño se acordó con `grilling` en la misma sesión; las 13 decisiones están en ese issue.

**Status:** ready-for-agent

## Problem Statement

Hay días en que la papelería Papyrus no presta el servicio de paquetes: fines de semana, festivos o cierres puntuales.
Hoy no hay forma de avisarles a los clientes que tienen algo pendiente (un Paquete Anunciado hace poco o uno Recibido
que todavía no han retirado). El Admin tendría que armar la lista a mano mirando `/paquetes`, buscar el teléfono de
cada uno y escribir el mismo mensaje una y otra vez por fuera de PAQUETEX. Además, no queda rastro de a quién ya se le
avisó ni cuándo, así que es fácil escribirle dos veces a la misma persona o saturarla de mensajes.

## Solution

Una vista nueva, **Avisos especiales**, solo para Admin y con entrada desde el menú de cuenta. La vista lista **un
cliente por fila**: cada Persona con al menos un Paquete Anunciado en los últimos 5 días calendario (hora de Colombia)
o Recibido (sin importar la fecha). En cada fila aparecen sus paquetes resumidos (códigos con el color del Estado).

Arriba de la lista hay un selector para elegir uno de los **mensajes especiales guardados** ("Fin de semana",
"Festivo"…), con una vista previa. Cada fila tiene dos acciones:

- **Enviar SMS**: envía ese mensaje solo cuando el Admin toca el botón, por la misma cadena de proveedores que los
  avisos automáticos (AWS SNS primero). La página no se recarga.
- **WhatsApp**: un enlace que abre el chat con el mismo texto ya escrito.

Cada fila muestra **"Último SMS: <nombre del mensaje> · <fecha y hora>"**, el último aviso especial enviado por SMS a
ese cliente. Es solo informativo: no bloquea ni pide confirmación para reenviar. El SMS respeta las mismas reglas que
los avisos automáticos (baja administrativa, preferencias SMS, sin teléfono): si no aplica, el botón queda apagado con
el motivo visible, y el WhatsApp sigue disponible.

Los mensajes especiales se crean, editan y eliminan en `/administracion/notificaciones`, en una sección nueva
"Mensajes especiales". Cada uno tiene nombre y un solo texto para SMS y WhatsApp, con `{nombre}` y `{codigos}` como
únicas variables, historial de cambios y vista previa con conteo de caracteres (160 = 1 SMS).

## User Stories

### Acceso y navegación

1. Como Admin, quiero un enlace "Avisos especiales" en el menú de cuenta, para llegar a la vista sin escribir la URL.
2. Como Admin, quiero que solo los Admin vean ese enlace y puedan abrir la vista, para que el Staff no mande avisos
   masivos por su cuenta.
3. Como Staff (no Admin), si abro la URL de la vista directamente, quiero recibir el mismo rechazo que en cualquier
   otra pantalla de administración, para que la restricción no dependa de ocultar un enlace.
4. Como visitante sin sesión, si abro la URL, quiero que me lleve a ingresar, igual que el resto de pantallas de
   staff.

### Quiénes aparecen en la lista

5. Como Admin, quiero ver solo a los clientes que tienen algo pendiente con Papyrus (Anunciados recientes o
   Recibidos), para avisar únicamente a quienes el cierre les afecta.
6. Como Admin, quiero que un Paquete Anunciado cuente solo si se anunció hoy o en los 4 días calendario anteriores
   (hora de Colombia), para no avisar por anuncios viejos que probablemente nunca llegaron.
7. Como Admin, quiero que el corte de los 5 días use la fecha calendario y no horas exactas, para que la lista no
   cambie según la hora a la que abro la vista.
8. Como Admin, quiero que todos los Paquetes Recibidos cuenten sin importar cuándo llegaron, porque todos esperan ser
   retirados.
9. Como Admin, quiero que los Paquetes Entregados o Cancelados nunca hagan aparecer a un cliente, porque ya no tiene
   nada pendiente.
10. Como Admin, quiero ver una sola fila por cliente aunque tenga varios paquetes pendientes, para mandarle un solo
    aviso y no saturarlo.
11. Como Admin, quiero que cada fila corresponda a la misma Persona a la que hoy le llegarían los avisos automáticos de
    esos paquetes (el Destinatario alcanzable, o si no, el Anunciante), para que el aviso especial llegue a quien de
    verdad lo debe recibir.
12. Como Admin, quiero que un paquete cuyo destinatario no se puede resolver a ninguna Persona viva aparezca de todos
    modos en la fila de quien lo anunció, o si no hay nadie alcanzable, que no aparezca, para no ver filas sin a quién
    escribirle.

### Cómo se ve cada fila

13. Como Admin, quiero ver en cada fila el nombre del cliente y su Torre/Apartamento si lo tiene, para reconocerlo de
    un vistazo.
14. Como Admin, quiero ver los códigos de sus paquetes pendientes con el color de su Estado (como en `/paquetes`), para
    saber qué tiene por retirar.
15. Como Admin, quiero poder abrir cada código en `/consultar`, igual que en `/paquetes`, para revisar un paquete
    puntual sin salir del flujo.
16. Como Admin, quiero ver "Último SMS: <nombre del mensaje> · <fecha y hora>" en cada fila, para saber si ya le
    escribí hace poco y con cuál aviso.
17. Como Admin, quiero que el último SMS cuente cualquier mensaje especial (no solo el elegido en el selector), porque
    lo que satura al cliente es cuántos SMS recibe, no de qué tipo.
18. Como Admin, si al cliente nunca se le ha enviado un aviso especial, quiero ver "Sin avisos enviados" (o un texto
    equivalente), y no un espacio vacío ambiguo.
19. Como Admin, quiero que la fecha y hora del último SMS se muestren en hora de Colombia y en formato amigable, igual
    que el resto de la app.
20. Como Admin, quiero que la lista tenga el mismo look de filas-tarjeta que `/paquetes` en escritorio (issue 445), y
    tarjetas en celular, para que la vista se sienta parte de la app.

### Búsqueda y filtros

21. Como Admin, quiero buscar por nombre, teléfono, código o Torre/Apartamento, para encontrar a un cliente puntual en
    una lista larga.
22. Como Admin, quiero filtrar por Anunciado o Recibido, para avisar primero a un grupo (por ejemplo, solo a quienes
    tienen algo Recibido).
23. Como Admin, quiero que un cliente con paquetes de los dos estados aparezca en los dos filtros, para no perderlo.
24. Como Admin, quiero ver cuántos clientes hay en la lista (en total y por filtro), para dimensionar el envío.

### Selección del mensaje

25. Como Admin, quiero un selector arriba de la lista con los mensajes especiales guardados, para elegir una vez cuál
    se manda.
26. Como Admin, quiero ver la vista previa del mensaje elegido (con datos de ejemplo en `{nombre}` y `{codigos}`) y su
    número de caracteres, para revisar lo que va a llegar antes de enviar.
27. Como Admin, quiero que todos los botones SMS y WhatsApp de la lista usen el mensaje elegido, para no mezclar
    avisos por error.
28. Como Admin, quiero que la vista recuerde el mensaje elegido mientras trabajo (al buscar, filtrar o cambiar de
    página), para no tener que elegirlo de nuevo.
29. Como Admin, si no hay ningún mensaje especial creado, quiero ver un aviso con un enlace a "Mensajes especiales" en
    Notificaciones, con los botones de envío apagados, para saber qué falta.

### Enviar por SMS

30. Como Admin, quiero un botón "Enviar SMS" en cada fila que mande el mensaje elegido a ese cliente solo cuando lo
    toco, para que nunca salga un aviso sin mi intención.
31. Como Admin, quiero que el SMS lleve el texto del mensaje con `{nombre}` reemplazado por el nombre del cliente y
    `{codigos}` por los códigos de sus paquetes pendientes en la lista, para que lea como dirigido a él.
32. Como Admin, quiero que el SMS salga por la misma cadena de proveedores que los avisos automáticos (AWS SNS primero,
    con los respaldos configurados en Proveedores), para no mantener otra vía de envío.
33. Como Admin, quiero que al tocar el botón la página no se recargue: el botón muestra "Enviando…" y al terminar la
    fila se actualiza con el nuevo "Último SMS", para seguir avisando cliente por cliente sin perder mi lugar.
34. Como Admin, si el envío falla (ningún proveedor lo entrega), quiero un aviso rojo en esa fila ("No se pudo enviar
    el SMS"), para saber que no llegó.
35. Como Admin, quiero que un envío fallido no cambie el "Último SMS", para que esa fecha siempre corresponda a un SMS
    que sí salió.
36. Como Admin, quiero poder reenviar a un cliente aunque ya se le haya enviado hace poco, sin confirmación ni bloqueo,
    porque a veces cambia el aviso (por ejemplo, se agrega el lunes al cierre del sábado).
37. Como Admin, quiero que cada SMS de aviso especial (exitoso o fallido) quede en el registro de envíos SMS, para que
    el Dashboard lo cuente en el uso y costo de SMS.
38. Como Admin, quiero que el registro sepa que fue un aviso especial (y no un aviso de Paquete ni un OTP), para que
    las cuentas del Dashboard no se mezclen sin poder distinguirlas.
39. Como Admin, quiero que el SMS respete el texto sin tildes y la normalización que ya aplican los SMS de la app, para
    que llegue legible y en la menor cantidad de segmentos.
40. Como Admin, si el mensaje elegido fue eliminado por otro Admin mientras tenía la vista abierta, quiero un error
    claro al intentar enviar, y no un SMS con un texto que ya no existe.

### Reglas de a quién se le puede enviar SMS

41. Como Admin, quiero que un cliente en baja administrativa aparezca con el SMS apagado y el motivo "De baja", porque
    la app no le notifica nada mientras esté de baja.
42. Como Admin, quiero que un cliente sin teléfono (solo usuario de WhatsApp) aparezca con el SMS apagado y el motivo
    "Sin teléfono".
43. Como Admin, quiero que un cliente que desactivó el SMS para el Estado de todos sus paquetes en la lista (Anunciado
    o Recibido, en su matriz de preferencias) aparezca con el SMS apagado y el motivo "Notificaciones SMS
    desactivadas", para respetar lo que él mismo eligió.
44. Como Admin, quiero que si el cliente tiene SMS activo para el Estado de al menos uno de sus paquetes en la lista, el
    botón SMS esté disponible.
45. Como Admin, quiero que esas reglas también se revisen al enviar (no solo al dibujar la lista), para que un envío
    forzado a mano no se las salte.
46. Como Admin, quiero que el botón de WhatsApp siga disponible para clientes con el SMS apagado, siempre que tengan
    teléfono o usuario de WhatsApp, para poder escribirles a mano si de verdad hace falta.
47. Como Admin, quiero que un cliente bloqueado se trate igual que en los avisos automáticos (sin una regla nueva
    inventada para esta vista), para que la app se comporte igual en todas las pantallas.

### Enviar por WhatsApp

48. Como Admin, quiero un botón de WhatsApp en cada fila que abra el chat del cliente con el mensaje elegido ya escrito
    (con `{nombre}` y `{codigos}` resueltos), para enviarlo yo desde WhatsApp.
49. Como Admin, quiero que el enlace de WhatsApp use los mismos enlaces que el resto de la app (celular y escritorio),
    para que abra la app instalada como ya lo hace hoy.
50. Como Admin, quiero que tocar el botón de WhatsApp no cambie el "Último SMS" ni deje registro, porque la app no
    puede saber si de verdad lo envié.
51. Como Admin, quiero que un cliente sin teléfono ni usuario de WhatsApp tenga el botón de WhatsApp apagado, con el
    motivo.

### Administrar los mensajes especiales

52. Como Admin, quiero una sección "Mensajes especiales" en `/administracion/notificaciones`, para crear y mantener
    los avisos en el mismo lugar que el resto de mensajes.
53. Como Admin, quiero crear un mensaje especial con un nombre ("Fin de semana") y un texto, para tenerlo listo para
    la próxima vez.
54. Como Admin, quiero que el nombre sea obligatorio y único, para no confundir dos mensajes en el selector.
55. Como Admin, quiero que el texto sea obligatorio, para no enviar un SMS vacío.
56. Como Admin, quiero poder usar solo `{nombre}` y `{codigos}` en el texto, y que cualquier otra llave entre `{}` se
    rechace al guardar con un mensaje claro, para no enviar placeholders sin resolver.
57. Como Admin, quiero ver mientras escribo una vista previa con datos de ejemplo y el número de caracteres (con aviso
    cuando pase de 160, que equivale a más de 1 SMS), para controlar el costo.
58. Como Admin, quiero editar el nombre o el texto de un mensaje cuando haya información nueva ("este sábado 18…"),
    para reutilizarlo.
59. Como Admin, quiero eliminar un mensaje que ya no sirve, con confirmación, para que no aparezca más en el selector.
60. Como Admin, quiero que eliminar un mensaje no borre el historial de envíos: el "Último SMS" de los clientes sigue
    mostrando el nombre que tenía el mensaje cuando se envió.
61. Como Admin, quiero un historial de cambios de cada mensaje (quién, cuándo, texto anterior y nuevo), como ya lo
    tienen las demás plantillas, para recuperar lo que decía antes.
62. Como Admin, quiero que el mismo texto se use para SMS y WhatsApp, para que el aviso diga lo mismo por los dos
    canales.
63. Como Staff (no Admin), quiero no ver ni poder usar la sección "Mensajes especiales", igual que el resto de
    `/administracion/notificaciones`.

## Implementation Decisions

- **Módulo de dominio nuevo, "avisos especiales"**: un servicio profundo con interfaz pequeña que concentra las reglas,
  para que las rutas solo lo llamen:
  - listar los clientes elegibles para una fecha "hoy" (inyectable para las pruebas), con sus paquetes pendientes,
    teléfono/WhatsApp, Torre/Apartamento, el motivo si el SMS no aplica y su último aviso especial;
  - resolver el texto de un mensaje para un cliente (`{nombre}`, `{codigos}`);
  - enviar el SMS de un mensaje a un cliente con un `NotificationSender` dado, revisando de nuevo la elegibilidad,
    registrando el envío y devolviendo el resultado (éxito con fecha y hora, o falla);
  - crear, editar y eliminar mensajes especiales, con historial.
- **Quién es "el cliente" de un Paquete**: se reusa la resolución de los avisos automáticos (`resolver_destino_notificable`:
  el Destinatario alcanzable, o si no, el Anunciante vivo y con teléfono), agrupando por esa Persona. Los paquetes
  cuyo destino no resuelve a nadie quedan fuera, salvo cuando la identidad tiene solo usuario de WhatsApp: esa fila
  aparece con el SMS apagado ("Sin teléfono") y el WhatsApp disponible. La resolución para ese caso extiende la
  existente sin cambiar el comportamiento de los avisos automáticos.
- **Elegibilidad de Paquetes**: Estado RECIBIDO (cualquier fecha) o ANUNCIADO con fecha de anuncio, convertida a hora de
  Colombia, entre hoy y 4 días calendario atrás. ENTREGADO y CANCELADO nunca entran. Se reusa la conversión de zona
  horaria que ya usa la app (`hora_local`/config del conjunto), sin una zona fija nueva.
- **Regla del SMS** (decisión de esta conversación): el SMS está disponible si la Persona no está en baja
  administrativa, tiene teléfono y tiene el canal SMS activo (`preferencia_activa`) para el Estado (ANUNCIADO o
  RECIBIDO) de al menos uno de sus paquetes en la lista. Si no, el motivo es "De baja", "Sin teléfono" o
  "Notificaciones SMS desactivadas", en ese orden de prioridad. Las mismas reglas se aplican en el envío. No hay regla
  nueva para bloqueados: se comporta igual que los avisos automáticos (hoy el bloqueo no frena notificaciones).
- **Esquema nuevo** (migración Alembic):
  - **MensajeEspecial**: id, nombre (único entre los no eliminados), texto, creado/actualizado, `eliminado_en`
    (eliminación lógica, para que los envíos viejos sigan apuntando a él).
  - **MensajeEspecialHistorial**: append-only, como `PlantillaNotificacionHistorial` (mensaje, usuario, nombre/texto
    anterior y nuevo, fecha). Registra creación, edición y eliminación.
  - **EnvioAvisoEspecial**: append-only, **solo envíos exitosos**: persona, mensaje especial, el **nombre del mensaje
    copiado al momento del envío**, usuario Admin que envió y fecha. El "Último SMS" de una fila es el registro más
    reciente de esa Persona. A propósito no guarda el texto ni el teléfono, igual que `RegistroSms`.
- **Registro de envíos SMS**: valor nuevo `AVISO_ESPECIAL` en `TipoRegistroSms` (sin migración, la columna es
  VARCHAR). Cada intento, exitoso o fallido, se registra con `registrar_envio`. Las tarjetas de SMS del Dashboard que
  hoy suman `AVISO_PAQUETE` pasan a incluir también `AVISO_ESPECIAL` en el uso y el costo.
- **Envío síncrono**: a diferencia de los avisos de Paquete (en segundo plano), el botón espera la respuesta real del
  proveedor, como "Enviar prueba" en Notificaciones, porque el Admin necesita saber si llegó.
- **Interacción sin recarga**: el botón hace un POST por fetch a una ruta de la vista que responde el fragmento de la
  fila actualizado (último SMS, o el aviso de error). Es el mismo patrón de fragmentos HTML que ya usa la búsqueda en
  vivo, sin JSON nuevo. Sin JS, el formulario hace un POST normal y redirige a la vista (Post/Redirect/Get).
- **Texto del SMS**: `{nombre}` es el nombre de la Persona y `{codigos}` son los códigos de acceso de sus paquetes en
  la lista, separados por coma. El texto final pasa por la misma normalización de los SMS de la app (sin tildes). No
  hay otras variables: el guardado rechaza llaves desconocidas, reusando la validación de plantillas existente con
  este conjunto acotado.
- **WhatsApp**: enlaces con `url_whatsapp`/`url_whatsapp_desktop` y `?text=` del mensaje resuelto, igual que "Pedir
  autorización". No hay ruta de servidor ni registro.
- **Selector de mensaje**: va en la URL de la vista (`?mensaje=<id>`) para que se conserve al buscar, filtrar y
  paginar, y la búsqueda en vivo lo arrastra como hoy arrastra los filtros. Sin parámetro, se elige el primero
  alfabéticamente.
- **Vista**: ruta nueva bajo `/administracion/`, protegida con `require_admin`; enlace en el menú de cuenta solo para
  Admin, junto a "Dashboard". Plantilla propia que reusa los componentes de `/paquetes` (filas-tarjeta del issue 445
  en escritorio, tarjetas en celular, búsqueda, filtro por Estado, paginación), sin acoplarse a la plantilla de
  resultados de `/paquetes`.
- **Notificaciones**: `/administracion/notificaciones` gana la sección "Mensajes especiales": lista con nombre y
  extracto, y modales para crear, editar (con vista previa y contador de caracteres) y eliminar (con confirmación),
  siguiendo el patrón de modales de esa misma pantalla y de los catálogos de motivos.
- **Tailwind**: si las plantillas nuevas usan clases que no están en el bundle compilado, hay que recompilar
  `tailwind.css` (las dos salidas) y subir el `?v=`. El repo de despliegue no lo recompila.

## Testing Decisions

- **Una buena prueba** verifica comportamiento externo: lo que el Admin ve en el HTML de la respuesta, lo que el sender
  falso recibió (destino y texto) y lo que quedó en la base (envíos, registro SMS, historial). Nunca nombres de
  funciones internas ni el orden de consultas.
- **Costura principal: HTTP con `TestClient`** (confirmada con Jesús). Las pruebas entran como Admin, siembran Personas
  y Paquetes con los helpers de dominio de siempre y reemplazan `get_notification_sender` por un sender falso que
  registra los envíos o lanza una falla. Prior art: el envío de prueba en `tests/web/test_admin_notificaciones.py`
  (override del sender), los catálogos en `tests/web/test_admin_motivos_cancelacion.py` (CRUD con modales) y la
  lista/filtros de `tests/web/test_packages.py`.
- **Costura secundaria: el servicio de dominio**, solo donde por HTTP la prueba quede incómoda: el corte de 5 días
  calendario en hora de Colombia (con "hoy" inyectado, incluido un anuncio de las 11 p. m. de hace 5 días) y la
  matriz de motivos del SMS (baja, sin teléfono, SMS apagado para uno o todos los Estados). Prior art:
  `tests/data_model` (servicios con sesión real).
- **Qué cubrir**, como mínimo:
  - quién entra y quién no (Anunciado de 4 y de 5 días, Recibido viejo, Entregado, Cancelado);
  - una fila por cliente con varios paquetes;
  - acceso solo Admin;
  - SMS exitoso: el texto resuelto llega al sender, se crea el envío y se registra `AVISO_ESPECIAL`;
  - SMS fallido: aviso de error, sin envío nuevo y con registro fallido;
  - el reenvío no se bloquea;
  - el SMS apagado por cada motivo, y rechazado también en el POST;
  - el enlace de WhatsApp con el texto;
  - CRUD de mensajes con nombre único, variables desconocidas rechazadas e historial;
  - un mensaje eliminado ya no está en el selector, pero su nombre sigue en el "Último SMS".
- **Nombres de archivos de prueba únicos** entre `tests/web`, `tests/data_model` y `tests/browser`: el CI recolecta
  todo en una sola sesión.

## Out of Scope

- Envío masivo ("Enviar a todos los de la lista"): el SMS se manda cliente por cliente, por decisión explícita.
- Bloqueo o confirmación de reenvío por envío reciente: el "Último SMS" es solo informativo.
- Registrar los clics de WhatsApp: no hay forma de saber si el mensaje se envió.
- Envío por WhatsApp desde el servidor (API de WhatsApp Business): no hay proveedor conectado.
- Programar avisos para que salgan solos en una fecha.
- Acceso para Staff no Admin.
- Textos distintos para SMS y WhatsApp, y variables distintas de `{nombre}` y `{codigos}`.
- Avisos por correo electrónico.

## Further Notes

- La regla "SMS activo para el Estado de al menos uno de sus paquetes en la lista" la propuso Claude y Jesús la
  confirmó al revisar las costuras (2026-10-11). Hacía falta porque el aviso especial no es un evento de Paquete y las
  preferencias de SMS son por evento.
- La fecha del "Último SMS" sale del registro propio de envíos de avisos especiales, no de `registros_sms`, que a
  propósito no guarda la Persona ni el teléfono (privacidad). No hay que agregarle esos datos.
- Las rutas de esta vista no deben depender de `/paquetes` (otra pantalla con su propia lógica de filtros y
  agrupación). Se reusan los componentes visuales, no la consulta.

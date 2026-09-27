# Spec — PIN de operador en dispositivos compartidos

Status: ready-for-agent
Feature: pin-operador-dispositivo
Branch: PaqueteXv.2
Depende de: `staff-auth` (sesión de staff, `current_staff`, `sesion_version`), `fotos-multiples-s3` (cola de fotos en segundo plano), `admin-staff` / `personal-crud-staff` (`/administracion/personal`).
Fuente de verdad: grilling del 2026-09-27 (esta conversación) · `CONTEXT.md` ("el actor de cada acción sale de la sesión real")

---

## Problem Statement

Varios Usuarios del staff comparten el mismo equipo (el celular del mostrador o un PC de la papelería Papyrus). Hoy la sesión de staff es una por navegador: el último que entró con usuario y contraseña queda como actor de todo lo que se haga en ese equipo, aunque quien reciba, entregue o cancele sea otra persona. Para que cada movimiento quede a nombre del Usuario que lo hizo, habría que cerrar sesión y volver a entrar con contraseña en cada cambio de turno o de persona, y eso en la práctica no ocurre. Además, un equipo que se queda sin atender sigue abierto con la identidad del último Usuario.

## Solution

Cada Usuario tiene un **PIN** de 4 dígitos, que elige él mismo y que es único en el sistema. Un equipo queda **registrado** para un Usuario cuando este entra una vez con usuario y contraseña. El registro dura 15 días por defecto y es configurable. A partir de ahí, en ese equipo basta con digitar el PIN para convertirse en el **Operador activo**: el Usuario que figura como actor de todo lo que se haga.

Tras 300 s sin interacción (configurable), el equipo se **bloquea**: una capa con el teclado numérico cubre la página y nada se puede hacer hasta que alguien digite su PIN.
- Si desbloquea el mismo Usuario, continúa donde iba.
- Si desbloquea otro, la vista se recarga limpia y todo lo siguiente queda a su nombre.

El bloqueo lo hace cumplir el servidor y funciona igual en celular y en escritorio. Aplica a todos los roles, ADMIN incluido.

## User Stories

1. Como Usuario del staff, quiero entrar por primera vez a un equipo con mi usuario y contraseña, para que ese equipo quede registrado a mi nombre.
2. Como Usuario sin PIN, quiero que el sistema me lleve obligatoriamente a crear mi PIN antes de usar cualquier vista, para no poder operar sin identidad rápida.
3. Como Usuario, quiero elegir mi propio PIN de 4 dígitos, para recordarlo fácilmente.
4. Como Usuario, quiero que el sistema rechace un PIN que ya tiene otro Usuario, para que cada PIN identifique a una sola persona.
5. Como ADMIN, quiero que después de 3 intentos de cambio de PIN rechazados por "ya existe" en una hora no se permitan más intentos, para que nadie pueda recorrer las combinaciones y descubrir los PIN ajenos.
6. Como Usuario, quiero que mi PIN solo funcione en los equipos donde yo entré con contraseña en los últimos días configurados, para que conocer mi PIN no baste para entrar desde otro equipo.
7. Como Usuario registrado en un equipo, quiero desbloquearlo digitando solo mi PIN, sin elegir mi nombre de una lista, para cambiar de persona en segundos.
8. Como Usuario, quiero que la pantalla de bloqueo no muestre quiénes están registrados en el equipo, para no exponer esa información.
9. Como Usuario, quiero ver en la pantalla de bloqueo el nombre del conjunto, el teclado numérico y un enlace "Ingresar con usuario y contraseña", para poder registrar a alguien nuevo en ese equipo.
10. Como Usuario, quiero que en un equipo sin ningún registro vigente se muestre directamente el formulario de usuario y contraseña, para no ver un teclado de PIN que no me sirve.
11. Como Usuario, quiero que el equipo se bloquee solo tras el tiempo de inactividad configurado, para que el siguiente compañero no opere a mi nombre.
12. Como Usuario, quiero que cualquier toque, clic o tecla en la página cuente como actividad, para que no se bloquee mientras escribo en un formulario o abro y cierro modales.
13. Como Usuario, quiero que los procesos automáticos (cola de fotos, reintentos) no cuenten como actividad, para que el equipo se bloquee aunque haya fotos pendientes.
14. Como ADMIN, quiero que el servidor rechace cualquier acción que llegue tras el tiempo de inactividad (más un minuto de margen, porque el navegador avisa de la actividad como máximo una vez por minuto), aunque el navegador falle o se manipule, para que nada quede a nombre equivocado.
15. Como Usuario, quiero que el navegador le avise al servidor de mi actividad local (como máximo una vez por minuto), para que el servidor sepa que sigo trabajando aunque cerrar un modal no genere ninguna petición.
16. Como Usuario, quiero un botón "Bloquear" en el menú, para bloquear el equipo al instante antes de pasárselo a un compañero.
17. Como Usuario, quiero un botón "Salir de este dispositivo" en el menú, para quitar mi registro de ese equipo puntual.
18. Como Usuario que desbloquea el equipo que él mismo dejó bloqueado, quiero seguir exactamente donde iba (la vista, el modal abierto, lo escrito), para no perder trabajo.
19. Como Usuario que desbloquea un equipo que dejó otro Usuario, quiero que la vista se recargue limpia, sin modales ni formularios a medias del anterior, para no firmar sin querer lo que llenó otro.
20. Como Usuario que desbloquea una vista para la que no tengo permiso (por ejemplo, un OPERADOR sobre una vista de administración), quiero llegar al inicio, para no ver un error.
21. Como Usuario, quiero que un guardado rechazado por el bloqueo no se aplique y que pueda repetirlo tras desbloquear yo mismo, para no perder ni duplicar lo que estaba haciendo.
22. Como Usuario, quiero que tras 5 PIN incorrectos seguidos el equipo deje de aceptar PIN y pida usuario y contraseña, para frenar a quien prueba PIN al azar.
23. Como Usuario que entra con contraseña tras esos 5 intentos, quiero que el sistema me lleve a cambiar mi PIN, pudiendo dejar el mismo, para renovarlo si sospecho que lo descubrieron.
24. Como Usuario, quiero que un PIN correcto o un ingreso con contraseña pongan en cero el contador de intentos fallidos del equipo, para que los errores ocasionales no se acumulen.
25. Como ADMIN, quiero ver en `/administracion/personal` un aviso con los últimos bloqueos por intentos fallidos (fecha, hora y equipo), para detectar si alguien está probando PIN.
26. Como Usuario, quiero cambiar mi PIN cuando quiera, confirmando con mi contraseña, para renovarlo si lo compartí o lo olvidé.
27. Como ADMIN, quiero un botón "Cerrar en todos los dispositivos" por cada Usuario en `/administracion/personal`, para cortar su acceso en todos los equipos si se pierde o roban un celular.
28. Como Usuario, quiero el mismo botón "Cerrar en todos los dispositivos" para mí mismo, para cortar mi acceso en todos los equipos sin pedírselo al ADMIN.
29. Como ADMIN, quiero que desactivar a un Usuario o cambiarle la contraseña siga cortando su acceso de inmediato, también por PIN, para que las reglas de hoy se mantengan.
30. Como Usuario, quiero que las fotos en cola sigan subiendo mientras el equipo está bloqueado o lo desbloqueó otra persona, para que ninguna foto se quede sin subir por el cambio de Operador.
31. Como ADMIN, quiero que esa excepción de las fotos solo permita subir fotos a paquetes ya creados y exija que el equipo esté registrado, para que no se convierta en una puerta trasera.
32. Como Usuario con varias pestañas abiertas, quiero que bloquear o desbloquear en una afecte a todas, para que en un equipo haya un solo Operador activo.
33. Como Usuario con varias pestañas abiertas, quiero que la actividad en cualquier pestaña cuente para el mismo tiempo de inactividad, para que no se bloquee una pestaña mientras trabajo en otra.
34. Como Usuario, quiero que cuando otro Usuario desbloquea en una pestaña, las demás se recarguen limpias, para que ninguna conserve la vista a medias del anterior.
35. Como ADMIN, quiero configurar en `/administracion/conjunto` (sección "Seguridad de sesión") el tiempo de bloqueo por inactividad, entre 60 y 3600 s y con 300 s por defecto, para ajustarlo al ritmo del mostrador.
36. Como ADMIN, quiero configurar ahí mismo cuántos días dura el registro de un equipo, entre 1 y 90 días y con 15 por defecto, para equilibrar comodidad y seguridad.
37. Como ADMIN, quiero que los cambios de configuración apliquen de inmediato, sin cerrar ninguna sesión, para no interrumpir a nadie.
38. Como ADMIN, quiero que si acorto la duración del registro, los equipos que ya pasaron el nuevo límite pidan contraseña en su siguiente acción, para que el cambio tenga efecto real.
39. Como ADMIN, quiero que el sistema rechace valores fuera de rango con un mensaje claro, para no dejarlo inusable por error.
40. Como ADMIN, quiero que el día del despliegue se cierren las sesiones abiertas y todos creen su PIN al volver a entrar, para que nadie quede operando sin PIN.
41. Como auditor, quiero que cada Paquete siga registrando como actor al Usuario que desbloqueó con su PIN, para saber quién hizo cada movimiento.
42. Como Usuario, quiero que la experiencia sea igual en celular y en escritorio, para no aprender dos formas de trabajar.
43. Como residente, quiero que mi ingreso por OTP no cambie, porque esta funcionalidad es solo para el staff.

## Implementation Decisions

### Vocabulario nuevo (candidatos al glosario de `CONTEXT.md`)

- **PIN**: 4 dígitos por Usuario, elegido por él, único entre todos los Usuarios. Identifica al Usuario solo en equipos donde está registrado.
- **Dispositivo registrado**: un equipo (navegador) en el que un Usuario entró con contraseña, vigente durante la duración configurada.
- **Operador activo**: el Usuario que desbloqueó el equipo con su PIN y es el actor de todo lo que se hace en él hasta el siguiente bloqueo. Hay uno solo por equipo.
- **Bloqueo**: el estado del equipo después de la inactividad configurada o de "Bloquear". Mientras dura, el servidor rechaza toda acción salvo la subida de fotos en cola.

### Modelo de datos

- **Usuario** suma:
  - la huella del PIN, calculada con HMAC y una llave del servidor. No se usa bcrypt: bcrypt no permite verificar unicidad ni buscar al Usuario por PIN. Es anulable hasta que el Usuario crea el PIN, y tiene índice único.
  - la fecha de creación o cambio del PIN.
  - una versión de registros de dispositivo, con la misma idea que `sesion_version`. Subirla invalida todos sus registros ("Cerrar en todos los dispositivos").
- **Dispositivo** (tabla nueva): identificador aleatorio que viaja en una cookie firmada propia del equipo (distinta de la cookie de sesión), fecha de creación, último uso y contador de intentos de PIN fallidos seguidos.
- **Registro de dispositivo** (tabla nueva): par Dispositivo–Usuario con la fecha del ingreso por contraseña y la versión de registros del Usuario en ese momento. Vigente si no venció la duración configurada, si la versión coincide con la actual del Usuario y si el Usuario está activo. "Salir de este dispositivo" borra el par.
- **Evento de seguridad** (tabla nueva, mínima): bloqueo por intentos fallidos (Dispositivo, fecha y hora) e intentos de cambio de PIN rechazados por "ya existe" (Usuario, fecha y hora; sirven para el límite de 3 por hora).
- **Configuración del conjunto** suma dos campos: segundos de inactividad (60–3600, 300 por defecto) y días de registro del dispositivo (1–90, 15 por defecto).
- Una migración alembic en el árbol de raíz única (ADR-0002).

### Sesión y puerta de acceso

- La sesión de staff (cookie firmada) guarda el Operador activo, el Dispositivo y la marca de última actividad.
- `current_staff` sigue siendo el único punto de entrada para obtener al actor. Además de sus comprobaciones actuales (`activo`, `sesion_version`), exige que el registro Dispositivo–Usuario esté vigente y que la última actividad no pase del tiempo configurado. Si pasó, responde con un rechazo distinguible del 401 de "sin sesión": las peticiones htmx o fetch reciben un código o encabezado que el cliente convierte en la capa de bloqueo, y la navegación normal recibe la pantalla de bloqueo. En ambos casos la acción no se aplica.
- Toda petición aceptada que venga de interacción del Usuario renueva la marca de actividad. Las peticiones automáticas, como la cola de fotos, no la renuevan: se marcan con un encabezado propio.
- Endpoint de aviso de actividad: sin contenido y sin efectos, renueva la marca si el equipo no está bloqueado todavía.
- La cookie de sesión conserva sus 24 h renovables en cada uso. El registro del equipo vive en su propia cookie firmada (un año), y el vencimiento real lo controlan el tiempo de inactividad y la vigencia del registro, leídos de la configuración en cada petición. Una sesión vencida con registro vigente pide PIN, no contraseña (desvío acordado en el ticket 02).
- Se crea una dependencia **`registered_device_staff`** para la subida de fotos en cola: exige solo un registro de dispositivo vigente, no el desbloqueo. Aplica únicamente a la ruta de asociar fotos a un Paquete ya existente.

### Módulo de dominio nuevo: servicio del Operador del dispositivo

Una interfaz pequeña y profunda, sin conocimiento de HTTP:
- `registrar_ingreso(dispositivo, usuario)`: tras verificar la contraseña con el servicio de staff actual, registra el par, pone en cero los intentos y dice si hay que crear o cambiar el PIN.
- `desbloquear(dispositivo, pin)`: devuelve el Usuario o un motivo de rechazo (PIN incorrecto, equipo que exige contraseña). Cuenta los fallos y, al 5.º, deja el equipo en "requiere contraseña" y registra el evento.
- `definir_pin(usuario, pin)`: valida 4 dígitos, verifica unicidad (con límite de 3 rechazos por hora y por Usuario) y permite repetir el mismo PIN.
- `salir_de_dispositivo(dispositivo, usuario)` y `cerrar_en_todos(usuario, actor)`, este último usable por el ADMIN o por el propio Usuario.
- Reloj inyectable a nivel de módulo, igual que `_now()` en el ciclo de vida del Paquete.

### Web

- `/ingresar` conserva usuario y contraseña. Al entrar, registra el equipo y, si falta PIN o viene de los 5 intentos, redirige a la pantalla de crear o cambiar PIN.
- Pantalla o capa de bloqueo: nombre del conjunto, teclado numérico y enlace a usuario y contraseña. En un equipo sin registros vigentes, redirige a `/ingresar`.
- Vista del PIN del propio Usuario (cambiar PIN confirmando la contraseña, y "Cerrar en todos los dispositivos"), enlazada desde el menú de cuenta.
- El menú de cuenta reemplaza el cierre de sesión de staff por "Bloquear" y "Salir de este dispositivo". La salida unificada existente sigue cerrando la sesión de cliente como hoy.
- En `/administracion/personal`, por Usuario: "Cerrar en todos los dispositivos" y un aviso con los últimos bloqueos por intentos fallidos.
- En `/administracion/conjunto`: sección "Seguridad de sesión" con los dos campos y validación de rangos.

### Cliente (plantilla base, JavaScript)

- El contador de inactividad escucha toques, clics y teclas, y avisa al servidor como máximo una vez por minuto mientras haya actividad local.
- Al vencer el tiempo, o al recibir la señal de bloqueo del servidor, muestra la capa de bloqueo sobre la página sin navegar, para que el estado de la página se conserve.
- Al desbloquear: si es el mismo Usuario, quita la capa. Si es otro, recarga la URL actual, y el servidor manda al inicio si no hay permiso.
- Sincronización entre pestañas por un canal del navegador (BroadcastChannel, con respaldo en eventos de `storage`) para bloquear, desbloquear, cambiar de Operador y reiniciar la actividad. El servidor sigue siendo la fuente de verdad.
- La cola de fotos marca sus peticiones como automáticas y no se detiene cuando el equipo está bloqueado.

### Despliegue

- Todas las sesiones de staff abiertas se invalidan al desplegar, con un cambio de llave o subiendo la versión de sesión de todos. En el siguiente ingreso, cada Usuario crea su PIN.
- La llave HMAC del PIN es un secreto nuevo del entorno, independiente de la llave de la cookie de sesión.

## Testing Decisions

- Las pruebas verifican comportamiento observable (respuestas HTTP, qué quedó en la BD, qué ve el Usuario), no detalles internos como el formato de la huella o de la cookie.
- **Costura web (`TestClient`, carpeta `tests/web`), la principal.** Dos clientes HTTP simulan dos equipos, y el reloj del módulo se reemplaza para simular el paso del tiempo. Casos:
  - un primer ingreso sin PIN exige crearlo antes de cualquier vista;
  - PIN repetido rechazado, y el tercer rechazo en una hora bloquea más intentos;
  - un PIN válido en un equipo registrado desbloquea, y en un equipo sin registro de ese Usuario no;
  - 5 fallos llevan a contraseña y luego a cambiar el PIN (aceptando el mismo), y un acierto pone el contador en cero;
  - tras la inactividad configurada, una acción de staff se rechaza con la señal de bloqueo y no se aplica;
  - el aviso de actividad y las peticiones del Usuario renuevan la marca, y las automáticas no;
  - la subida de fotos en cola funciona bloqueada y falla sin registro de dispositivo;
  - "Bloquear", "Salir de este dispositivo" y "Cerrar en todos los dispositivos" (este último por ADMIN y por uno mismo);
  - desactivar un Usuario o cambiarle la contraseña corta también el acceso por PIN;
  - rangos de la configuración, y que un cambio aplique en la siguiente petición;
  - el registro vence al acortar los días;
  - recibir o entregar tras desbloquear con el PIN de otro Usuario deja a ese Usuario como actor del Paquete;
  - el ingreso por OTP del residente no cambia.

  Antecedentes: `test_sesiones_24h.py` (dos equipos y versión de sesión) y `test_auth.py`.
- **Costura de navegador (Playwright, carpeta `tests/browser`, marcador `-m browser`)**, con el reloj del navegador controlado. Casos:
  - la capa de bloqueo aparece al vencer el tiempo;
  - toques y teclas reinician el contador;
  - la misma persona conserva el formulario a medias y otra persona recibe la vista limpia;
  - bloquear y desbloquear se sincronizan entre dos pestañas;
  - la cola de fotos sigue subiendo con la capa visible.

  Antecedente: `test_fotos_cola.py`.
- No hay pruebas unitarias separadas del servicio de dominio: todo su comportamiento se observa desde la costura web.
- Recordatorio del CI: nombres de archivo de prueba que no se repitan entre carpetas.

## Out of Scope

- Una vista de "Dispositivos" con la lista de equipos y su revocación puntual.
- Atribuir cada foto al Usuario que la tomó (hoy las fotos no guardan autor).
- PIN asignado por el sistema, PIN de longitud distinta de 4 o PIN por equipo.
- Un Operador activo distinto por pestaña.
- Cambios en el portal del residente (OTP) o en su sesión.
- MFA para staff.
- Recuperar el PIN por correo o SMS: si se olvida, se entra con contraseña y se cambia.

## Further Notes

- Riesgo aceptado: al exigir unicidad, el rechazo "ese PIN ya existe" confirma que el PIN pertenece a alguien. Se mitiga con el límite de 3 rechazos por hora y con que un PIN solo sirve en equipos donde su dueño está registrado.
- Con 4 dígitos y 5 intentos por equipo antes de pedir contraseña, la probabilidad de acertar al azar el PIN de alguno de los N Usuarios registrados en un equipo es de alrededor de 5·N/10 000 por ciclo.
- La preferencia "Lector" ya es por equipo, no por Usuario. El Dispositivo registrado sigue la misma lógica, pero del lado del servidor.
- Después de implementar, conviene agregar los términos nuevos al glosario de `CONTEXT.md` (PIN, Dispositivo registrado, Operador activo, Bloqueo).

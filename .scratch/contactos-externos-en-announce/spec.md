Status: ready-for-agent
Feature: contactos-externos-en-announce
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (conversación del 2026-09-20) ·
`.scratch/contactos-externos/spec.md` y `.scratch/contactos-externos-import-export/spec.md`
(módulo de Contactos externos: tabla aparte, llaves Teléfono y usuario de WhatsApp) ·
`.scratch/announce-rapido/spec.md` (campo único de `/announce`) · CONTEXT.md (glosario) ·
`docs/adr/0007-persona-telefono-o-whatsapp.md`

---

## Problem Statement

Cuando el Staff (Operador o Admin) anuncia o recibe un paquete desde `/announce`, teclea un Teléfono o
un usuario de WhatsApp en el campo único. Si esa identidad no existe como Persona en la base de
paquetes, la vista responde "No encontramos a nadie con ese dato — regístralo" y el Staff tiene que
**escribir el nombre a mano**, aunque a veces esa misma persona ya está en la base de Contactos
externos (los contactos consolidados desde Google Contacts, la versión 1.0 de producción, WhatsApp,
etc.). Hoy esa información está a un clic de distancia en otra pantalla —que además solo puede ver un
Admin— y el Operador que atiende la portería no la aprovecha: teclea el nombre desde cero, con el
riesgo de errores de tipeo y de nombres distintos para la misma persona.

## Solution

Cuando el dato tecleado en `/announce` **no existe en paquetes** pero **sí coincide, exactamente, con
un Contacto externo**, la vista lo dice con claridad y sugiere ese nombre, con el mismo lenguaje visual
y la misma mecánica que ya usa para elegir a un residente de una unidad:

- Un mensaje: **"Este usuario no registra en el sistema, pero podría ser:"**.
- Una tarjetita con **solo el nombre** del contacto. Un clic/toque la deja seleccionada.
- Al seleccionarla aparece la tarjeta de siempre (con el subtítulo **"Contacto externo"**) con
  **Anunciar** y **Recibir** listos. Anunciar o recibir registra a la Persona con ese nombre y con el
  Teléfono/WhatsApp tecleado, exactamente como si el Staff hubiera escrito el nombre a mano.
- Bajo la tarjetita, **"Nueva persona"** —plegada— permite registrar a alguien con **otro nombre**
  (si la sugerencia no corresponde, por ejemplo porque el número cambió de dueño). Siempre hay una
  salida manual, exista o no el contacto externo.

Si el dato no existe ni en paquetes ni en Contactos externos, la vista se comporta **exactamente igual
que hoy**. La sugerencia es solo de lectura y transparente: no modifica, marca ni enlaza nada en
Contactos externos ni en paquetes, y el Staff sigue decidiendo.

## User Stories

1. Como Operador, quiero que al teclear un Teléfono completo que no existe en paquetes el sistema
   consulte Contactos externos, para no escribir a mano el nombre de alguien que ya se conoce de otra
   fuente.
2. Como Operador, quiero lo mismo al teclear un usuario de WhatsApp, para que las dos identidades de
   la Persona (ADR-0007) se comporten igual.
3. Como Operador, quiero que solo se consulte Contactos externos cuando la Persona **no existe** en
   paquetes, para que la base de paquetes siempre tenga prioridad y nunca se mezcle con datos externos.
4. Como Operador, quiero que una Persona que existe pero está **De baja** o **Bloqueada** se siga
   mostrando como hoy (con sus avisos) y sin sugerencia externa, para no confundir un estado
   administrativo con "no existe".
5. Como Operador, quiero que la coincidencia sea exacta e ignore el formato en que tecleé el dato
   (con o sin +57, espacios, `@` inicial o mayúsculas), para que la sugerencia aparezca sin importar
   cómo lo escriba.
6. Como Operador, quiero ver el mensaje "Este usuario no registra en el sistema, pero podría ser:",
   para tener claro que es un contacto externo y no una Persona registrada.
7. Como Operador, quiero ver una tarjetita solo con el nombre, con el mismo aspecto que la lista de
   residentes de una unidad, para reconocer el patrón de selección que ya uso todos los días.
8. Como Operador, quiero elegir la tarjetita con un clic o toque, para dejar seleccionada a esa
   persona sin escribir nada.
9. Como Operador, quiero que al elegirla aparezca la tarjeta de siempre con el subtítulo "Contacto
   externo" y los botones Anunciar y Recibir listos, para anunciar o recibir sin pasos adicionales.
10. Como Operador, quiero que el mensaje siga visible después de elegir la tarjetita, para no olvidar
    que esa persona todavía no está registrada en el sistema.
11. Como Operador, quiero que Anunciar registre a la Persona con ese nombre y el Teléfono/WhatsApp
    tecleado y cree el Anuncio, para que el resultado sea idéntico a haber escrito el nombre a mano.
12. Como Operador, quiero que Recibir haga lo mismo y además abra el modal de recepción del Paquete
    recién anunciado, para recibir el paquete físico en el mismo acto.
13. Como Operador, quiero que el nombre quede en MAYÚSCULAS y con espacios normalizados, como
    cualquier otro nombre del sistema, para que no haya casing distinto según por dónde entró.
14. Como Operador, quiero tener siempre disponible "Nueva persona" bajo la tarjetita, para registrar a
    alguien con otro nombre cuando la sugerencia no corresponde (por ejemplo, el número cambió de
    dueño).
15. Como Operador, quiero que "Nueva persona" muestre el formulario de siempre (campo Nombre más
    Anunciar y Recibir), para no aprender nada nuevo.
16. Como Operador, quiero que "Nueva persona" empiece plegada cuando hay sugerencia, para que la
    sugerencia sea lo primero que veo, sin ruido.
17. Como Operador, quiero que mientras "Nueva persona" esté abierta no se vea a la vez el par
    Anunciar/Recibir de la tarjeta seleccionada, para no anunciar a nombre equivocado por tener dos
    pares de botones en pantalla.
18. Como Operador, quiero que cuando el dato no existe ni en paquetes ni en Contactos externos vea
    exactamente el formulario actual ("No encontramos a nadie con ese dato — regístralo"), para que el
    flujo de siempre no cambie.
19. Como Operador, quiero que el campo Nombre no me robe el foco mientras sigo escribiendo el
    Teléfono/WhatsApp, para poder terminar de teclear sin interrupciones.
20. Como Operador, quiero que si sigo tecleando y el valor deja de coincidir la sugerencia
    desaparezca, para no anunciar a nombre de alguien por error.
21. Como Operador, quiero que teclear un código Torre+Apto se comporte exactamente como hoy, para que
    la sugerencia no aparezca donde no hay Teléfono ni WhatsApp con qué coincidir.
22. Como Operador, quiero que un Teléfono o WhatsApp incompleto no dispare ninguna consulta ni
    sugerencia, para no ver propuestas a medio teclear.
23. Como Admin, quiero ver la misma sugerencia que el Operador, para trabajar `/announce` de la misma
    forma.
24. Como Operador (rol que no puede abrir la vista de administración de Contactos externos), quiero
    ver la sugerencia, para beneficiarme de ese dato sin necesitar permisos de Admin.
25. Como Admin, quiero que la sugerencia muestre solo el nombre (sin otros teléfonos, usuarios de
    WhatsApp, fuentes ni fechas del contacto), para exponer lo mínimo necesario a quien opera.
26. Como Admin, quiero que usar una sugerencia no modifique, marque ni enlace el Contacto externo,
    para que esa base siga siendo solo de consulta y yo la pueda depurar a mi ritmo, a mano.
27. Como Staff, quiero que si otra persona registra ese Teléfono/WhatsApp mientras miro la sugerencia,
    al elegir la tarjetita no se cree un duplicado ni se use un nombre desactualizado, para mantener
    la unicidad de la identidad de la Persona.
28. Como Staff, quiero que la sugerencia coincida aunque el Contacto externo tenga varios teléfonos o
    usuarios de WhatsApp y yo teclee cualquiera de ellos, para no depender de cuál conozco.
29. Como Staff en celular (el 90% del uso), quiero que el mensaje, la tarjetita y la tarjeta
    seleccionada se vean y se toquen bien en pantalla angosta, para usarlos desde la portería.
30. Como desarrollador, quiero que el cambio no requiera migraciones ni altere las reglas de negocio de
    Persona, Paquete, Ocupante ni Apartamento, para desplegarlo con bajo riesgo.

## Implementation Decisions

- **Consulta de solo lectura en el módulo de Contactos externos.** Una función nueva que recibe el
  valor tecleado y su tipo (Teléfono o usuario de WhatsApp) y devuelve **únicamente el nombre** del
  Contacto externo que coincide, o nada. Normaliza el valor con las mismas reglas canónicas que ya usa
  la importación de Contactos externos (Teléfono canónico; usuario de WhatsApp sin `@` y en
  minúscula), de modo que cualquier formato de entrada coincida con lo guardado. Ambas llaves son
  únicas a nivel de tabla, así que hay como máximo **un** contacto por valor: nunca hay varias
  sugerencias que ordenar o elegir. No expone otros teléfonos, usuarios de WhatsApp, fuentes ni fechas.
- **Punto de integración: la resolución en vivo del campo único principal de `/announce`**, y solo en
  la rama "el valor es un Teléfono completo (10 dígitos) o un usuario de WhatsApp válido, y no existe
  ninguna Persona con esa identidad". "No existe" usa el mismo criterio que la vista ya usa hoy para
  llegar a esa rama: cualquier Persona encontrada (activa, De baja o Bloqueada) sigue por la tarjeta
  actual y **no** dispara consulta externa. Torre+Apto, valores incompletos y campo vacío no cambian.
- **Fragmento con sugerencia** (reemplaza al formulario "No encontramos a nadie" solo cuando hay
  coincidencia externa): (1) el mensaje con el texto exacto pedido por el cliente; (2) la tarjetita del
  nombre, con el mismo aspecto y el mismo comportamiento táctil que los botones de la lista de
  residentes de una unidad; (3) un contenedor donde aparece la tarjeta seleccionada; (4) "Nueva
  persona" plegada, con el mismo patrón nativo de desplegable que ya usa la lista de residentes,
  conteniendo el formulario actual de persona nueva (campo Nombre obligatorio, Anunciar y Recibir), que
  conserva sus garantías actuales (Nombre sin autofocus, porque el fragmento se re-renderiza en cada
  tecleo).
- **Interacción de clic**: el mismo mecanismo delegado que la lista de residentes (el contenedor de
  resultados nunca se reemplaza a sí mismo, solo su contenido). El clic pide al servidor la tarjeta
  seleccionada identificando la sugerencia por **el valor tecleado y su tipo**, nunca por un nombre
  enviado desde el navegador. Esa petición exige sesión de Staff (la misma dependencia que el resto de
  `/announce`) y **vuelve a resolver** en el momento del clic: si la Persona ya existe (se registró
  entre tanto) responde con el estado vigente de esa Persona en vez de la sugerencia; si el Contacto
  externo ya no existe, responde con el formulario actual "No encontramos a nadie". Así nunca se
  registra un duplicado ni se usa un nombre desactualizado.
- **Tarjeta seleccionada**: nombre normalizado, subtítulo "Contacto externo", campos ocultos con la
  identidad tecleada (Teléfono o usuario de WhatsApp) y el nombre a registrar. **Anunciar y Recibir
  presentes ambos y sin la compuerta de autorización por WhatsApp** — la Persona todavía no existe, no
  hay bandera de recepción automática que consultar; el comportamiento debe ser el del formulario
  actual de "persona nueva", **no** el de la tarjeta de un residente ya registrado (que con la bandera
  apagada reemplaza Recibir por un pedido de autorización). El mensaje de la sugerencia permanece
  visible tras la selección. Mientras "Nueva persona" esté abierta, la tarjeta seleccionada se oculta
  (nunca dos pares Anunciar/Recibir a la vez), igual que en la lista de residentes.
- **Registro**: el envío reutiliza **sin cambios** el registro de Anuncio por Teléfono/WhatsApp directo:
  se crea la Persona con ese nombre (canonicalizado a MAYÚSCULAS y espacios colapsados en la frontera
  del dominio, como cualquier nombre) y el Anuncio queda con la misma Persona como Anunciante y como
  Destinatario. Anunciar crea el Paquete en `Anunciado`; Recibir además abre el modal de recepción del
  Paquete recién creado. No cambian las reglas de Persona, Paquete, Ocupante ni Apartamento.
- **El Contacto externo no se toca**: ni se modifica, ni se marca como "usado", ni se enlaza con la
  Persona creada. La sugerencia es puramente informativa.
- **Permisos**: la sugerencia y su selección están disponibles para todo Staff (Operador y Admin),
  aunque la vista de administración de Contactos externos siga siendo exclusiva de Admin. Es una
  decisión explícita del cliente; por eso la sugerencia expone solo el nombre.
- **Sin cambios de esquema, sin migraciones, sin dependencias nuevas.** El costo es una consulta por
  igualdad sobre columnas ya únicas, ejecutada solo en la rama "no existe" y con el debounce que ya
  tiene la resolución en vivo.
- **Textos de interfaz** (verbatim del cliente): "Este usuario no registra en el sistema, pero podría
  ser:" y el subtítulo "Contacto externo". El resto de textos de la vista no cambia.
- **Mobile-first**: la vista es una columna angosta y el 90% del uso es desde celular; el mensaje, la
  tarjetita y la tarjeta seleccionada deben verse y tocarse bien a 360–414 px de ancho.

## Testing Decisions

- **Qué es una buena prueba aquí**: verifica comportamiento externo observable por HTTP (qué fragmento
  devuelve cada ruta, qué campos ocultos y botones trae, qué queda en la base tras el envío), no
  detalles de implementación ni clases de estilo. Las únicas cadenas que se fijan son contratos
  funcionales: el texto exacto del mensaje, el subtítulo "Contacto externo", los nombres de campo
  (`telefono` / `whatsapp_usuario` / `nombre` / `accion`) y la presencia o ausencia de esos elementos.
- **Seam único: las rutas HTTP de `/announce`** — la resolución en vivo (fragmento), la selección de la
  sugerencia y el envío de registro — sobre el Postgres efímero del arnés de pruebas web. La consulta de
  Contactos externos no se prueba por separado: se cubre a través de esas rutas (incluidos los formatos
  de entrada distintos). Los Contactos externos se siembran por la misma vía que usa la importación.
- **Casos a cubrir**: sugerencia por Teléfono y por usuario de WhatsApp; coincidencia con formatos de
  entrada distintos (+57, espacios, `@`, mayúsculas) y con un contacto de varios teléfonos/WhatsApp;
  **no** aparece si la Persona existe (activa, De baja, Bloqueada) aunque el contacto externo exista;
  no aparece si no existe en ninguna base (formulario actual intacto, incluida la presencia de Anunciar
  y Recibir y la ausencia de autofocus); Torre+Apto, valor incompleto y campo vacío no consultan; se
  muestra solo el nombre (no aparecen otros datos del contacto en el HTML); un Operador (no Admin) la
  ve; sin sesión redirige al login; el fragmento con sugerencia trae "Nueva persona" con Nombre,
  Anunciar y Recibir; la tarjeta seleccionada trae Anunciar **y** Recibir con la identidad y el nombre
  ocultos; el envío por Anunciar registra la Persona con el nombre en MAYÚSCULAS y el Teléfono/WhatsApp
  tecleado; el envío por Recibir abre el modal de recepción; el Contacto externo queda intacto (nombre,
  teléfonos, WhatsApps, fuentes y fecha de actualización); si la Persona se registra entre la
  sugerencia y el clic, no se duplica y se muestra su estado vigente.
- **Prior art**: las pruebas web existentes de la resolución en vivo de `/announce` (Persona con match,
  sin match pide nombre, valores incompletos que no disparan nada, formulario de persona nueva con
  Anunciar/Recibir cableados y sin autofocus) y de su envío por Teléfono/WhatsApp directo; para sembrar
  Contactos externos, las pruebas web de su vista de administración. Todas las pruebas existentes deben
  seguir pasando sin modificación.

## Out of Scope

- El formulario "Nueva persona" que vive **dentro de la lista de residentes de una unidad** (su campo
  "Teléfono o WhatsApp" con resolución en vivo): no recibe la sugerencia en esta versión.
- Sugerir por **nombre**, por búsqueda parcial o con varias sugerencias: solo coincidencia exacta de
  Teléfono o usuario de WhatsApp.
- Consultar Contactos externos con un código Torre+Apto (los Contactos externos no tienen dirección).
- Completar a la Persona nueva con los **otros** identificadores del contacto externo (por ejemplo, su
  usuario de WhatsApp cuando se tecleó el Teléfono).
- Enlazar, marcar o "promover" el Contacto externo a la Persona creada, o cualquier estado que registre
  que ya fue usado.
- Mostrar la sugerencia en otras vistas (`/anunciar`, `/paquetes`, `/residentes`).
- Cualquier cambio en la eliminación de residentes.
- La depuración o eliminación de Contactos externos (la hará el cliente a futuro, de forma manual, en
  su propia vista).

## Further Notes

- **Vocabulario**: el mensaje pedido por el cliente dice "usuario" para referirse a una Persona; en el
  glosario, "Usuario" es el Staff. El texto visible se mantiene **tal cual lo pidió el cliente** (es
  copy de interfaz, no vocabulario de dominio); el código, las pruebas y la documentación siguen el
  glosario (Persona, Contacto externo).
- **Calidad del dato**: los nombres de Contactos externos vienen de fuentes heterogéneas (pueden estar
  en minúscula, incompletos o ser apodos). Por eso es una **sugerencia**, no un dato confirmado: el
  Staff decide si la usa o registra a mano con "Nueva persona". Al registrar, el nombre se canonicaliza
  como cualquier otro.
- **Orden de referencia visual**: la selección de la sugerencia reproduce la experiencia de la lista de
  residentes de una unidad (tarjetita → clic → tarjeta con Anunciar/Recibir), incluida su regla de no
  mostrar dos pares de botones a la vez; conviene reutilizar ese patrón en vez de inventar uno nuevo.
- **Trazabilidad**: en un Paquete creado desde una sugerencia el snapshot y el Anunciante quedan como en
  cualquier Anuncio por Teléfono/WhatsApp directo; el origen "contacto externo" no se persiste (ver
  Out of Scope).

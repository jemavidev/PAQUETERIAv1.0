# 02 — Sugerencia por Teléfono: elegir el nombre de un Contacto externo y anunciar o recibir a su nombre (tracer bullet)

**What to build:** cuando el Staff (Operador o Admin) teclea en el campo único de `/announce` un **Teléfono completo** que no existe en paquetes pero sí coincide con un Contacto externo, la vista lo dice y sugiere ese nombre, de punta a punta:

1. Aparece el mensaje **"Este usuario no registra en el sistema, pero podría ser:"** y una **tarjetita solo con el nombre**, con el mismo aspecto y la misma mecánica que la lista de residentes de una unidad. La sugerencia reemplaza al formulario "No encontramos a nadie".
2. Un clic o toque la deja seleccionada y aparece debajo la tarjeta de siempre, con el subtítulo **"Contacto externo"** y **Anunciar y Recibir** listos. El mensaje sigue visible.
3. Anunciar o Recibir registra a la Persona con ese nombre (en MAYÚSCULAS, como cualquier nombre) y el Teléfono tecleado, igual que si el Staff hubiera escrito el nombre a mano: Anunciar crea el Paquete en `Anunciado`; Recibir además abre el modal de recepción.
4. Bajo la tarjetita queda **"Nueva persona" plegada**, con el formulario de persona nuevo de siempre, por si la sugerencia no corresponde y hay que registrar a alguien con otro nombre.

Es solo lectura: no se modifica, marca ni enlaza nada en Contactos externos ni en paquetes, y no hay cambios de esquema. Esta rebanada cubre solo el Teléfono; el usuario de WhatsApp es el ticket 03 y las garantías de robustez el 04.

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 1, 3–16, 18, 21–26, 28 —para Teléfono— y 30).

**Blocked by:** 01 — Extraer el formulario de "persona nueva" a un componente reutilizable.

**Status:** done

- [x] Con un Teléfono completo (10 dígitos, en cualquier formato de entrada: con o sin +57, espacios, guiones) que **no existe en paquetes** y coincide, de forma exacta, con **cualquiera de los teléfonos** de un Contacto externo, se muestra el mensaje con el texto exacto y la tarjetita con el nombre. La sugerencia reemplaza al formulario "No encontramos a nadie".
- [x] La sugerencia expone **solo el nombre**: en el HTML no aparecen los otros teléfonos, usuarios de WhatsApp, fuentes ni fechas del contacto.
- [x] Elegir la tarjetita muestra debajo la tarjeta con el subtítulo "Contacto externo", con **Anunciar y Recibir ambos presentes y sin la compuerta de autorización por WhatsApp** (comportamiento del formulario de persona nueva, no el de la tarjeta de un residente ya registrado), con el Teléfono tecleado y el nombre como datos ocultos. El mensaje sigue visible.
- [x] Anunciar desde esa tarjeta registra la Persona con el nombre en MAYÚSCULAS y espacios normalizados y el Teléfono tecleado, y crea el Paquete en `Anunciado` con esa Persona como Anunciante y Destinatario. Recibir hace lo mismo y además abre el modal de recepción del Paquete recién creado.
- [x] Bajo la tarjetita hay "Nueva persona" **plegada**, con el formulario de persona nueva (Nombre obligatorio, Anunciar y Recibir; sin autofocus), que registra con el nombre que se escriba a mano.
- [x] **No se sugiere ni se consulta** Contactos externos cuando existe una Persona con ese Teléfono —activa, De baja o Bloqueada—, aunque el contacto externo exista: se ve la tarjeta de siempre.
- [x] Si el Teléfono no está en Contactos externos, el fragmento es **idéntico al de hoy**.
- [x] Un código Torre+Apto, un valor incompleto y el campo vacío no consultan ni cambian nada.
- [x] La sugerencia y la ruta que atiende el clic exigen sesión de Staff (sin sesión redirigen al login, como el resto de `/announce`); un **Operador** (no Admin) la ve igual que un Admin.
- [x] Tras usar la sugerencia, el Contacto externo queda **intacto** (nombre, teléfonos, WhatsApps, fuentes y fecha de actualización).
- [x] El cambio no requiere migraciones ni altera las reglas de Persona, Paquete, Ocupante ni Apartamento.
- [x] Pruebas web (rutas HTTP de `/announce`) para cada punto anterior, con los Contactos externos sembrados por la misma vía que usa la importación; las pruebas existentes de `/announce` siguen pasando.
- [x] Verificado a mano en un navegador a ~390 px de ancho: el mensaje, la tarjetita y la tarjeta seleccionada se ven y se tocan bien.
- [x] "Contacto externo" queda definido en el glosario del dominio (contacto consolidado desde fuentes externas, con llaves Teléfono y usuario de WhatsApp, independiente de Persona y Ocupante).

**Notes:** el fragmento de la lista de residentes de una unidad ya oculta la tarjeta seleccionada mientras "Nueva persona" está abierta, con un mecanismo propio del formulario de la vista; conviene reutilizar los mismos ganchos (contenedor de la tarjeta seleccionada y marca del desplegable) en vez de duplicar la lógica. El ticket 04 fija y prueba ese comportamiento.

**Nota (revisión del ticket 01):** el campo Nombre del formulario de persona nueva tiene un `id` fijo; el fragmento con sugerencia debe dibujar UNA sola instancia del formulario (la del desplegable) para no duplicarlo en el DOM. El componente ya permite omitir su aviso ("No encontramos a nadie…"), que aquí no debe repetirse dentro de "Nueva persona".

## Verificación

- 17 pruebas web nuevas (`CODE/tests/web/test_announce_sugerencia_contacto_externo.py`) sobre las rutas de `/announce`, con los Contactos externos sembrados por `importar_contactos_externos`. Las que fijan lo esencial (la sugerencia, el desplegable "Nueva persona", el contenedor y la ruta del clic) se vieron fallar primero. Las de borde (formatos, varios teléfonos, Persona existente en cualquier estado, valores que no consultan) nacieron verdes porque el diseño del primer corte ya las cubría; una mutación —quitar el `persona is None` de la ruta— confirmó que sí fallan cuando deben.
- Suite completa: 1857 pasan. Corrió antes de los ajustes de la revisión; después de ellos pasan los 121 de `/announce` (104 existentes + 17 nuevas) y los de plantillas/layout.
- Navegador a 390 px (iframe de 390 px del mismo origen, sesión de Staff real, contacto ficticio sembrado y luego borrado): el mensaje, la tarjetita (58 px de alto) y la tarjeta seleccionada (Anunciar/Recibir de 48 px) se ven bien y sin scroll horizontal; el mensaje sigue visible al elegir; con "Nueva persona" abierta la tarjeta seleccionada se oculta y queda un solo par de botones, y al cerrarla vuelve; sin autofocus y con una sola instancia del campo Nombre. No se envió ningún formulario en el navegador: el registro está cubierto por las pruebas.
- Sin cambios de esquema, de reglas de Persona/Paquete/Ocupante/Apartamento ni de CSS compilado (todas las clases ya estaban en el bundle).

## Decisiones y notas para los tickets 03 y 04

- La consulta vive en `contacto_externo_sugerencia_service.py`, aparte de `contacto_externo_service.py` (fusión/importación/listado del Admin): su superficie es solo el nombre, que ve todo el Staff.
- Orden del fragmento: mensaje → tarjetita → "Nueva persona" → contenedor de la tarjeta seleccionada, igual que `_identificar_unidad.html` (el spec enumera el contenedor antes del desplegable; se cambia moviendo un bloque si el cliente lo prefiere).
- `components/_persona_resuelta.html` gana el parámetro `nombre_a_registrar`: la Persona todavía no existe, así que Anunciar y Recibir van juntos, sin píldora "Auto" ni link de WhatsApp.
- **Ticket 03:** basta la rama `"whatsapp"` en `sugerir_nombre_de_contacto_externo`; la ruta, las plantillas y el JS ya no dependen del tipo.
- **Ticket 04:** la ruta del clic (`/announce/identificar-sugerencia`) todavía NO re-resuelve la Persona (si se registró entre la sugerencia y el clic mostraría igual la tarjeta "Contacto externo"; `POST /announce` no duplica ni renombra) y responde vacío si el contacto ya no existe. El resumen "Nueva persona" mide 24 px de alto, igual que en la lista de residentes: revisar el área táctil a 360–414 px.
- Revisión (`/code-review`): renombrados función y módulo (`_service`) y las plantillas (cada una calza con su ruta); `None` explícito en la consulta; misma condición para el campo oculto y para Recibir en la tarjeta compartida; glosario recortado a la definición; pruebas más robustas (extractor de `<input>` en vez de regex, aserción de fuentes que ahora sí puede fallar, "solo el nombre" también sobre la tarjeta seleccionada).

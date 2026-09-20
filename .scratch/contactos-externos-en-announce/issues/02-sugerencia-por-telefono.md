# 02 — Sugerencia por Teléfono: elegir el nombre de un Contacto externo y anunciar o recibir a su nombre (tracer bullet)

**What to build:** cuando el Staff (Operador o Admin) teclea en el campo único de `/announce` un **Teléfono completo** que no existe en paquetes pero sí coincide con un Contacto externo, la vista lo dice y sugiere ese nombre, de punta a punta:

1. Aparece el mensaje **"Este usuario no registra en el sistema, pero podría ser:"** y una **tarjetita solo con el nombre**, con el mismo aspecto y la misma mecánica que la lista de residentes de una unidad. La sugerencia reemplaza al formulario "No encontramos a nadie".
2. Un clic o toque la deja seleccionada y aparece debajo la tarjeta de siempre, con el subtítulo **"Contacto externo"** y **Anunciar y Recibir** listos. El mensaje sigue visible.
3. Anunciar o Recibir registra a la Persona con ese nombre (en MAYÚSCULAS, como cualquier nombre) y el Teléfono tecleado, igual que si el Staff hubiera escrito el nombre a mano: Anunciar crea el Paquete en `Anunciado`; Recibir además abre el modal de recepción.
4. Bajo la tarjetita queda **"Nueva persona" plegada**, con el formulario de persona nuevo de siempre, por si la sugerencia no corresponde y hay que registrar a alguien con otro nombre.

Es solo lectura: no se modifica, marca ni enlaza nada en Contactos externos ni en paquetes, y no hay cambios de esquema. Esta rebanada cubre solo el Teléfono; el usuario de WhatsApp es el ticket 03 y las garantías de robustez el 04.

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 1, 3–16, 18, 21–26, 28 —para Teléfono— y 30).

**Blocked by:** 01 — Extraer el formulario de "persona nueva" a un componente reutilizable.

**Status:** ready-for-agent

- [ ] Con un Teléfono completo (10 dígitos, en cualquier formato de entrada: con o sin +57, espacios, guiones) que **no existe en paquetes** y coincide, de forma exacta, con **cualquiera de los teléfonos** de un Contacto externo, se muestra el mensaje con el texto exacto y la tarjetita con el nombre. La sugerencia reemplaza al formulario "No encontramos a nadie".
- [ ] La sugerencia expone **solo el nombre**: en el HTML no aparecen los otros teléfonos, usuarios de WhatsApp, fuentes ni fechas del contacto.
- [ ] Elegir la tarjetita muestra debajo la tarjeta con el subtítulo "Contacto externo", con **Anunciar y Recibir ambos presentes y sin la compuerta de autorización por WhatsApp** (comportamiento del formulario de persona nueva, no el de la tarjeta de un residente ya registrado), con el Teléfono tecleado y el nombre como datos ocultos. El mensaje sigue visible.
- [ ] Anunciar desde esa tarjeta registra la Persona con el nombre en MAYÚSCULAS y espacios normalizados y el Teléfono tecleado, y crea el Paquete en `Anunciado` con esa Persona como Anunciante y Destinatario. Recibir hace lo mismo y además abre el modal de recepción del Paquete recién creado.
- [ ] Bajo la tarjetita hay "Nueva persona" **plegada**, con el formulario de persona nueva (Nombre obligatorio, Anunciar y Recibir; sin autofocus), que registra con el nombre que se escriba a mano.
- [ ] **No se sugiere ni se consulta** Contactos externos cuando existe una Persona con ese Teléfono —activa, De baja o Bloqueada—, aunque el contacto externo exista: se ve la tarjeta de siempre.
- [ ] Si el Teléfono no está en Contactos externos, el fragmento es **idéntico al de hoy**.
- [ ] Un código Torre+Apto, un valor incompleto y el campo vacío no consultan ni cambian nada.
- [ ] La sugerencia y la ruta que atiende el clic exigen sesión de Staff (sin sesión redirigen al login, como el resto de `/announce`); un **Operador** (no Admin) la ve igual que un Admin.
- [ ] Tras usar la sugerencia, el Contacto externo queda **intacto** (nombre, teléfonos, WhatsApps, fuentes y fecha de actualización).
- [ ] El cambio no requiere migraciones ni altera las reglas de Persona, Paquete, Ocupante ni Apartamento.
- [ ] Pruebas web (rutas HTTP de `/announce`) para cada punto anterior, con los Contactos externos sembrados por la misma vía que usa la importación; las pruebas existentes de `/announce` siguen pasando.
- [ ] Verificado a mano en un navegador a ~390 px de ancho: el mensaje, la tarjetita y la tarjeta seleccionada se ven y se tocan bien.
- [ ] "Contacto externo" queda definido en el glosario del dominio (contacto consolidado desde fuentes externas, con llaves Teléfono y usuario de WhatsApp, independiente de Persona y Ocupante).

**Notes:** el fragmento de la lista de residentes de una unidad ya oculta la tarjeta seleccionada mientras "Nueva persona" está abierta, con un mecanismo propio del formulario de la vista; conviene reutilizar los mismos ganchos (contenedor de la tarjeta seleccionada y marca del desplegable) en vez de duplicar la lógica. El ticket 04 fija y prueba ese comportamiento.

**Nota (revisión del ticket 01):** el campo Nombre del formulario de persona nueva tiene un `id` fijo; el fragmento con sugerencia debe dibujar UNA sola instancia del formulario (la del desplegable) para no duplicarlo en el DOM. El componente ya permite omitir su aviso ("No encontramos a nadie…"), que aquí no debe repetirse dentro de "Nueva persona".

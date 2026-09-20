# 04 — Robustez de la sugerencia: vigencia al elegir, un solo par de botones y pantalla angosta

**What to build:** que la sugerencia nunca lleve al Staff a registrar un duplicado, a anunciar con datos viejos ni a ver botones repetidos. Cubre los casos de borde de la experiencia del ticket 02 (y, por extensión, del 03): qué pasa si el estado cambia entre que se muestra la sugerencia y se elige, qué se ve mientras "Nueva persona" está abierta, qué pasa si el Staff sigue tecleando, y que todo se vea bien en el celular (el 90% del uso).

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 17, 19, 20, 27 y 29).

**Blocked by:** 02 — Sugerencia por Teléfono: elegir el nombre de un Contacto externo y anunciar o recibir a su nombre.

**Status:** ready-for-agent

- [ ] **Vigencia al elegir:** al hacer clic en la tarjetita, el servidor vuelve a resolver el valor (identificándolo por el valor tecleado y su tipo, nunca por un nombre enviado desde el navegador). Si entre tanto se registró una Persona con esa identidad, se muestra su estado vigente (la tarjeta de siempre) y **no se crea un duplicado**; si el Contacto externo ya no existe, se muestra el formulario "No encontramos a nadie".
- [ ] **Un solo par de botones:** mientras "Nueva persona" está abierta no se ve a la vez el par Anunciar/Recibir de la tarjeta seleccionada; al cerrarla, vuelve a verse (mismo comportamiento que la lista de residentes de una unidad).
- [ ] **Cambio de valor:** si el Staff sigue tecleando y el valor deja de coincidir, o pasa a otra identidad, la sugerencia y la tarjeta seleccionada desaparecen; nunca queda seleccionada una tarjeta de un valor anterior.
- [ ] **Sin robo de foco:** el campo Nombre de "Nueva persona" no lleva autofocus, para no interrumpir mientras se termina de teclear el Teléfono o WhatsApp.
- [ ] **Pantalla angosta:** el mensaje, la tarjetita, la tarjeta seleccionada y "Nueva persona" se ven y se tocan bien a 360, 390 y 414 px de ancho, sin scroll horizontal (verificado en un navegador).
- [ ] Pruebas web (rutas HTTP de `/announce`) para lo verificable desde el servidor: la vigencia al elegir en sus dos variantes, la ausencia de autofocus y el contrato de marcado del desplegable y del contenedor de la tarjeta seleccionada. Lo que depende de JavaScript (ocultar/mostrar el par de botones, limpiar al cambiar el valor) se verifica en un navegador y queda anotado en el ticket.
- [ ] Las pruebas de los tickets 01, 02 y 03 y las existentes de `/announce` siguen pasando.

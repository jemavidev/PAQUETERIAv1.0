# 09 — /consultar: una guía que coincide con varios paquetes

**What to build:** la búsqueda por término de /consultar (código de acceso o guía) asume "cero o un paquete", y con dos paquetes de la misma guía falla con un error 500 (el envío de varias cajas comparte guía, y en el glosario la Guía es una referencia, no una llave). Con este ticket la búsqueda pasa a "cero, uno o varios": con cero o uno, todo igual que hoy; con varios, el **Staff con sesión** ve la lista de coincidencias para elegir, y el **público sin sesión** ve un mensaje neutro que no muestra datos de nadie, para que una lectura repetida por error no exponga el paquete de otra persona.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 50 a 56).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Con cero coincidencias, /consultar se comporta exactamente como hoy.
- [x] Con un solo paquete (por código de acceso o por guía), se comporta exactamente como hoy, incluidas las acciones de Staff sobre él; las pruebas existentes de /consultar pasan sin modificarse.
- [x] Con varios paquetes con la misma guía y **sesión de Staff**, se muestra una lista con código de acceso, destinatario y estado de cada uno; cada fila lleva al detalle habitual de ese paquete (el mismo que hoy se ve al buscar su código de acceso).
- [x] Con varios paquetes y **sin sesión**, se muestra un mensaje neutro que dice que la guía corresponde a más de un paquete y pide consultar con el código de acceso de cada uno; no aparece ningún dato de ningún paquete (ni nombre, ni estado, ni código, ni cantidad de paquetes con detalle).
- [x] Si el término coincide con el código de acceso de un paquete y, además, con la guía de otro, gana el código de acceso (es único).
- [x] Ninguna combinación de coincidencias produce un error 500, para Staff ni para el público.
- [x] Consultar por código de acceso sigue funcionando igual.
- [x] Pruebas HTTP con dos y con tres paquetes de la misma guía, en los estados `Anunciado`, `Recibido` y `Entregado`, con y sin sesión de Staff.

## Verificación

- Vistas fallar primero (`tests/web/test_search.py`): las 4 pruebas nuevas que producen una coincidencia múltiple
  fallaban (el `.one_or_none()` reventaba con `MultipleResultsFound`); las 2 que ya pasaban fijan lo que no debe
  cambiar (un solo paquete por guía y el detalle por código de acceso). Ahora pasan las 48 de `test_search.py`.
- Cero coincidencias y un solo paquete (por código de acceso o por guía): igual que hoy, incluidas las acciones
  de Staff sobre él; las pruebas existentes de /consultar no se modificaron.
- Varios paquetes con la misma guía, con sesión de Staff: lista con destinatario, código de acceso y estado de
  cada uno (probado con Recibido, Entregado y Cancelado) y un enlace por fila a `/consultar?q=<código>`, que abre
  el detalle habitual de ESE paquete y solo de ese. No muestra los paquetes que no coinciden.
- Varios paquetes, sin sesión: un mensaje neutro ("Esta guía corresponde a más de un paquete. Consulta con el
  código de acceso de cada uno."), sin ningún dato: la prueba comprueba que no aparecen los códigos de acceso, los
  nombres ni el teléfono de ninguno de los tres paquetes.
- Coincidencia mixta: si el término es el código de acceso de un paquete y a la vez la guía de otro, gana el
  código de acceso (es único) y se ve el detalle de ese paquete.
- Sin 500 en ninguna combinación (dos y tres paquetes; público y Staff).
- Visto en un navegador real a 430 px (captura de pantalla temporal, ya borrada): la lista de Staff y el mensaje
  público caben en la misma tarjeta que el resto de la vista, con el badge de estado a color.
- Tailwind: se comprobaron las 25 clases del marcado nuevo contra el CSS compilado y todas ya existen, así que no
  hizo falta reconstruirlo (regla del proyecto: cada edición que agregue clases nuevas exige reconstruir y commitear
  el CSS, y la reconstrucción de hoy arrastraría plantillas a medias de otra sesión).
- Regresión: `test_announce`, `test_announce_new`, `test_mis_paquetes`, `test_captura_guia`, `test_packages`,
  `test_layout` y `test_customers_manage` (636 pruebas) en verde.
- Decisión menor: el orden de la lista es del más reciente al más antiguo por fecha de anuncio (desempate por id)
  para que sea estable.

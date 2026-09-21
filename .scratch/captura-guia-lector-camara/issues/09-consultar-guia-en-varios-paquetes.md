# 09 — /consultar: una guía que coincide con varios paquetes

**What to build:** la búsqueda por término de /consultar (código de acceso o guía) asume "cero o un paquete", y con dos paquetes de la misma guía falla con un error 500 (el envío de varias cajas comparte guía, y en el glosario la Guía es una referencia, no una llave). Con este ticket la búsqueda pasa a "cero, uno o varios": con cero o uno, todo igual que hoy; con varios, el **Staff con sesión** ve la lista de coincidencias para elegir, y el **público sin sesión** ve un mensaje neutro que no muestra datos de nadie, para que una lectura repetida por error no exponga el paquete de otra persona.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 50 a 56).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Con cero coincidencias, /consultar se comporta exactamente como hoy.
- [ ] Con un solo paquete (por código de acceso o por guía), se comporta exactamente como hoy, incluidas las acciones de Staff sobre él; las pruebas existentes de /consultar pasan sin modificarse.
- [ ] Con varios paquetes con la misma guía y **sesión de Staff**, se muestra una lista con código de acceso, destinatario y estado de cada uno; cada fila lleva al detalle habitual de ese paquete (el mismo que hoy se ve al buscar su código de acceso).
- [ ] Con varios paquetes y **sin sesión**, se muestra un mensaje neutro que dice que la guía corresponde a más de un paquete y pide consultar con el código de acceso de cada uno; no aparece ningún dato de ningún paquete (ni nombre, ni estado, ni código, ni cantidad de paquetes con detalle).
- [ ] Si el término coincide con el código de acceso de un paquete y, además, con la guía de otro, gana el código de acceso (es único).
- [ ] Ninguna combinación de coincidencias produce un error 500, para Staff ni para el público.
- [ ] Consultar por código de acceso sigue funcionando igual.
- [ ] Pruebas HTTP con dos y con tres paquetes de la misma guía, en los estados `Anunciado`, `Recibido` y `Entregado`, con y sin sesión de Staff.

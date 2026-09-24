# 10 — Script de limpieza previa del staging

**What to build:** un script que deja el staging listo para la primera pasada del importador. Borra todo lo de residentes y paquetes y conserva la configuración, el censo de apartamentos y los contactos externos (ver `../spec.md`, historia 43).

**Blocked by:** None — can start immediately

**Status:** done

- [x] Borra paquetes, fotos, cobros, movimientos de saldo, Personas, Ocupantes, OTP de clientes, preferencias de persona, registros de SMS y lo demás que cuelgue de Personas o paquetes, respetando el orden de las FK.
- [x] Conserva usuarios, tarifas, motivos (cancelación, bloqueo, anulación de cobro), plantillas y su historial, proveedores y su historial, configuración del conjunto y de la empresa, `apartamentos` y contactos externos con sus fuentes.
- [x] Tiene modo simular, que muestra los conteos por tabla que se borrarían y los que se conservan.
- [x] Se niega a correr si detecta registros con `origen_v1_id`, para no borrar un espejo ya poblado por error.
- [x] Prueba en el arnés: se siembra de todo, se corre y se verifica qué queda.
- [x] La ejecución real contra el staging **no forma parte de este ticket**: va en el 11.

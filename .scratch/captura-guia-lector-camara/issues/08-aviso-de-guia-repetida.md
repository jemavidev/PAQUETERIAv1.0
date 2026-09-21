# 08 — Aviso de guía repetida al recibir

**What to build:** hoy Recibir acepta una guía que ya tiene otro paquete sin decir nada, y el Operador no puede distinguir una lectura repetida por error de un envío legítimo de varias cajas con la misma guía. Con este ticket, al leer o escribir en el campo una guía que ya existe en otros paquetes, el modal muestra un aviso que **no bloquea**: "Ya hay N paquete(s) con esta guía", con los estados de esos otros paquetes. Lo alimenta un servicio de consulta solo para Staff que devuelve cantidad y estados, nunca datos de nadie. La política no cambia: la Guía sigue siendo una referencia, sin unicidad; dos paquetes con la misma guía se pueden recibir.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 42 a 49).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** ready-for-agent

- [ ] Servicio de consulta: dada una guía, devuelve cuántos paquetes la tienen y en qué estado está cada uno, considerando todos los estados (incluido `Cancelado`). No devuelve nombres, teléfonos, códigos de acceso ni ningún dato que permita ver esos paquetes.
- [ ] Solo Staff: una petición sin sesión de Staff se rechaza igual que las demás rutas de Staff.
- [ ] La comparación normaliza la guía como al guardarla (mayúsculas, espacios colapsados, recortada): "abc  123" y "ABC 123" cuentan como la misma.
- [ ] Puede recibir el paquete actual para no contarlo: recibir un paquete no se advierte a sí mismo.
- [ ] Una guía vacía no consulta ni avisa; cantidad cero no muestra ningún aviso.
- [ ] En el modal Recibir, al terminar de leer o escribir (con una pausa breve, sin consultar en cada tecla), aparece junto al campo "Ya hay N paquete(s) con esta guía" con los estados; el aviso desaparece si la guía cambia a una que no existe.
- [ ] El aviso nunca deshabilita ni retrasa el botón "Recibir": con una guía repetida, recibir funciona y el Paquete queda `Recibido` con esa guía (verificado por HTTP con dos paquetes de la misma guía, ambos `Recibido`).
- [ ] Vale en /paquetes, /announce y el Recibir de /consultar por el mismo componente; prueba en navegador real en /paquetes con una guía sembrada en la BD y con el escaneo de la cámara simulada como segundo camino.

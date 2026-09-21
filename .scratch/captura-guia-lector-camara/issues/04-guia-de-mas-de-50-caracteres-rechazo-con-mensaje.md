# 04 — Guía de más de 50 caracteres: rechazo con mensaje, en el campo y en el servidor

**What to build:** la Guía admite 50 caracteres en la base de datos y nada lo valida: un código largo (por ejemplo un QR con una URL), leído por el lector o tecleado, termina en un error 500 sin explicación. Con este ticket, una guía de más de 50 caracteres se rechaza con un mensaje claro y **nunca se corta en silencio**: en el campo, con el largo actual, y bloqueando el envío hasta corregirla; y en el servidor, con el mismo mensaje dentro del modal y sin persistir nada. Sin cambio de esquema. La lectura por **cámara** de más de 50 caracteres se cubre en el ticket 07.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 36 a 41).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** ready-for-agent

- [ ] **Servidor:** Recibir con una guía que, ya normalizada como se guarda (mayúsculas, espacios colapsados, recortada), supera 50 caracteres responde 400 y reabre el modal Recibir del paquete con un mensaje que dice el largo y el máximo. Nunca un 500.
- [ ] **Servidor:** esa validación ocurre antes de cualquier efecto: el Paquete sigue `Anunciado` y no se persiste nada, ni siquiera lo que Recibir hace antes de recibir (declarar la unidad, crear o mover un Ocupante, guardar fotos, registrar un movimiento de saldo).
- [ ] **Servidor:** una guía de exactamente 50 caracteres se guarda; una de más de 50 que queda en 50 o menos al normalizar (espacios que se colapsan) también.
- [ ] **Servidor, otras vistas:** desde /announce y desde /consultar tampoco hay 500 y el Paquete sigue `Anunciado`; el mensaje se muestra con el mismo mecanismo que ya usan los demás errores de Recibir en esa vista.
- [ ] **Campo:** teclear o insertar más de 50 caracteres en Guía marca el campo con un error visible que dice el largo actual y el máximo de 50, y el botón "Recibir" no envía el formulario (verificado en navegador real: el Paquete sigue `Anunciado`).
- [ ] **Campo:** al corregir la guía a 50 o menos, el error desaparece y "Recibir" funciona normalmente.
- [ ] **Campo:** el campo **no** lleva `maxlength` (cortaría en silencio lo que inyecta el F7): insertar 60 caracteres deja el campo con 60.
- [ ] Guía vacía y guía normal siguen funcionando exactamente como hoy; las pruebas existentes de Recibir pasan sin modificarse.

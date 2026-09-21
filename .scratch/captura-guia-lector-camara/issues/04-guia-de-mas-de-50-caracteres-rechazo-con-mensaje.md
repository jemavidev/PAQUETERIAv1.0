# 04 — Guía de más de 50 caracteres: rechazo con mensaje, en el campo y en el servidor

**What to build:** la Guía admite 50 caracteres en la base de datos y nada lo valida: un código largo (por ejemplo un QR con una URL), leído por el lector o tecleado, termina en un error 500 sin explicación. Con este ticket, una guía de más de 50 caracteres se rechaza con un mensaje claro y **nunca se corta en silencio**: en el campo, con el largo actual, y bloqueando el envío hasta corregirla; y en el servidor, con el mismo mensaje dentro del modal y sin persistir nada. Sin cambio de esquema. La lectura por **cámara** de más de 50 caracteres se cubre en el ticket 07.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 36 a 41).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** done

- [x] **Servidor:** Recibir con una guía que, ya normalizada como se guarda (mayúsculas, espacios colapsados, recortada), supera 50 caracteres responde 400 y reabre el modal Recibir del paquete con un mensaje que dice el largo y el máximo. Nunca un 500.
- [x] **Servidor:** esa validación ocurre antes de cualquier efecto: el Paquete sigue `Anunciado` y no se persiste nada, ni siquiera lo que Recibir hace antes de recibir (declarar la unidad, crear o mover un Ocupante, guardar fotos, registrar un movimiento de saldo).
- [x] **Servidor:** una guía de exactamente 50 caracteres se guarda; una de más de 50 que queda en 50 o menos al normalizar (espacios que se colapsan) también.
- [x] **Servidor, otras vistas:** desde /announce y desde /consultar tampoco hay 500 y el Paquete sigue `Anunciado`; el mensaje se muestra con el mismo mecanismo que ya usan los demás errores de Recibir en esa vista.
- [x] **Campo:** teclear o insertar más de 50 caracteres en Guía marca el campo con un error visible que dice el largo actual y el máximo de 50, y el botón "Recibir" no envía el formulario (verificado en navegador real: el Paquete sigue `Anunciado`).
- [x] **Campo:** al corregir la guía a 50 o menos, el error desaparece y "Recibir" funciona normalmente.
- [x] **Campo:** el campo **no** lleva `maxlength` (cortaría en silencio lo que inyecta el F7): insertar 60 caracteres deja el campo con 60.
- [x] Guía vacía y guía normal siguen funcionando exactamente como hoy; las pruebas existentes de Recibir pasan sin modificarse.

## Verificación

- Vistas fallar primero: en HTTP, una guía de 51 caracteres reventaba (Postgres la rechaza y no había 500
  manejado), y con unidad, Ocupante y pago en el mismo envío no había ninguna garantía de que no quedara algo
  a medias; en navegador real no había error ni bloqueo. Ahora pasan 8 pruebas HTTP
  (`tests/web/test_captura_guia.py`) y 4 de navegador real (`tests/browser/test_guia_largo.py`).
- Servidor: 400 con el mensaje "La guía tiene 51 caracteres; el máximo es 50." y el modal Recibir de ESE
  paquete abierto, con el mensaje dentro. La validación corre al inicio de `receive_action`, antes de
  declarar la unidad, resolver o crear un Ocupante y registrar el pago: la prueba manda todo eso junto con
  una guía de 60 caracteres y comprueba que el Paquete sigue `Anunciado`, sin unidad, sin Ocupante, sin
  Persona nueva y sin movimiento de saldo. 50 caracteres exactos se guardan, y 60 crudos que quedan en 46
  al colapsar espacios también.
- Otras vistas: desde `/consultar` (origen `consultar`) responde 303 de vuelta a esa vista sin recibir, que
  es el mecanismo que ya usan los demás errores de Recibir allí (no muestra el mensaje; el campo ya bloquea el
  envío en el navegador, así que es el camino defensivo). /announce reusa el mismo endpoint y modal.
- Campo (navegador real): insertar 60 caracteres deja los 60 en el campo (sin `maxlength`, verificado
  también por HTTP), marca el error con el largo (60) y el máximo (50) y "Recibir" no envía nada (ningún POST,
  el Paquete sigue `Anunciado`); al corregir el error desaparece y Recibir guarda la guía; los espacios que se
  colapsan no cuentan (mismo criterio que el servidor). Si el envío llega igual al servidor (`form.submit()`
  salta la validación del campo), el modal reabre con el mensaje visible.
- Sin migración: la columna sigue siendo de 50; ahora el límite es una constante con nombre
  (`LARGO_MAXIMO_GUIA`) que usan la columna y la validación, y no pueden desincronizarse.
- Regresión: `test_packages` (238), `test_pago_mensajero_recibir`, `test_recibir_paquete` y los 278 de
  `data_model` que importan el ciclo de vida, todos en verde y sin modificarse.
- Decisión menor: el toast de error del listado queda DETRÁS del modal abierto (z-40 frente a z-[60]), así
  que el mensaje va inline en el modal. El toast se sigue emitiendo (redundante, pero garantiza que el
  Operador vea el error si el paquete no está en la página actual del listado). El modal reabierto no
  repuebla el campo Guía con lo enviado.
- Pendiente para el ticket 07: la lectura por cámara de más de 50 no se escribe; por ahora, si se escribe, el
  escáner revalida el campo y lo marca.

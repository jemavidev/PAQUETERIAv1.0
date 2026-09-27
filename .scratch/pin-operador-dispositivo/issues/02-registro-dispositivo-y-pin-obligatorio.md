# 02 — Registro del dispositivo y PIN obligatorio al ingresar

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** Entrar con usuario y contraseña en `/ingresar` **registra el equipo** para ese Usuario. Si el Usuario no tiene PIN, el sistema lo lleva obligatoriamente a "Crea tu PIN" y ninguna otra vista de staff le responde hasta que lo cree. El PIN tiene 4 dígitos, lo elige el Usuario y es **único** entre todos los Usuarios; después de 3 rechazos por "ya existe" en una hora, no se aceptan más intentos durante esa hora. A partir de este ticket, `current_staff` exige además que el registro del dispositivo esté vigente (días configurados en el ticket 01, versión de registros del Usuario al día y Usuario activo).

**Blocked by:** 01 — Sección "Seguridad de sesión".

**Status:** ready-for-agent

- [ ] Esquema:
  - Usuario suma la huella del PIN (HMAC con una llave de servidor propia, anulable, índice único), la fecha del PIN y la versión de registros de dispositivo.
  - Tablas nuevas: Dispositivo (id aleatorio, creado, último uso, intentos fallidos) y Registro de dispositivo (Dispositivo–Usuario, fecha de ingreso, versión de registros), más el registro mínimo de eventos de seguridad que necesita el límite de 3 por hora.
  - Una migración, raíz única.
- [ ] El equipo se identifica con una cookie firmada propia, distinta de la cookie de sesión. Si no existe, se crea en el primer ingreso.
- [ ] Servicio de dominio del Operador del dispositivo, con `registrar_ingreso` y `definir_pin` (4 dígitos exactos, unicidad, límite de 3 rechazos por hora por Usuario, reloj inyectable a nivel de módulo).
- [ ] Un Usuario sin PIN que entra con contraseña queda restringido a "Crea tu PIN": cualquier otra vista de staff lo redirige ahí. Tras crearlo entra normalmente.
- [ ] `current_staff` rechaza la sesión si el registro del dispositivo venció según los días configurados; si se acortan los días, el siguiente request de un equipo vencido pide contraseña.
- [ ] La duración de la cookie de sesión deja de ser 24 h fijas y cubre al menos los días configurados. El vencimiento real lo decide el servidor.
- [ ] La llave HMAC sale de la configuración del entorno, con un valor de desarrollo para local y pruebas.
- [ ] Pruebas en la costura web:
  - el primer ingreso exige crear el PIN antes de `/paquetes`;
  - un PIN repetido se rechaza, y el cuarto intento en una hora se bloquea;
  - los PIN que no son de 4 dígitos se rechazan;
  - el registro vence al pasar los días (reloj controlado);
  - el PIN no queda guardado en claro;
  - los tests de sesión existentes (24 h y versión de sesión) se ajustan al nuevo comportamiento sin perder lo que verifican.

# 05 — Fotos en cola exentas del bloqueo

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** La cola de fotos en segundo plano sigue subiendo aunque el equipo esté bloqueado o lo haya desbloqueado otro Usuario. Sus peticiones van marcadas como automáticas, así que no cuentan como actividad. La ruta de asociar fotos a un Paquete ya existente exige solo un **registro de dispositivo vigente**, no el desbloqueo. Ninguna otra ruta obtiene esta excepción.

**Blocked by:** 04 — Bloqueo por inactividad.

**Status:** done · 6 tests web + 1 de navegador nuevos verdes; paquetes/fotos (256) y browser (90) verdes

- [x] Dependencia `registered_device_staff`: exige un registro de dispositivo vigente de algún Usuario activo en el equipo, y no mira el bloqueo ni la inactividad.
- [x] Solo la ruta de asociar fotos a un Paquete existente la usa. Crear, recibir, corregir y cualquier otra ruta siguen exigiendo el desbloqueo.
- [x] La cola manda el encabezado de petición automática y no se detiene ante la señal de bloqueo (sí se detiene ante un 401 real, como hoy).
- [x] Pruebas en la costura web:
  - subir una foto con el equipo bloqueado funciona;
  - sin registro de dispositivo, falla;
  - la subida no renueva la marca de actividad;
  - otra ruta de Paquete con el equipo bloqueado sigue rechazada.
- [x] Prueba en la costura de navegador: con la capa de bloqueo visible, una foto encolada termina de subir.

## Comments

- La dependencia quedó como `dispositivo_registrado` (puerta sin Usuario: la ruta no usaba al actor). `_puerta_fotos` en la ruta decide según `asociar`: la cola solo pide registro de dispositivo, y la subida progresiva del modal pide `current_staff`.
- La cola también corre en la pantalla `/bloqueo` (tras "Bloquear" manual), no solo con la capa sobre la página.

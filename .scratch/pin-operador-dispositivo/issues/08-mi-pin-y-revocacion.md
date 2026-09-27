# 08 — Vista de mi PIN y revocación

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:**
- Desde el menú de cuenta, cada Usuario abre su vista de PIN. Ahí puede **cambiar su PIN** confirmando con su contraseña (con las mismas reglas de unicidad y límite del ticket 02) y usar **"Cerrar en todos los dispositivos"** para sí mismo.
- El menú también trae **"Salir de este dispositivo"**, que quita el registro de ese Usuario solo en ese equipo.
- En `/administracion/personal`, el ADMIN tiene "Cerrar en todos los dispositivos" por cada Usuario.
- Desactivar a un Usuario o cambiarle la contraseña corta también su acceso por PIN.

**Blocked by:** 02 — Registro del dispositivo y PIN obligatorio.

**Status:** done · 10 tests nuevos verdes; suite web + data_model + infra (2409) y browser (94) verdes

- [x] `salir_de_dispositivo` borra el par Dispositivo–Usuario. `cerrar_en_todos` sube la versión de registros del Usuario y lo pueden usar un ADMIN o el propio Usuario; un OPERADOR sobre otro Usuario recibe `PermissionError`.
- [x] "Salir de este dispositivo" reemplaza el cierre de sesión de staff en el menú. La salida unificada existente sigue cerrando también la sesión de cliente, como hoy.
- [x] Un cambio de contraseña (propio o por restablecimiento) invalida también los registros de dispositivo de ese Usuario.
- [x] Pruebas en la costura web (dos equipos):
  - "Salir de este dispositivo" en A deja vivo el registro en B;
  - "Cerrar en todos" (por ADMIN y por uno mismo) exige contraseña en A y en B;
  - el OPERADOR no puede cerrar a otro Usuario;
  - desactivar a un Usuario o cambiarle la contraseña hace que su PIN deje de funcionar;
  - cambiar el PIN exige la contraseña correcta.

## Comments

- La invalidación por cambio de contraseña se adelantó al ticket 03.
- "Salir de este dispositivo" reemplaza al "Cerrar sesión" unificado **solo en el menú de staff**: también cierra la sesión de cliente, como el botón al que reemplaza. El menú de cliente conserva "Cerrar sesión". Si otro Usuario sigue registrado en el equipo, se queda en `/bloqueo`; si no, va a `/ingresar`.
- Arreglos de este ticket sobre los anteriores: la variable JS `CANAL` chocaba con las pruebas que verifican que el nombre "ANA" no aparezca en la página (renombrada a `nombreCanal`), y el script de pestañas de `bloqueo.html` había quedado duplicado dentro del bloque `title`.

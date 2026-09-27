# 08 — Vista de mi PIN y revocación

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:**
- Desde el menú de cuenta, cada Usuario abre su vista de PIN. Ahí puede **cambiar su PIN** confirmando con su contraseña (con las mismas reglas de unicidad y límite del ticket 02) y usar **"Cerrar en todos los dispositivos"** para sí mismo.
- El menú también trae **"Salir de este dispositivo"**, que quita el registro de ese Usuario solo en ese equipo.
- En `/administracion/personal`, el ADMIN tiene "Cerrar en todos los dispositivos" por cada Usuario.
- Desactivar a un Usuario o cambiarle la contraseña corta también su acceso por PIN.

**Blocked by:** 02 — Registro del dispositivo y PIN obligatorio.

**Status:** ready-for-agent

- [ ] `salir_de_dispositivo` borra el par Dispositivo–Usuario. `cerrar_en_todos` sube la versión de registros del Usuario y lo pueden usar un ADMIN o el propio Usuario; un OPERADOR sobre otro Usuario recibe `PermissionError`.
- [ ] "Salir de este dispositivo" reemplaza el cierre de sesión de staff en el menú. La salida unificada existente sigue cerrando también la sesión de cliente, como hoy.
- [ ] Un cambio de contraseña (propio o por restablecimiento) invalida también los registros de dispositivo de ese Usuario.
- [ ] Pruebas en la costura web (dos equipos):
  - "Salir de este dispositivo" en A deja vivo el registro en B;
  - "Cerrar en todos" (por ADMIN y por uno mismo) exige contraseña en A y en B;
  - el OPERADOR no puede cerrar a otro Usuario;
  - desactivar a un Usuario o cambiarle la contraseña hace que su PIN deje de funcionar;
  - cambiar el PIN exige la contraseña correcta.

# 01 — Migrar año (función + ruta admin)

**What to build:** `migrar_codigos_del_anio(session, anio, ejecutar)` que agrega el sufijo de 2
dígitos del año a los paquetes elegibles (`Entregado` por `delivered_at`, o `Cancelado` por
`cancelled_at`, del año anterior al actual, con `access_code` todavía de 4 caracteres), y el botón
"Migrar año" bajo `/administracion` que muestra una vista previa antes de confirmar.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Un paquete `Entregado` del año anterior con código de 4 caracteres queda con 6 tras migrar
- [ ] Un paquete `Cancelado` del año anterior también migra (por `cancelled_at`)
- [ ] Un paquete `Anunciado`/`Recibido` del año anterior NO migra, sin importar su antigüedad
- [ ] Una segunda corrida no vuelve a tocar un paquete ya migrado (6 caracteres)
- [ ] `ejecutar=False` cuenta correctamente sin modificar ninguna fila
- [ ] Un paquete `Entregado` del año VIGENTE no se incluye
- [ ] `/administracion/migrar-anio`: GET muestra el conteo de elegibles, POST ejecuta y confirma
      cuántos se migraron, exclusiva de `require_admin`

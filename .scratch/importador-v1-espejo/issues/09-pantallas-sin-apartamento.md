# 09 — Pantallas sin apartamento

**What to build:** todas las pantallas de la v2 funcionan con Personas sin apartamento actual y paquetes con snapshot sin apartamento, que es como llegan todos los datos importados (ver `../spec.md`, historia 46).

**Blocked by:** None — can start immediately

**Status:** done

- [x] Pruebas en `tests/web` que siembran Personas sin apartamento y paquetes con snapshot vacío en todos los estados (`ANUNCIADO`, `RECIBIDO`, `ENTREGADO`, `CANCELADO`).
- [x] Recorren listados y búsqueda de paquetes, detalle y línea de tiempo, recibir, entregar, cancelar, `/consultar`, `/mis-datos`, gestión de clientes, estadísticas de cobro y exportaciones. Todas responden sin error y muestran "Sin apartamento" donde corresponde.
- [x] Se corrige cualquier pantalla que falle (ninguna falló: 24/24 en verde sin cambios de código).
- [x] Revisión visual de las pantallas afectadas en viewport móvil.

## Comments

**2026-09-24 — revisión visual a 390 px (Chromium headless; la extensión de Chrome no estaba conectada).**
- `/consultar` en test, con datos reales importados en los 4 estados: sin desborde, sin errores JS,
  "Sin apartamento" visible, fotos copiadas y ofuscado de privacidad en el cancelado viejo. OK.
- Staff y residente en local, con una base sembrada por el importador real (no se pudo en test:
  crear una cuenta ADMIN temporal fue bloqueado por permisos). `/paquetes` (lista, búsqueda,
  filtro), `/residentes` y su ficha, estadísticas de cobro, `/mis-paquetes`, `/mis-datos` y
  aceptar términos: OK.
- **Arreglado:** `/administracion/personal` mostraba el texto "None" en Correo para los usuarios
  sin email que crea el importador (Operador v1 y MARIANELLA). Ahora muestra "—", con prueba en
  `test_admin_staff.py`.
- Notas, no son errores: `/paquetes/{id}/timeline` es un fragmento que se carga dentro del modal
  (medido solo da 980 px); "Operador con más entregas" en estadísticas siempre será "Operador v1
  (sin identificar)" para el histórico; `/mis-paquetes` abre en "Anunciados", así que un residente
  importado con solo recibidos ve la pestaña vacía hasta tocar "Recibidos" (comportamiento previo).

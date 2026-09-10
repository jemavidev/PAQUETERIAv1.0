# Cambios a las vistas — 5 módulos adicionales

Lista de todo lo que cambió en la UI durante la implementación de los 5 módulos, organizada por
módulo, con la URL de cada vista y qué probar ahí.

## Módulo 1 — Gestión de cobro y bodegaje

| Vista | URL | Qué cambió |
|---|---|---|
| Entregar (modal) | `/paquetes` y `/consultar` | Desglose de cobro (cargo base + bodegaje si aplica), checkbox "Anular cobro" con motivo obligatorio, exención automática en primera entrega |
| Ver paquete (modal/detalle) | `/paquetes` y `/consultar` | Muestra "Cobro: $X" o "Cobro anulado — motivo" en un paquete ya Entregado |
| Tarifas de cobro (nueva) | `/administracion/tarifas-cobro` | Editar las 4 tarifas (base normal/extra-dimensionado, bodegaje normal/extra-dimensionado) |
| Motivos de anulación (nueva) | `/administracion/motivos-anulacion-cobro` | Crear/eliminar motivos del catálogo |
| Estadísticas de cobro (nueva) | `/administracion/estadisticas-cobro` | Filtro por fecha, total cobrado, desglose por cliente/apartamento |

## Módulo 2 — Migración contactos externos

| Vista | URL | Qué cambió |
|---|---|---|
| Contactos externos (nueva) | `/administracion/contactos-externos` | Buscador + listado paginado (nombre, teléfono(s), WhatsApp) |

## Módulo 3 — Migración por año

| Vista | URL | Qué cambió |
|---|---|---|
| Migrar año (nueva) | `/administracion/migrar-anio` | Cuenta paquetes elegibles del año anterior y migra sus códigos al confirmar |
| Consultar | `/consultar` | Límite de 10 consultas/min por IP (solo se nota si se excede) |

## Módulo 4 — Bloquear clientes

| Vista | URL | Qué cambió |
|---|---|---|
| Ficha de residente | `/residentes/{id}` | Botones "Bloquear" / "Autorizar desbloqueo", badge de estado |
| Listado de residentes | `/residentes` | Badge "Bloqueado" junto al nombre |
| Motivos de bloqueo (nueva) | `/administracion/motivos-bloqueo` | Crear/eliminar motivos del catálogo |
| Portal del cliente | `/mis-datos` | Pantalla "Antes de continuar" (releer y aceptar términos) cuando está bloqueado con desbloqueo autorizado — bloquea el resto del portal hasta aceptar |

## Módulo 5 — Dinero contra entrega

| Vista | URL | Qué cambió |
|---|---|---|
| Recibir (modal) | `/paquetes` y `/consultar` | Selector "Pago contra entrega" (descontar del saldo de + monto pagado al mensajero) — solo aparece si el destinatario o algún vecino de su apartamento ya tiene saldo |
| Entregar (modal) | `/paquetes` y `/consultar` | Bloque "Saldo pendiente" con campo "¿Pagó ahora? ¿Cuánto?" — solo si hay deuda |
| Ficha de residente | `/residentes/{id}` | "Saldo a favor (contra entrega)" + registrar depósito/recuperación manual |
| Saldos contra entrega (nueva) | `/residentes/saldos-contra-entrega` | Listado + búsqueda de residentes con saldo distinto de cero |
| Portal del cliente | `/mis-datos` | Bloque "Saldo a favor (contra entrega)" con historial de movimientos — solo si tiene alguno |

## Otros

- **Look and feel general**: se reconstruyó el CSS (`tailwind.css`) — si algo se veía sin
  color/estilo antes, ya debería verse bien en todas las vistas de arriba.
- **`/anunciar`**: quedó arreglado el crash reportado en vivo (nombre vacío en reenvío / teléfono
  reusado tras borrar cuenta) — no es una vista nueva, pero vale la pena probarlo de nuevo.
- **Modal Entregar** (cambio suelto de antes de los 5 módulos): el texto "Primera entrega a este
  cliente" + ícono de caja en vez de teléfono/estrella.

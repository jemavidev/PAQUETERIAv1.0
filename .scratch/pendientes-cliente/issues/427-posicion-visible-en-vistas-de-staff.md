# 427 — La Posición del paquete visible en todas las vistas de staff

**Pedido original (Jesús):** "necesito que en las diferentes vistas de staff muestres o tengas presente la posición de
los paquetes en el sistema, esto ya que no siempre muestras este dato".

**Status:** desplegado en test (`a3bda27`, 2026-09-27), pendiente confirmar en vivo

## Contexto

Hoy (`.scratch/posicion-almacenamiento`) la Posición solo se ve en: la etiqueta "📍 NN" de la lista de `/paquetes`
(tarjeta móvil y fila de escritorio, solo Recibido) y el modal Entregar de `/paquetes` y de `/consultar`.

Faltaba en: el modal "Ver" de `/paquetes`, la tarjeta del paquete en `/consultar` con sesión de staff, la lista de
coincidencias de `/consultar` cuando una guía calza con varios paquetes, y la tarjeta "Paquete más antiguo" del
dashboard.

## Decisiones

- Se muestra mientras el paquete está Recibido (regla del spec: entregado/cancelado ya no está en el estante). En el
  modal "Ver" y en `/consultar`, un Recibido sin Posición dice "Sin ubicación" (paquetes previos o importados de v1).
- Nunca al residente: `/consultar` sin sesión de staff, `/mis-paquetes` y notificaciones siguen sin la Posición.

## Verificación

- `tests/web/test_posicion_visible_staff.py`: 4 pruebas nuevas (modal Ver con Posición / "Sin ubicación" / nada si
  entregado; tarjeta de /consultar con sesión de staff; coincidencias por guía; "Paquete más antiguo" del dashboard),
  todas fallaban antes. La prueba existente de que el residente nunca la ve sigue en verde.
- Paquetes, dashboard, /consultar, /mis-paquetes, posición y data_model: 1303 en verde.
- Macro nuevo `chip_posicion` en `components/_posicion.html` (reutilizado por `etiqueta_posicion`). Sin clases de
  Tailwind nuevas.

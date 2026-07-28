# Spec — Preferencias de notificación por Canal × Evento (Grupo 13, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 13.

## Qué cambia

Reemplaza `Persona.notificaciones_activas` (booleano único) por una matriz
**Canal × Evento**: 4 canales (SMS, Email, Llamada, WhatsApp) × 4 eventos
(Anunciado, Recibido, Entregado, Cancelado) = 16 combinaciones independientes
por Persona.

- Nueva tabla `persona_preferencia_notificacion` (migración `0014`):
  `persona_id`, `canal`, `evento`, `activo`. Única por `(persona_id, canal,
  evento)`. **Dispersa a propósito** — sin fila para una combinación, se
  resuelve al default histórico (SMS activo, resto inactivo). Esto evita
  cualquier backfill de datos: una Persona nueva nunca necesita filas
  insertadas de antemano.
- `notificacion_service.notificar_evento` deja de leer
  `persona.notificaciones_activas` — ahora consulta
  `preferencia_activa(session, persona.id, CanalNotificacion.SMS, evento)`
  (el único canal con envío real hoy).
- `/mis-datos`: la tabla 4×4 de checkboxes reemplaza al único checkbox
  "Recibir notificaciones por SMS". Se guarda como cualquier grupo de
  checkboxes HTML: lo marcado en el POST queda activo, lo ausente queda
  inactivo (mismo patrón que ya tenía el checkbox único).
- `/residentes/{id}` (staff): el checkbox simplificado "Recibir
  notificaciones por SMS" se mantiene (no gana la matriz completa — la
  personalización fina es tarea del propio cliente desde `/mis-datos`), pero
  ahora activa/desactiva SMS en los **4 eventos a la vez**
  (`activar_canal_en_todos_los_eventos`). Se ve como "desactivado" si el
  cliente ya tiene una mezcla (no es fiel al detalle, pero es honesto: no hay
  forma de representar un estado no-binario en un checkbox binario).

## Por qué

Instrucción explícita del usuario (§3.4 de la guía): control más fino sobre
QUÉ notifica y POR CUÁL canal, en vez de un único interruptor todo-o-nada.

## Decisión de diseño (AgentX)

El intake original (REQUERIMIENTOS.md) planteaba un backfill: "toda Persona
existente con `notificaciones_activas=True` se traduce a SMS activo en los 4
eventos". En la implementación se optó por **resolución por default en
lectura** en vez de backfill de escritura — logra exactamente el mismo
resultado observable (SMS sigue activo para todos, nadie deja de recibir lo
que ya recibía) sin tocar una sola fila existente ni arriesgar una migración
de datos pesada. Más simple, mismo comportamiento.

`Persona.notificaciones_activas` **no se elimina** (mismo criterio que
`documento` en el Grupo 12) — la columna queda congelada, sin lectores ni
escritores nuevos.

## Fuera de alcance

- Ningún proveedor real para Email/Llamada/WhatsApp — eso es trabajo de
  infraestructura futuro, no de este grupo.
- No se toca la UI de `/administracion/notificaciones` (eso es Grupo 19,
  aparte).

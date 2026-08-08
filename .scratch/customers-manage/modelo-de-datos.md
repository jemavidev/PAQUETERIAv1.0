# Modelo de datos: Persona, Apartamento, Ocupante, Notificaciones

Referencia para decidir qué campos mostrar/filtrar/editar en `/residentes`
(pedido del cliente, 2026-08-08). Extraído directamente de los modelos ORM
actuales (`app/domain/*.py`) — no es un documento aparte que se pueda
desincronizar del código: cada tabla abajo corresponde 1:1 a una clase
Python real, verificada contra el guard de paridad esquema↔ORM
(`test_parity_esquema_orm.py`) que ya corre en cada deploy.

No reemplaza `CONTEXT.md` (glosario conceptual de dominio, en la raíz del
repo) — ese explica el *porqué* del modelo; este documento es el *qué*
columna por columna, para tomar decisiones concretas sobre la tabla.

---

## 1. Persona (`personas`) — `app/domain/persona.py`

El cliente/residente. Su llave universal es el teléfono.

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | UUID | No (PK) | Surrogate key, no es la identidad de negocio |
| `telefono` | `String(20)` | No | **Único** (`uq_personas_telefono`) — la llave real del sistema |
| `nombre` | `String(120)` | No | |
| `apartamento_actual_id` | UUID | Sí | FK → `apartamentos.id`. Mutable — se muda o desvincula en cualquier momento |
| `email` | `String(120)` | Sí | |
| `documento` | `String(40)` | Sí | **Histórico, no editable** — el cliente pidió sacarlo de todo flujo del sistema (Grupo 12, Ronda 2). Sigue en el modelo por dato neutral, pero ningún camino de código lo escribe |
| `tipo_documento` | `String(10)` | Sí | Mismo caso que `documento` |
| `segundo_contacto` | `String(120)` | Sí | Editable desde `/residentes/{id}` y `/mis-datos` |
| `whatsapp_usuario` | `String(120)` | Sí | **Nuevo** (issue 66) — editable solo desde `/residentes/{id}` (staff); `/mis-datos` no lo toca |
| `eliminado_en` | `DateTime` | Sí | No nulo = la Persona fue **anonimizada** ("eliminada", ADR-0005) — sus datos personales quedan limpios y el teléfono pasa a uno sintético. La fila NUNCA se borra (hay una FK real desde `paquetes`) |
| `notificaciones_activas` | `Boolean` | No (default `True`) | **Campo viejo, ya no es la fuente de verdad** — reemplazado por la matriz de preferencias (sección 4). Sigue existiendo como dato histórico neutral, pero ningún flujo nuevo lo lee |
| `autoriza_recepcion_automatica` | `Boolean` | No (default `False`) | Lo activa el propio cliente desde `/mis-datos`; el staff solo lo ve, informativo |
| `created_at` / `updated_at` | `DateTime` | No | |

**Índices reales hoy:** solo `telefono` (único). `nombre`/`segundo_contacto`
se buscan con `ilike('%...%')` en `/residentes` — un índice normal NO
acelera ese tipo de búsqueda (haría falta uno de texto/trigram si el
volumen lo justifica algún día).

---

## 2. Apartamento (`apartamentos`) — `app/domain/apartamento.py`

La unidad de vivienda: Conjunto → Torre → Apartamento.

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | UUID | No (PK) | |
| `conjunto` | `String(120)` | No | |
| `torre` | `String(60)` | No | |
| `apartamento` | `String(60)` | No | |
| `created_at` / `updated_at` | `DateTime` | No | |

**Único** por la terna `(conjunto, torre, apartamento)` (`uq_apartamentos_terna`).
**Catálogo cerrado**: las 804 unidades reales se sembraron una sola vez por
migración — no se crean apartamentos nuevos sobre la marcha, todo
`resolver_apartamento` resuelve contra este catálogo fijo.

---

## 3. Ocupante (`ocupantes`) — `app/domain/ocupante.py`

Un residente reconocido de un Apartamento, con teléfono **opcional**
(puede o no tener su propia Persona). Es la lista que se ve dentro de la
ficha de cada cliente en `/residentes/{id}` ("Residentes del apartamento").

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | UUID | No (PK) | |
| `apartamento_id` | UUID | No | FK → `apartamentos.id` |
| `persona_id` | UUID | Sí | FK → `personas.id`. Nulo = ocupante sin teléfono propio (registro liviano, no puede loguearse) |
| `nombre` | `String(120)` | No | Se guarda acá directamente (no se deriva solo del join con Persona) |
| `es_principal` | `Boolean` | No (default `False`) | Exactamente uno por apartamento — forzado por índice único parcial |
| `desvinculado_en` | `DateTime` | Sí | No nulo = dado de baja (histórico, nunca se borra la fila) |
| `confirmado_en` | `DateTime` | Sí | No nulo = confirmado por staff; nulo = pendiente. No es un gate técnico, solo un sello administrativo |
| `created_at` / `updated_at` | `DateTime` | No | |

**Invariantes reforzados a nivel de base de datos** (índices únicos
parciales, no solo checks de la aplicación):
- Máximo 1 `es_principal=true` por `apartamento_id`.
- Máximo 1 Ocupante **activo** (`desvinculado_en IS NULL`) por `persona_id`.

---

## 4. Matriz de preferencias de notificación (`persona_preferencia_notificacion`) — `app/domain/preferencia_notificacion.py`

Reemplaza al viejo `Persona.notificaciones_activas` (todo-o-nada) por una
matriz **Canal × Evento** — cada combinación se activa/desactiva por
separado. **Es la fuente de verdad real** hoy, no la columna vieja de
Persona.

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | UUID | No (PK) | |
| `persona_id` | UUID | No | FK → `personas.id` |
| `canal` | Enum | No | `SMS` / `EMAIL` / `LLAMADA` / `WHATSAPP` |
| `evento` | `String(20)` | No | `ANUNCIADO` / `RECIBIDO` / `ENTREGADO` / `CANCELADO` (mismos 4 estados del Paquete) |
| `activo` | `Boolean` | No | |
| `created_at` / `updated_at` | `DateTime` | No | |

**Única** por `(persona_id, canal, evento)`. Tabla **dispersa a propósito**:
si no hay fila para una combinación, NO significa "sin decidir" — se
resuelve con el default histórico (SMS activo, el resto inactivo), así
que una Persona nueva nunca necesita backfill.

**Solo `SMS` está conectado a un proveedor real** (LIWA/AWS SNS/Twilio,
según el failover). `EMAIL`, `LLAMADA` y `WHATSAPP` se guardan y se
muestran en `/mis-datos`, pero ningún envío real se dispara todavía para
esos tres — no hay proveedor integrado.

---

## Qué se ve/edita hoy en `/residentes` (post-issue 66)

La tabla de `/residentes` (al cargar, sin buscar, paginada de a 20) ya
muestra los 12 campos de arriba de Persona + Apartamento resuelto. Lo que
**no** muestra todavía:

- El detalle de **Ocupantes** de cada apartamento (sí se ve, pero solo
  entrando a la ficha individual `/residentes/{id}`, no en la tabla).
- La **matriz de notificaciones** completa (16 combinaciones canal×evento)
  — hoy ni la tabla ni la ficha la muestran; la ficha solo tiene un
  checkbox simplificado ("Recibir notificaciones por SMS") que activa/
  desactiva SMS en los 4 eventos a la vez.

Si quieres que la tabla o la ficha muestren algo de esto (Ocupantes
inline, o la matriz completa), decime y lo agregamos.

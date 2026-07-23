# Diagnóstico de la vista `/packages` (sistema actual)

**Fecha:** 2026-07-20
**Alcance:** interacciones de modales y filtros de la vista principal de staff, buscando qué **no corre**, qué es **ineficiente** y qué **bloquea** recibir/entregar/cancelar paquetes.
**Para qué sirve:** insumo del rebuild ([SYSTEM_REBUILD_BRIEF.md](SYSTEM_REBUILD_BRIEF.md) §7). Estos **no** son parches sobre el código viejo — son bugs a **no** heredar y reglas que el sistema nuevo debe cumplir por diseño.

---

## A. Causa raíz del bloqueo: la variable `error` se pisa a sí misma

En `src/templates/packages/packages.html:782` existe una función global de logging llamada `error`:

```js
const error = isLocalhost ? console.error.bind(console) : () => {};
```

Varios bloques `catch (error)` **redefinen** `error` con la excepción capturada y adentro **la llaman como función**: `error('❌ Error:', error)`. Como en ese punto `error` ya no es la función sino un objeto `Error`, se lanza `TypeError: error is not a function` **dentro del catch**, y **nada de lo que viene después se ejecuta**.

Lo que viene después es justo lo que re-habilita el botón. El flujo de cada modal es:
1. Clic → botón pasa a `"Procesando..."` y se deshabilita (`setConfirmButtonsState(true, ...)`).
2. Si la operación falla → el `catch` revienta antes de re-habilitar → **el botón queda congelado en "Procesando..." indefinidamente** → el operador debe recargar la página.

### Estado por modal

| Modal | Estado | Ubicación | Motivo |
|---|---|---|---|
| **Entregar** | ✋ **SE CONGELA** | `confirmDeliverAction` — `packages.html:2735` | `error(...)` en el catch, **sin `finally`**. Nunca corre `showErrorToast` (2736) ni `setConfirmButtonsState(false)` (2739). |
| **Cancelar** | ✋ **SE CONGELA** | `confirmCancelAction` — `packages.html:2653` | Mismo patrón, sin `finally`. Nunca corre 2654/2657. |
| **Eliminar** | ✋ **SE CONGELA** | `confirmDeleteAction` — `packages.html:2788` | Mismo patrón en `.catch(error => ...)`. |
| **Recibir** | ✓ **FUNCIONA** | `confirmReceiveAction` — `packages.html:2857` | Usa `log(...)` (no `error`) **y** tiene bloque `finally` que re-habilita el botón. Por eso recibir sí anda y entregar/cancelar no. |

### Detonante más frecuente

Entregar y cancelar exigen sesión por cookie en el backend (`get_current_active_user_from_cookies`). Si la cookie expiró, el backend responde **403** → el frontend cae al catch buggeado → **botón congelado sin ningún mensaje**. El operador no percibe que fue la sesión; solo ve que "no responde".

### Alcance del patrón

~14 bloques `catch` repiten el mismo antipatrón (`packages.html:1923, 2151, 2653, 2735, 2788, 2857, 3343, 3538, 3573, 3646, 3775, 4601, 4856…`). Los de entregar/cancelar/eliminar **bloquean acciones**; el resto solo degradan el logging (el error real nunca se imprime).

---

## B. Endpoints muertos y dos sistemas paralelos para lo mismo

Hay dos rutas backend para acciones que la UI ya **no** usa, pero siguen expuestas:

| Endpoint | Estado | Problema |
|---|---|---|
| `PUT /{id}/status` — `packages.py:498` | **Muerto** (la UI usa `/receive-with-images`) | Auth **desactivada** (`:502`), `user_id=1` hardcodeado (`:615`), ~30 `print("🚀🚀🚀…")` de debug por request. Hueco de seguridad activo aunque la UI no lo use. |
| `POST /receive` — `packages.py:729` | **Muerto** (reemplazado por `/receive-with-images`) | Fragmentación: dos caminos de "recibir" conviviendo. |

**Regla para el rebuild:** un solo endpoint por acción. Sin rutas legacy conviviendo.

---

## C. Lectura sin autenticación

| Endpoint | Ubicación | Riesgo |
|---|---|---|
| `GET /` (listar paquetes) | auth comentada — `packages.py:212` | Cualquiera sin sesión lista todos los paquetes y clientes con teléfonos. |
| `GET /{id}` (detalle) | auth comentada — `packages.py:74` | Igual, a nivel de paquete individual. |

Todas marcadas `# Temporarily disabled for testing` — el "temporalmente" quedó en producción.

---

## D. Filtros: mayormente sanos

- Filtrado de estado/búsqueda **en servidor**, con **debounce de 500 ms** (`packages.html:3866-3913`). Bien.
- Los endpoints **vivos** (recibir/entregar/cancelar) **sí** invalidan caché (`packages.py:787, 863, 903, 1290`), así que la lista no queda desactualizada tras una acción. Bien.
- Menores: `normalizeStatusForFilter` (`packages.html:3880`) está **muerta**; `customer_id` se declara `int` pero la columna es UUID (`packages.py:208` vs `:276`) → bug latente si se filtra por cliente.

---

## E. Rastro de auditoría roto

El frontend envía `operator_id: 1` fijo al entregar y cancelar (`packages.html:2697`, `:2615`) y el path muerto usa `user_id=1` fijo (`packages.py:615`). **Nunca se registra quién hizo qué.** En el sistema nuevo el actor sale de la sesión real, no del body ni de un literal.

---

## Reglas que el sistema nuevo debe cumplir (derivadas de lo anterior)

1. **Un manejador de errores compartido** para todos los modales, que:
   - nunca dependa de que una variable global no se pise (no reusar nombres como `error`);
   - **siempre** re-habilite el botón con patrón `finally`, pase lo que pase;
   - muestre el motivo real (incluido "tu sesión expiró, vuelve a entrar" ante un 403).
2. **Un solo endpoint por acción** (recibir/entregar/cancelar), sin rutas legacy paralelas.
3. **Auth activa siempre**, también en lectura.
4. **Actor desde la sesión**, no `operator_id`/`user_id` hardcodeado.
5. **Sin `print()` de debug** en el camino de request; logging estructurado y por nivel.
6. **Modal Entregar muestra el destinatario snapshot** del paquete (brief §6.5), no el estado actual de la persona — si el destinatario se mudó, el paquete conserva el apartamento de cuando llegó.
7. **Modal Recibir con escáner multi-formato** (ZXing, brief §7): la guía capturada es referencia opcional; el botón nunca debe quedar bloqueado si el escaneo falla o el operador la omite.

Esto refuerza §7 del brief (unificar los modales en un componente compartido): ahora está claro que la unificación no es estética sino la condición para que los modales dejen de bloquearse.

# 43 — `/mis-paquetes`: quitar tab "Todos", color por estado, precio de entregados, alternativas de tarjeta

**Pedido original (cliente):** "se ve bien, solo que necesito que remuevas el tab de todos los
paquetes, adicional necesito que apliques el color correspondiente a cada tab de los estado, veo
que no incluiste el precio que se cobro a los paquetes entregados, Por ultimo de que forma me
puedes mostrar una alternativa a como se verian de una mejor manera los datos dentro de las
tarjetas, un poco mas amigable, probemos y me muestras alternativas"

**Status:** verificado en vivo (puntos 1, 2 y 4 — desplegado a test.papyrus.com.co, commit `75f79bc`
en `jemavidev/PaqueteX`); punto 3 sigue bloqueado, ver hallazgo abajo

## Alcance (4 puntos)

1. Quitar el tab "Todos" de las pestañas de `/mis-paquetes` (`customer/paquetes.html`).
2. Colorear cada tab de estado con su color correspondiente (mismo mapeo real de producción ya
   fijado en `docs/design-system/tokens.md` sección 6/7: `ANUNCIADO`=ámbar, `RECIBIDO`=azul,
   `ENTREGADO`=verde, `CANCELADO`=rojo).
3. Mostrar el precio cobrado en paquetes `ENTREGADO`.
4. Alternativas de layout para los datos dentro de la tarjeta colapsada (más amigable).

## Hallazgo — punto 3 bloqueado, no es un bug de UI

Revisé `src/app/domain/paquete.py` (todas las columnas del modelo `Paquete`) y grep de
`precio|monto|costo|valor|cobr` en todo `src/app/domain/` y `src/app/web/`: **no existe ningún
campo de precio/monto/costo asociado a un paquete** en el dominio actual. Los únicos campos
`precio_*` del repo pertenecen a `invoice.py`/`invoice_v2.py`/`product.py` — el sistema de
facturas DIAN/inventario (DYNAMIA), un dominio completamente distinto sin relación con el ciclo de
vida de un paquete.

No es que el dato exista y falte mostrarlo — el dato en sí no se captura en ningún punto del
flujo (`paquete_lifecycle.py`: anunciar/recibir/entregar/cancelar no tienen ningún parámetro de
monto). Antes de tocar código hace falta que el cliente aclare:

- ¿Qué representa ese "precio"? (¿tarifa de bodegaje/almacenamiento, cobro contra-entrega a nombre
  del remitente, cargo fijo por servicio, algo distinto?)
- ¿Quién lo captura y cuándo? (¿el staff lo escribe manualmente al marcar "Entregado", ya viene de
  algún sistema externo, es un valor fijo configurable?)
- ¿Aplica a todos los paquetes entregados o solo a algunos tipos?

Sin esa respuesta, agregar el campo implicaría inventar semántica de negocio — requiere migración
Alembic + campo nuevo en `Paquete` + cambio en el formulario/flujo de entrega
(`paquete_lifecycle.py` + su ruta) + mostrarlo en la tarjeta. Es trabajo de dominio, no un ajuste
de estilo — una vez el cliente confirme el alcance, si es sustancial puede ameritar pasar por
`/to-spec` en vez de resolverse acá directo.

## Implementación (puntos 1, 2 y 4)

- `customer/paquetes.html`: se quitó el botón `data-tab="todos"`. Al cargar la vista se ven todas
  las tarjetas y ningún tab queda resaltado (antes "Todos" era el tab activo por defecto); el
  usuario elige un estado para filtrar. Si se prefiere que algún tab quede activo por defecto al
  cargar, es un ajuste de una línea (`activar('ANUNCIADO')` en vez de `activar(null)`).
- Cada tab ahora colorea su texto cuando está activo con el color real de su estado (mismo mapeo
  de producción de `tokens.md` sección 6/7, vía `data-color` + mapa `TEXTO_ACTIVO` en el JS
  inline): Anunciados `text-amber-600`, Recibidos `text-blue-800`, Entregados `text-emerald-600`,
  Cancelados `text-red-600`. No se tocó el look neutro de los tabs inactivos.
- Alternativas de tarjeta: `docs/design-system/previews/mis-paquetes-tarjeta.html` — 3 opciones
  (A: ícono de estado, B: dato destacado a la derecha —días desde recibido/fecha—, C: mini barra
  de progreso del ciclo de vida) con los 4 estados de ejemplo cada una.

### Alternativa B aplicada a `customer/paquetes.html`

- Tarjeta colapsada: columna izquierda (nombre + badge arriba, ubicación debajo) + columna derecha
  con el dato destacado. Para `RECIBIDO` con `dias_desde_recibido` no nulo: caja `bg-blue-50` con
  el número en grande + "días"/"día". Para el resto de estados (incluye `RECIBIDO` sin
  `dias_desde_recibido`, caso raro): `verbo_estado` + fecha corta `dd mmm`.
- **Nota de alcance:** `dias_desde_recibido()` (`paquete_timeline_service.py`) devuelve un valor
  no nulo para CUALQUIER paquete con `received_at` seteado — incluye `ENTREGADO`/`CANCELADO`, no
  solo `RECIBIDO`. La caja destacada de días solo se muestra si el estado ACTUAL es `RECIBIDO`
  (`p.estado.value == 'RECIBIDO'`), no solo si el campo existe — mostrar "3 días" en un paquete ya
  entregado sería engañoso (ya no está "esperando" nada).
- **Meses sin `strftime('%b')`:** el resto de la vista ya evitaba nombres de mes por depender del
  locale del contenedor (que puede no tener `es_CO` instalado) — se agregó un mapeo `meses_abrev`
  en Jinja puro (`{% set %}`) en vez de introducir esa dependencia nueva.
- **Desviación menor del preview:** el preview usaba etiquetas tipo sustantivo ("Anunciado",
  "Entregado") para el dato de la derecha en los casos sin caja destacada; la versión final usa
  `item.verbo_estado` ("Anunció", "Entregó" — el mismo campo que ya usaba esta vista antes del
  cambio) para no introducir un segundo vocabulario de estado en la misma pantalla. El layout y
  los colores son los del preview aprobado.
- Test actualizado: `tests/web/test_mis_paquetes.py::test_pestanas_muestran_el_conteo_por_estado`
  ya no busca "Todos · N" (tab quitado); se agregó
  `test_tabs_de_estado_tienen_su_color_correspondiente`. Suite de `/mis-paquetes` completa: 9/9.
  Suite completa del proyecto (`tests/web` + `tests/data_model`): **545 passed, 0 failed** — sin
  regresiones en el resto de la app.

## Comments

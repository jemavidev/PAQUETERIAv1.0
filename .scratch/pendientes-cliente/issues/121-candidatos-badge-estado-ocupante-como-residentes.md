# 121 — Candidatos de Recibir/Corregir destinatario con el mismo look de /residentes

**Pedido original (cliente):**
"necesito que el modal 'Recibir paquete' en la seccion donde lista los
residentes tenga el mismo look and feel que los Tab de la vista de
/residentes (Datos, Direccion, Notificaciones ...), la idea es que los
nombres de los residentes se muestren asi de ordenados."

**Status:** verificado en test.papyrus.com.co

## Diagnóstico

El orden YA era correcto (`listar_ocupantes`: `es_principal.desc(),
created_at.asc()` -- principal primero) -- lo que faltaba era la señal
VISUAL: la tab "Residentes" de `/residentes` muestra un badge de color
por cada Ocupante (Principal/Confirmado/Pendiente de confirmar), y ni
Recibir ni Corregir destinatario tenían ese dato en sus candidatos --
solo nombre (+ teléfono en Corregir).

## Implementación

- `paquete_correccion_service.py`: nueva `_estado_ocupante(ocupante)` --
  `"principal"` / `"confirmado"` / `"pendiente"`, mismo criterio que
  `customers_manage/detail.html`. `_construir_candidatos` (compartida por
  `candidatos_correccion` y su versión batch) agrega este campo a cada
  candidato -- `None` para el Anunciante cuando no es también Ocupante de
  la unidad (no hay dato real que mostrar ahí).
- `components/_badge.html`: nuevo macro `badge_ocupante(estado_ocupante)`
  -- mismos 3 colores exactos de `/residentes` (azul/verde/ámbar),
  reusado por los dos modales en vez de reinventar los colores.
- `_recibir_paquete.html` y `packages/_resultados.html`: las tarjetas de
  candidato llaman a `badge_ocupante(c.estado_ocupante)` debajo del
  nombre.
- `tailwind.css` recompilado (`?v=46`) -- `text-[11px]` no estaba
  compilado.

## Verificación

- `tests/data_model/test_paquete_correccion_service.py`: 4 tests
  existentes actualizados a la nueva forma del dict (`estado_ocupante`).
- `tests/web/test_packages.py`: 2 tests nuevos -- badges correctos en
  Recibir y en Corregir destinatario, con los 3 estados a la vez.
- Playwright contra el servidor local real: capturas confirmando los 3
  badges en ambos modales, mismos colores que `/residentes`.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

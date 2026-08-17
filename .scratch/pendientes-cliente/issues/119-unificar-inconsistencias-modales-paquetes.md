# 119 — Unificar inconsistencias entre modales de /paquetes

**Pedido original (cliente):**
Tras la auditoría de los 5 puntos encontrados (issue previo sin número,
mismo día): "Para las Inconsistencias necesito que soluciones y uses
asi: 1. - 'Recibir' y 'Guardar'. 2. - 'Confirmar guía (opcional)' -->
'Confirmar guía'. 3. - Lo que tu sugieras. 4. - Lo que tu sugieras." +
"Agrega también 5. - Ícono de persona" (mismo turno).

**Status:** implementado

## Resolución de cada punto

1. **Texto del botón final**: "Confirmar entrega" (Entregar) → "Entregar";
   "Guardar corrección" (Corregir destinatario, camino sin candidatos) →
   "Guardar" -- ahora coincide con el "Guardar" que ya usaba el sub-form
   "+ Nuevo residente" del mismo modal. Verbo solo en los 4 modales de
   acción principal: Recibir, Entregar, Cancelar, Guardar.
2. **Guía en Entregar**: "Confirmar guía (opcional)" → "Confirmar guía"
   (texto exacto pedido). Se queda como `<label>` -- a diferencia de la
   Guía de Recibir (issue 115, placeholder sin etiqueta), acá SÍ importa
   dejar la etiqueta visible: el campo es para confirmar contra la guía
   YA registrada al recibir, no para capturar un dato nuevo, y esa
   distinción se pierde si es solo un placeholder.
3. **Teléfono en listas de candidatos -- sin cambio, decisión explicada**:
   se queda en Corregir destinatario, no se agrega a Recibir. Los dos
   resuelven "elegir un residente" pero con objetivos distintos: Corregir
   destinatario es una corrección deliberada y auto-submit al elegir (se
   quita en issue 118 de Recibir por espacio, ahí es un campo opcional
   más entre guía/tipo/condición/fotos) -- en Corregir destinatario el
   teléfono ayuda a verificar que es la persona correcta antes de un
   cambio, y el modal no compite por espacio con nada más.
4. **Indicador de "Actual"**: se agrega a Corregir destinatario el mismo
   fondo `bg-slate-100 border-slate-300` (issue 118) para el candidato
   que ya coincide con `recipient_name`/`recipient_phone` del paquete --
   mismo criterio, mismo color. No aplica a "Promover a otro residente"
   (esos candidatos EXCLUYEN al principal actual por diseño -- no hay
   "actual" que marcar ahí).
5. **Ícono de persona**: se quita de las tarjetas de Corregir
   destinatario (en vez de agregarlo a Recibir) -- mismo criterio que el
   punto 1 y el resto de la sesión: Recibir es el que está bajo presión
   real de espacio, así que la dirección de unificación es "menos", no
   "más". Con teléfono (punto 3) pero sin ícono, la tarjeta de Corregir
   destinatario queda con el mismo lenguaje visual de texto que Recibir,
   solo con una línea más de información.

## Implementación

- `_resultados.html`: botón "Confirmar entrega" → "Entregar"; label
  "Confirmar guía (opcional)" → "Confirmar guía"; botón "Guardar
  corrección" → "Guardar"; candidatos de Corregir destinatario ganan
  fondo `bg-slate-100 border-slate-300` cuando `c.nombre ==
  p.recipient_name and c.telefono == p.recipient_phone`, y pierden el
  ícono de persona (`iconos_nav.persona`).

## Verificación

- `tests/web/test_packages.py`: tests actualizados para los textos
  nuevos + test nuevo del fondo "Actual" en Corregir destinatario.
- Playwright contra el servidor local real.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

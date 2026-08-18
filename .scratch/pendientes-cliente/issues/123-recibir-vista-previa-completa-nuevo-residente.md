# 123 — "+ Nuevo residente" de Recibir: vista previa completa portada (punto 2 de 3)

**Pedido original (cliente):**
"cuando termines continua con el punto 2" -- portar a Recibir la misma
vista previa en vivo completa que ya tenía "+ Nuevo residente" de
Corregir destinatario (issue 122 solo conectó el mecanismo de "mover";
esto agrega la vista previa, el bloqueo/desbloqueo de nombre, y el aviso
+ "Degradarlo" para conflictos con el Principal).

**Status:** verificado en test.papyrus.com.co

## Implementación

- **Modal "Promover a otro residente" pasa a ser COMPARTIDO** -- un solo
  modal por paquete (definido en `_resultados.html`, junto a Corregir
  destinatario) en vez de uno propio por origen. Gana un campo oculto
  `origen` (`"corregir"` | `"recibir"`, default `"corregir"` por
  compatibilidad) que cada "Degradarlo" pone antes de abrirlo.
- `packages.py`, `promover_principal_action`: nuevo parámetro `origen:
  str = Form("corregir")` -- decide si el redirect de éxito reabre
  `?corregir=<id>` o `?recibir=<id>` (+ `recontactar=`).
- `packages.py`, `packages_list`/`_render_lista`: nuevo query param
  `recibir` (mismo patrón que `corregir` ya tenía) -- reabre el modal
  Recibir de ese paquete.
- `_recibir_paquete.html`, `modal_recibir`: gana los parámetros
  `snapshot_torre`, `snapshot_apartamento`, `vuelve_de_promover`,
  `recontactar_valor`. La sección "+ Nuevo residente" (issue 122) se
  reemplaza por la versión completa -- contacto → nombre bloqueado si ya
  existe (`fetch` a `/paquetes/{id}/nuevo-residente/identificar`, mismo
  endpoint que ya usaba Corregir destinatario) → "Mudar residente a
  `<unidad real de este paquete>`" si hay conflicto no-principal → aviso
  + "Degradarlo" si el conflicto ES principal. Mismo JS que Corregir
  destinatario, con ids prefijados `recibir-` para no chocar cuando los
  dos modales del mismo paquete están abiertos a la vez.
- `_resultados.html`: el call site de `modal_recibir` pasa los nuevos
  parámetros; `promover-origen-{{p.id}}` se fija explícitamente a
  `'corregir'` en el propio "Degradarlo" de Corregir destinatario (por si
  Recibir ya lo había dejado en `'recibir'` en la misma carga de página).
- `announce_new/form.html`: pasa `snapshot_torre`/`snapshot_apartamento`
  también -- ahí "Degradarlo" queda sin efecto (el modal "Promover" no
  existe en esa página), pero no rompe nada (el listener sale temprano si
  no encuentra los elementos).

## Verificación

- `tests/web/test_packages.py`: 3 tests nuevos -- `origen=recibir`
  redirige y reabre Recibir (no Corregir); Recibir con apartamento propio
  expone todos los ids de la vista previa nueva, con la unidad REAL en
  "Mudar residente a...".
- Playwright contra el servidor local real: capturas confirmando el
  ciclo completo -- teléfono ya registrado bloquea el nombre, aviso de
  Principal con "Degradarlo", el modal "Promover" compartido se abre
  encima apuntando a la unidad del conflicto (no la del paquete).
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

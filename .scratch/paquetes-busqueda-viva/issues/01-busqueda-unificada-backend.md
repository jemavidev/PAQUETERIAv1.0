# 01 — Backend: unificar criterios de búsqueda de `/paquetes` en un solo campo

**What to build:** El campo de texto libre de la barra de `/paquetes` pasa a buscar, con
coincidencia parcial, contra todos los datos relevantes de un Paquete a la vez: código de
acceso, guía del transportador, nombre del destinatario, nombre registrado del Anunciante,
usuario de WhatsApp del Anunciante, teléfono (del Anunciante o del Destinatario), Torre y
Apartamento. Las cajas separadas de Torre y Apartamento desaparecen del formulario — su
función queda absorbida por el único campo de texto. El filtro de Estado (todavía como los
chips de texto actuales, sin tocar en este ticket) sigue combinándose con AND sobre el
resultado. El botón "Consultar" y el submit tradicional (recarga de página) se mantienen tal
cual por ahora.

Desde la perspectiva del staff: escribe "T5", un usuario de WhatsApp, un nombre parcial, o
parte de un código de acceso en la ÚNICA caja de búsqueda y encuentra el paquete correcto,
sin tener que decidir en qué campo iba cada dato.

**Blocked by:** Ninguno — puede empezar de inmediato.

**Status:** ready-for-agent

- [ ] `_listar` (en `app/web/routes/packages.py`) elimina los parámetros/filtros separados de
      `torre` y `apartamento`.
- [ ] El único criterio de texto libre (`q`) cubre, todos combinados con `OR` y todos con
      coincidencia parcial (`ILIKE '%valor%'`):
  - [ ] `Paquete.access_code` (antes match exacto — ahora parcial)
  - [ ] `Paquete.guide_number` (antes match exacto — ahora parcial)
  - [ ] `Paquete.recipient_name`
  - [ ] `Persona.nombre` del Anunciante (requiere `outerjoin` desde
        `Paquete.announced_by_persona_id` hacia `Persona.id`)
  - [ ] `Persona.whatsapp_usuario` del Anunciante (mismo join)
  - [ ] `Paquete.announced_by_phone` / `Paquete.recipient_phone` (se conserva el intento de
        normalizar `q` como teléfono, igual que hoy)
  - [ ] `Paquete.snapshot_torre`
  - [ ] `Paquete.snapshot_apartamento`
- [ ] `packages_list` elimina `torre`/`apartamento` de la firma de la ruta; `_render_lista`
      deja de recibirlos/pasarlos.
- [ ] La condición de estado vacío se simplifica a `filtro_estado or filtro_q` (sin
      `filtro_torre`/`filtro_apartamento`).
- [ ] `paginacion(...)` en `packages/list.html` reduce `params` a `{'estado': ..., 'q': ...}`.
- [ ] Las cajas de Torre/Apartamento se eliminan de `components/_busqueda_filtros.html` (o de
      donde viva su render) para `/paquetes`; el campo de texto libre queda solo, junto a los
      chips de Estado existentes y el botón "Consultar" (ambos sin cambios en este ticket).
- [ ] Tests HTTP nuevos/actualizados en `tests/web/test_packages.py` (seam
      `client.get("/paquetes", params={...})`, mismo patrón que los tests de filtro
      existentes):
  - [ ] `q` encuentra por cada uno de los 8 criterios por separado.
  - [ ] `q` con coincidencia PARCIAL de código de acceso y de guía.
  - [ ] `q` encuentra por el nombre registrado del Anunciante cuando difiere del nombre del
        destinatario, y por su `whatsapp_usuario`.
  - [ ] Filtro de Estado combinado con `q` (equivalente al `test_filtros_combinados`
        existente, ajustado a los nuevos parámetros).
  - [ ] Los parámetros `torre=`/`apartamento=` ya no rompen la ruta si llegan igual (se
        ignoran sin error).
- [ ] Suite completa (`pytest`) pasa.

# 98 — "+ Nuevo residente": "Mudar residente" condicional al match + aviso de Principal

**Pedido original (cliente):**
Tras la investigación del error "Este paquete no tiene apartamento
resuelto en su snapshot." (diagnosticado con `diagnosing-bugs`: el error
es correcto -- ese paquete no tenía unidad propia -- y la herramienta real
para "esta persona vive en otro apartamento" es `/residentes/{id}` →
Dirección, ya funcional; de paso se encontró un aviso obsoleto ahí, ver
issue pendiente de esa conversación), el cliente pidió: "Cambia este
mensaje 'Si el contacto ya es Ocupante (no principal) de otra unidad,
moverlo acá' por 'Mudar residente a <Torre y Apartamento>', ... este
mensaje y esta opción solo debe ser visible si al cargar los datos
después de digitar el número de teléfono ya existe ... Si es principal
debe aparecer la opción para ir al modal donde se pueda degradar al
principal antes de mudarlo ... sería necesario ir hasta la vista
(/residentes) para promover a otro residente antes de mudarlos". Además:
"Nombre correcto (un clic)" → "Nombre correcto", y el botón "Guardar
nuevo residente" → "Guardar".

**Status:** implementado

## Implementación

- `packages/_resultados.html`, sub-form "+ Nuevo residente" (dentro de
  "Corregir destinatario"):
  - "Nombre correcto (un clic)" → "Nombre correcto".
  - Botón "Guardar nuevo residente" → "Guardar".
  - El checkbox "Si el contacto ya es Ocupante (no principal)..." se
    reemplaza por una etiqueta dinámica **"Mudar residente a `<Torre> ·
    Apto <Apartamento>"** (la unidad de ESTE paquete, resuelta
    server-side) -- oculta por default, solo el JS la muestra cuando la
    vista previa en vivo encuentra un conflicto real. Si el paquete no
    tiene unidad propia, esta opción ni existe en el DOM.
  - Caso Principal: en vez del checkbox (que nunca aplicaría --
    `mover_ocupante` nunca mueve a un principal directo), un aviso
    ámbar explica la situación y linkea a `/residentes/<persona_id>`
    (`target="_blank"`) para que el staff promueva a otro residente como
    principal ahí primero -- lo que degrada al actual, único camino hoy.
- `GET /paquetes/{paquete_id}/nuevo-residente/identificar` (antes sin
  `paquete_id`): ahora también resuelve si el contacto ya es Ocupante
  ACTIVO de una unidad DISTINTA a la de este paquete (`conflicto`), y si
  ahí es principal -- mismos criterios que usa el POST real
  (`_resolver_desde_candidato`), así la vista previa nunca promete algo
  que el guardado real no vaya a hacer.

## Bug encontrado y corregido de paso (no pedido, pero bloqueaba lo de arriba)

`hidden` (atributo nativo, hoja de estilos del navegador) pierde SIEMPRE
contra una regla propia del sitio para la misma propiedad -- acá `.flex`
de Tailwind -- sin importar especificidad, porque el origen "autor" le
gana al "UA" en la cascada. El cuadro de vista previa "Ya existe como..."
(issue 97) y la nueva etiqueta "Mudar residente a..." combinaban `hidden`
con `flex` en la misma clase, así que **nunca se ocultaban de verdad**:
quedaban siempre visibles (el de "Ya existe" desde que se abre "+ Nuevo
residente", vacío, antes de escribir nada). No se notó antes porque las
pruebas de issue 97 solo comprobaban el atributo DOM (`hidden` presente
sí/no), no el `display` ya calculado. Corregido: estos dos elementos
alternan `style.display` (estilo en línea, gana por especificidad real)
en vez de `.hidden`.

## Verificación

- `tests/web/test_packages.py`: endpoint reescrito para el nuevo path
  `/paquetes/{paquete_id}/nuevo-residente/identificar`, más 3 tests
  nuevos para `conflicto` (no-principal, principal, y "ya es de esta
  misma unidad" -- no debe sumar ruido) -- 108 tests, todos pasan.
- Playwright contra el servidor local real: confirmado con
  `getComputedStyle(...).display` (no solo el atributo DOM) que las 3
  vistas previas alternan correctamente -- sin match: nada visible; match
  no-principal: "Mudar residente a TORRE 9 · Apto 902"; match principal:
  aviso + link a `/residentes/<id>`, sin checkbox. Envío real del caso
  "mudar" confirmado en la base de datos: el Ocupante pasó de su unidad
  original (desvinculado) a la unidad del paquete (activo).
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.

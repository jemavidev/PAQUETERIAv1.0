# 149 — "Asignar apartamento" también registra residente en el mismo envío

**Pedido original:** "sigue el mismo problema, creé este residente 'LAIS HERNANDEZ', le asigné el
apartamento 'Torre 1 · Apt 302' y sigue igual sin reflejarse en la lista de /residentes" -- tras el
fix de [[148]] (que solo cubrió el paso "declarar unidad" DENTRO de "Recibir"). Diagnóstico
confirmado contra la base de datos: el Paquete de Lais quedó con `snapshot_torre=TORRE 1`,
`snapshot_apartamento=302`, estado ENTREGADO -- pero cero Ocupantes en esa unidad, y su Persona
sin `apartamento_actual_id`. Mismo síntoma que [[148]], pero por la OTRA puerta: "Asignar
apartamento" (modal independiente, ícono propio en la fila de `/paquetes`) nunca tuvo ninguna
capacidad de registrar residente -- ni antes de [[148]] ni después, porque ese fix solo tocó el
modal "Recibir".

**Status:** implementado (el Paquete puntual de Lais quedó ENTREGADO -- terminal, ya no
corregible; ver "Nota sobre el caso reportado" abajo para cómo completarlo a mano)

## Diagnóstico

`assign_apartment_action` (`packages.py`) SIEMPRE llamó solo a `corregir_apartamento` -- que por
diseño (ver su propio docstring, ADR-0001) únicamente corrige el snapshot de dirección del
Paquete, nunca toca `Ocupante`. El modal "Asignar apartamento" (`_resultados.html`) nunca tuvo
campos de "¿A nombre de quién es?" -- ni siquiera candidatos numerados como sí llegó a tener
"Recibir" antes de [[148]]. Registrar a alguien como residente de la unidad recién asignada
siempre exigió una segunda visita a "Corregir destinatario" (documentado así en el propio
docstring de `corregir_apartamento`: "ampliada para poder asociar un residente nuevo desde
'Corregir destinatario' en Recibido").

## Fix

Mismo mecanismo que [[148]], aplicado al segundo punto de entrada:

- `assign_apartment_action`: nuevos campos opcionales `nuevo_ocupante_nombre`/
  `nuevo_ocupante_contacto`/`mover_de_otra_unidad`. Reusa `_resolver_desde_candidato` (la misma
  función compartida por Recibir y Corregir destinatario) pasando `candidato_idx="nuevo"` FIJO
  desde Python -- este modal nunca mostró candidatos numerados, así que no hay ningún índice que
  gestionar (más simple que el caso de Recibir en [[148]], que sí tuvo que preservar ese riesgo).
- Plantilla: sección `<details>` "+ Nuevo residente (opcional)" dentro del picker, mismo patrón
  visual que "+ Nueva persona" de `/announce`.

**Diferencia real y esperada con Recibir:** acá el Ocupante nuevo queda **pending**, no principal
-- "Asignar apartamento" no transiciona el Paquete (no es un "recibir" físico), así que no dispara
`promover_al_recibir` (el hook de auto-promoción vive en `paquete_lifecycle.receive()`, no en
`corregir_apartamento`). Confirmar/promover sigue un paso aparte (tab "Residentes" de
`/residentes`), igual que cualquier otro alta que no pase por recibir un paquete.

## Nota sobre el caso reportado (Lais Hernandez)

Su Paquete puntual ya está ENTREGADO -- fuera de `ESTADOS_CORREGIBLES`, ninguna de las dos rutas
(ni con este fix) puede tocarlo más. Para completar SU registro específico como residente: `/residentes`
→ su ficha → tab "Datos" (agregarle un Teléfono o WhatsApp -- `agregar_ocupante` lo exige para el
primer Ocupante de una unidad) → tab "Dirección" → asignar Torre 1 · Apto 302 (`reasignar_apartamento`
ya confirma y promueve a principal en el mismo acto, sin pasos extra). Para paquetes NUEVOS, el
fix de este ticket ya lo resuelve en un solo envío.

## Verificación

- `tests/web/test_packages.py::test_asignar_apartamento_registra_nuevo_residente_en_el_mismo_envio`
  (nuevo): asigna unidad + nuevo residente en un solo POST -- snapshot correcto, `recipient_name`
  corregido, Ocupante creado pending (NO principal, a diferencia de Recibir).
- `tests/web/test_packages.py::test_asignar_apartamento_sin_nuevo_residente_no_crea_ocupante`
  (nuevo): campo vacío -- cero Ocupantes, comportamiento idéntico a antes de este fix.
- Suite completa `/paquetes` + `/announce` + `/residentes`: 329/329, sin regresiones.
- Verificado en vivo contra `localhost:8010`: la sección "+ Nuevo residente (opcional)" aparece en
  el modal "Asignar apartamento" de paquetes reales sin unidad.

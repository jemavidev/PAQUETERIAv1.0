# 125 — Modal "Recibir paquete": quitar el badge de estado de ocupante

**Pedido original (cliente):**
"En el modal de 'Recibir paquete', necesito que que para la seccion
donde aparece el si los residentes estan 'pendientes, principales,
confirmados...' que se remueba esta badge o etiqueta, que solo aparezca
el nombre del residente y siga teniendo la funcionalidad de poder
seleccionar cualquiera de estos"

**Status:** implementado

## Implementación

- Revierte, SOLO para el modal "Recibir paquete" ([[121]] había agregado
  el mismo badge a los dos modales), la llamada a
  `badge_ocupante(c.estado_ocupante)` en la tarjeta de cada candidato --
  `components/_recibir_paquete.html`, dentro de `modal_recibir`. Queda
  solo `{{ c.nombre }}` en el `<span>`. Import de `badge_ocupante`
  eliminado del archivo (ya no se usa ahí).
- "Corregir destinatario" (`packages/_resultados.html`) CONSERVA el
  badge -- el pedido fue puntual sobre Recibir, no una reversión general
  de [[121]].
- La selección (radio real `name="candidato_idx"`, oculto tras
  `sr-only`) no se tocó -- sigue funcionando igual, solo cambia lo que
  se ve.

## Verificación

- `tests/web/test_packages.py`:
  `test_modal_recibir_candidatos_no_muestran_badge_de_estado_de_ocupante`
  reemplaza al test de [[121]] que esperaba el badge -- confirma que los
  3 nombres siguen presentes, que hay 5 radios `candidato_idx` (3
  ocupantes + Anunciante + "Nuevo residente"), y que "Principal"/
  "Confirmado"/"Pendiente" no aparecen cerca de cada nombre (ventana
  angosta, para no confundirse con el texto del JS de "+ Nuevo
  residente" más abajo en el mismo modal, que sí dice "Residente
  Principal de..." como parte de su aviso de conflicto).
  `test_modal_corregir_candidatos_muestran_badge_de_estado_de_ocupante`
  (Corregir destinatario) sigue pasando sin cambios.
- Playwright contra el servidor local real: tarjetas muestran solo el
  nombre, sin badge; clic en una tarjeta distinta marca su radio
  correctamente.
- Suite completa: 1010 passed.
- Pendiente: deploy a test.papyrus.com.co.

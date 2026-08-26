# 176 — `_buscar_residentes`: quitar la resolución "nombre de Ocupante → Principal de la unidad"

**Pedido original:** seguimiento a [[175]] -- "se ve mucho mejor, pero ya que corregiste el bug,
necesito ahora que no aparezcan las personas que estan relacionadas con ese apartamento, solo la
persona que busco ya que puedo por medio del boton de residentes que creaste ver quienes estan
asociados a una persona" -- ahora que existe "Agrupar por apartamento" ([[174]]) para ver a todos
los relacionados de una unidad, ya no hace falta que la búsqueda por texto infiera y muestre a
otras personas (el Principal) solo porque comparten unidad con quien matcheó -- el resultado debe
ser exactamente quien matchea el término, nada más.

**Status:** implementado

## Cambio

- `customers_manage.py` (`_buscar_residentes`): eliminado el tercer frente de búsqueda (nombre de
  Ocupante → resuelve al Principal ACTIVO de esa unidad). Quedan solo 2: (1) nombre o teléfono de
  la Persona misma, (2) Torre/Apartamento de su unidad. Docstring actualizado.
- **Efecto secundario aceptado, avisado al cliente:** un Ocupante SIN teléfono/WhatsApp propio (sin
  ficha propia, ej. un hijo menor solo con nombre) ya NO se puede encontrar por su nombre --
  antes resolvía al Principal de su unidad como sustituto; ahora no hay sustituto. Se acepta
  porque el caso de uso que cubría (encontrar la unidad por el nombre de un familiar) ya lo cubre
  "Agrupar por apartamento" partiendo de CUALQUIER persona con ficha propia de esa misma unidad.
- [[175]] queda sin efecto práctico: el bug que corrigió (Ocupante desvinculado "contaminando" la
  búsqueda) desaparece junto con el mecanismo completo que lo causaba. Se deja su registro tal
  cual (documenta el diagnóstico real, útil como referencia) -- no se marca inválido, el fix en sí
  seguía siendo correcto mientras el mecanismo existió.

## Tests afectados (`test_customers_manage.py`)

- `test_buscar_por_nombre_de_ocupante_sin_telefono_encuentra_al_principal` -- probaba EXACTAMENTE
  el mecanismo que se quita. Reescrito para confirmar el nuevo comportamiento (buscar por el
  nombre de un Ocupante sin ficha propia ya NO encuentra a nadie).
- `test_buscar_por_ocupante_desvinculado_no_trae_al_principal_de_la_unidad_donde_ya_no_vive`
  (issue 175) -- su escenario ya no es alcanzable (no hay mecanismo de resolución por Ocupante que
  desvincular). Eliminado.
- `test_resultados_no_se_duplican_si_varios_criterios_coinciden` -- su escenario de dedup
  dependía en parte del tercer frente (Ocupante sin teléfono resolviendo a la misma Persona que ya
  había matcheado por nombre directo). Revisado: sigue siendo válido como guard general de
  `encontradas.setdefault` aunque el segundo camino de match ya no aplique iguales.

## Verificación

- Suite completa: 300/300 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`): "dan" ahora trae SOLO a Daniela Arrazola -- ni Angelica
  ni Jesus.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

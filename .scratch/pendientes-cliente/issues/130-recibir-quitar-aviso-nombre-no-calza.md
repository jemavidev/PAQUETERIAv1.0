# 130 — Recibir: quitar el aviso "no está entre los residentes"

**Pedido original (cliente):**
"Este mensaje lo debes remover del modal de recibir paquetes '⚠️ El
destinatario declarado no está entre los residentes de esta unidad.'
esta de mas, ya se sobre entiende"

Revierte parcialmente [[127]]/[[128]]: se queda la lista de residentes
(chips, [[128]]) al declarar unidad desde Recibir, pero se quita el
aviso ámbar aparte que marcaba explícitamente si el destinatario no
calzaba con ninguno -- la lista de nombres ya lo deja ver por sí sola.

**Status:** verificado en test.papyrus.com.co

## Implementación

- `components/_recibir_paquete.html`, `pickerElegirTorre`: se quita
  toda la lógica de `avisoNombre` (comparación de
  `data-destinatario` contra los nombres, texto del aviso ámbar).
  `pickerLimpiarDesdeTorre` ya no lo limpia (elemento retirado).
- `components/_picker_apartamento.html`: se quita el `<p
  id="picker-aviso-nombre-*">` y el parámetro `destinatario_declarado`
  del macro `picker_apartamento` (y su atributo `data-destinatario` en
  el input).
- `_recibir_paquete.html`: la llamada a `picker_apartamento(...)` para
  Recibir ya no pasa `destinatario_declarado`.
- Bug propio encontrado (3ra vez en este mismo archivo): un comentario
  nuevo volvió a citar la frase "no coincide" (esta vez completa:
  "no coincide con el destinatario"), rompiendo en falso los mismos 3
  tests de `/paquetes` que ya se habían visto afectados en [[124]] y
  [[127]]. Reescrito evitando la frase.

## Verificación

- `tests/web/test_packages.py`:
  `test_modal_recibir_picker_expone_residentes_por_unidad` (renombrado
  desde la versión de [[127]]) -- confirma que `picker-aviso-nombre`
  ya NO aparece en el modal.
- `tests/web/test_announce_new.py`:
  `test_recibir_telefono_directo_picker_expone_residentes_por_unidad`
  (renombrado) -- ya no verifica `data-destinatario`.
- `tests/web/test_packages.py tests/web/test_announce_new.py
  tests/web/test_search.py`: 161 + 88 passed.
- Suite completa: 1016 passed.
- Pendiente: deploy a test.papyrus.com.co.

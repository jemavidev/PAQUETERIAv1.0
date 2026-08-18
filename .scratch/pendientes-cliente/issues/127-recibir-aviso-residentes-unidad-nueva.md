# 127 — Recibir: aviso si la unidad declarada ya tiene residentes

**Pedido original (cliente, pregunta exploratoria):**
"que posibilidad existe en que al recibir un paquete y no tenemos un
apartamento asociado, si ingresamos un apartamento que ya tiene
residentes, que sugieres que deberia parar, cual deberia ser el
comportamiento?"

Se presentaron 3 opciones (informativo sin bloquear / informativo +
aviso si el nombre no calza / con fricción extra tipo checkbox). El
cliente eligió la opción 2.

**Status:** verificado en test.papyrus.com.co

## Diagnóstico

Antes de este fix, Recibir con el picker liviano (`con_resumen=False`,
paquete sin apartamento) solo mostraba "✓ Torre X · Apto Y
seleccionado." -- sin importar si esa unidad ya tenía residentes
conocidos ni si el destinatario declarado coincidía con alguno. Riesgo
real de asociar el paquete a la unidad equivocada sin ninguna alerta.

## Implementación

- `ocupante_service.residentes_por_torre_apartamento` (ya existía para
  "Asignar apartamento") se reusa -- `announce_new.py` ahora también la
  llama y pasa `residentes_por_unidad` a su contexto (antes solo
  `packages.py` lo hacía).
- `components/_picker_apartamento.html`: el `<script>` JSON de
  residentes por unidad ya NO está condicionado a `con_resumen` (Recibir
  también lo necesita). Nuevo parámetro `destinatario_declarado` --
  viaja como `data-destinatario` en el input del Apartamento. En el modo
  liviano (`con_resumen=False`), 2 `<p>` nuevos: `picker-residentes-*`
  (lista de residentes o "Libre") y `picker-aviso-nombre-*` (ámbar,
  solo si hay residentes Y el destinatario no calza con ninguno).
- `components/_recibir_paquete.html`: `modal_recibir` gana
  `residentes_por_unidad=None`, lo pasa a `picker_apartamento(...)`
  junto con `destinatario_declarado=recipient_name`. JS de
  `pickerElegirTorre` (rama liviana) arma el mensaje de residentes y
  compara (mayúsculas, recortado) contra `data-destinatario`;
  `pickerLimpiarDesdeTorre` limpia los 2 elementos nuevos al reiniciar
  el picker. Nunca bloquea el submit -- puramente informativo, mismo
  criterio que el resto de la app (guía, Ocupante activo).
- `_resultados.html` y `announce_new/form.html`: sus llamadas a
  `modal_recibir(...)` pasan `residentes_por_unidad=residentes_por_unidad`.

## Verificación

- Bug propio encontrado al correr los tests: el texto real del aviso
  (no un comentario esta vez) usaba la frase "no coincide", que rompía
  en falso los mismos 3 tests de `/paquetes` que ya se habían visto
  afectados en issue 124 (el script de `recursos_recibir()` se incluye
  ahí también). Reescrito a "no está entre los residentes de esta
  unidad." -- se agregó una nota "OJO" en el código para no repetirlo
  una tercera vez.
- `tests/web/test_packages.py`:
  `test_modal_recibir_picker_expone_residentes_por_unidad_y_destinatario`
  -- confirma `data-destinatario`, los `<p>` nuevos, y el script JSON de
  residentes en el modal de Recibir.
- `tests/web/test_announce_new.py`:
  `test_recibir_telefono_directo_picker_expone_residentes_y_destinatario`
  -- mismo, para el modal de Recibir que abre `/announce`.
- Tailwind: nuevas clases (`text-amber-700`, etc.) -- rebuild +
  `?v=` de 47 a 48.
- Playwright contra el servidor local real: unidad con residentes +
  nombre que no calza → aviso ámbar visible sin bloquear el submit;
  unidad libre → "Libre -- sin residentes registrados.", sin aviso.
- Suite completa: 1016 passed.
- Pendiente: deploy a test.papyrus.com.co.

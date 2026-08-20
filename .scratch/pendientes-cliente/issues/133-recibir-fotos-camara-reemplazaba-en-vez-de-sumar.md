# 133 — Recibir: capturar varias fotos con la cámara reemplazaba en vez de sumar

**Pedido original (cliente):**
"veo en este momento que la funcionalidad para recibir con hasta 3
imagenes... desde el celular, solo permite capturar 1 imagen de las 3
posibles... si intento con la segunda, esta remplaza la primera que se
tomo, la idea es que puedan ser hasta 3 imagenes maximo. Analiza y dime
que flujos se compotan asi y como lo puedes corregir."

**Status:** implementado (skill `diagnosing-bugs`)

## Diagnóstico

`components/_carga_fotos.html` (macro `carga_fotos`) es el ÚNICO lugar
que ofrece carga de fotos en toda la app -- usado exclusivamente por
`modal_recibir` (`components/_recibir_paquete.html:293`), compartido
entre `/paquetes` y `/announce`. El bug afecta a los DOS flujos por
igual (mismo componente).

Causa raíz: el `<input type="file" capture="environment" multiple>`
hace que en mobile cada toque dispare la cámara del sistema para UNA
sola foto -- el navegador/SO SIEMPRE devuelve un `FileList` nuevo con
solo la foto recién tomada, sin memoria de capturas anteriores (ni
aunque el JS hubiera seteado `input.files` a mano antes). Hasta ahí es
una limitación de la plataforma, no corregible desde JS.

El bug real está en nuestro propio código: el listener de `change`
hacía `fijarArchivos(input.files)` -- **reemplazaba** toda la selección
con lo último capturado, en vez de sumarlo a lo ya tomado. El handler
de `drop` (arrastrar y soltar) sí sumaba correctamente
(`actuales.concat(nuevos)`) -- la inconsistencia entre los dos caminos
era la pista de que faltaba aplicar el mismo criterio en `change`.

## Corrección

- Nueva variable `acumulados` (persiste entre eventos `change`,
  independiente de `input.files` -- que la plataforma reemplaza en cada
  captura). Pasa a ser la única fuente de verdad para el render y el
  conteo; `input.files` queda como reflejo para el envío del form.
- `change`: ahora hace `fijarArchivos(acumulados.concat(nuevos))` en vez
  de reemplazar.
- `drop`: mismo cambio, por consistencia (funcionalmente ya sumaba,
  ahora lee de `acumulados` en vez de `input.files`).
- Quitar una foto (`data-quitar`): lee/escribe sobre `acumulados`.
- Sin cambios de alcance: el tope de 3 (`MAX`) se sigue aplicando igual
  (`nuevos.slice(0, MAX)` dentro de `fijarArchivos`) -- una 4ta captura
  con el cupo lleno simplemente no se agrega, mismo comportamiento de
  siempre.

## Verificación

- **Feedback loop** (skill `diagnosing-bugs`): script Playwright que
  simula 3 capturas de cámara SEPARADAS (`set_input_files` con UN solo
  archivo por llamada -- exactamente lo que hace `capture="environment"`
  en mobile, no un multi-select real) contra el servidor local real.
  Reproducido ANTES del fix: contador se quedaba en "1 de 3" tras las 3
  capturas, 1 sola miniatura visible. Confirmado DESPUÉS del fix: "1 de
  3" → "2 de 3" → "3 de 3", 3 miniaturas visibles.
- Casos adicionales verificados con el mismo script: una 4ta captura
  con el cupo lleno se ignora (se queda en "3 de 3", sin error); quitar
  una foto y volver a capturar deja el conteo coherente ("3 de 3" →
  quitar → "2 de 3" → capturar → "3 de 3").
- **Sin seam de pytest para esta regresión**: el bug es puramente de
  comportamiento JS/DOM (eventos `change`/`input.files` de un
  `<input type="file">`), y este repo no tiene infraestructura de
  navegador headless integrada a la suite de pytest (confirmado:
  ningún `playwright` en `pytest.ini`/dependencias de test) -- ningún
  test de Python puede ejercer esta ruta de verdad. El único test
  existente relacionado (`test_packages.py:548`) solo confirma que el
  atributo `capture="environment"` está presente en el HTML, no prueba
  el comportamiento de acumulación. Se documenta acá como la
  verificación real, siguiendo el mismo criterio que otros fixes
  puramente-JS de esta sesión (issues 124, 127).
- Suite completa de pytest: sin cambios esperados (el fix no toca
  ningún `.py`) -- se corre igual como red de seguridad.
- Servidor de desarrollo local reiniciado a mano durante la
  investigación: `uvicorn --reload` solo vigila archivos `.py` por
  defecto, un cambio de plantilla `.html` no dispara su propio reload
  -- hay que reiniciar el proceso a mano tras editar un `.html` para
  que el cambio se vea en `localhost:8010` (no es un bug de la app,
  es una característica del flag `--reload` de uvicorn -- documentado
  acá porque costó tiempo de depuración real en esta misma
  investigación).
- Pendiente: deploy a test.papyrus.com.co.

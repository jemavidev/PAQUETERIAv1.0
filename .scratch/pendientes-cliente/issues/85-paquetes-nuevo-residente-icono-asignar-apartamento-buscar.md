# 85 — `/paquetes`: ícono "Nuevo residente" + "Asignar apartamento" como búsqueda de un clic

**Pedidos originales (cliente), sobre [[84]]:**
1. "Necesito que en esta opcion '+ Es un nuevo residente de este
   apartamento' coloques un icono de color que diga 'Nuevo residente'".
2. "ahora necesito que para el boton de 'modal-asignar-apto-<id>' realices
   algo similar de eficiente que el boton para corregir residente,
   necesito que tenga un look and feel similar" → "posibilidades que
   tenga opciones para seleccionar asi como se corrigio la persona que
   anuncio, muestrame opciones" — 3 variantes prototipadas en vivo sobre
   `/paquetes` (`?variant_asignar=baseline|torre|buscar`); ganó C
   ("La opcion c es la mas rapida").

**Status:** implementado

## Implementación

- `packages/_resultados.html`, opción "Es un nuevo residente de este
  apartamento" (dentro de "Corregir destinatario"): ícono de "+" en
  círculo azul + texto corto "Nuevo residente", mismo layout ícono+texto
  que las tarjetas de candidatos (issue 84), distinguible por color
  (antes: texto gris apagado sin ícono).
- `packages/_resultados.html`, modal "Asignar apartamento": pasa de 2
  `<select>` en cascada a un solo campo de búsqueda sobre el catálogo
  completo -- escribir "302" o "Torre 3" filtra sugerencias "Torre X ·
  Apt Y" (hasta 8, construidas client-side desde el mismo JSON de
  catálogo que ya se enviaba); elegir una llena los campos ocultos
  `torre`/`apartamento` y envía el form de una vez
  (`form.requestSubmit()`). El botón de submit se queda `sr-only`
  (respaldo de teclado/accesibilidad, mismo patrón que
  `_busqueda_filtros.html` y la propia issue 84).
- `components/_recibir_paquete.html`: removida la cascada JS
  `data-torre-asignar`/`data-apto-asignar` (populaba el `<select>` de
  Apartamento según la Torre elegida) -- quedó muerta, ningún template
  la referencia ya.
- El prototipo completo de 3 variantes (select en cascada / Torre en
  tarjetas + select / búsqueda) queda archivado en la rama
  `prototype/asignar-apartamento-buscar`, fuera de `main`.

## Tests

- 1 test nuevo para el campo de búsqueda (`test_modal_asignar_apartamento_es_un_campo_de_busqueda`
  -- confirma que ya no hay `<select>` en ese modal y que los campos
  `torre`/`apartamento` siguen presentes por nombre).
- Los tests existentes de `asignar-apartamento` (backend, POST directo)
  no cambiaron -- ninguno dependía del widget del formulario.

## Verificación

- `tests/` completo: pasa (ver commit).
- Verificación manual vía HTTP (ambiente local): confirmado que el campo
  de búsqueda está presente, el `<select>` viejo y sus data-attrs ya no
  existen en el HTML, y el switcher del prototipo quedó completamente
  removido.
- Pendiente: deploy a test.papyrus.com.co.

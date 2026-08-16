# 88 — `/paquetes` "Asignar apartamento": flujo guiado de 3 pasos (reemplaza el campo de búsqueda libre)

**Pedido original (cliente):**
"sigue igual de mal, para esto hagamos o tomemos otro camino, mejor
primero voy a digitar SOLAMENTE el numero de apartamento y despues de
digitar los 3 digitos me vas a mostrar las 10 torres posibles, luego
despues de seleccionar una torre, me mostraras los residentes de esa
torre y apartamento en caso que existan o mostraras que esta libre ese
apartamento. Recuerda que esto es solo para tener una opcion eficiente
para seleccionar torre y apartamento o apartamento y torre, pero la
realidad que la informacion que se cruce hace referencia a esto
<TorreApartamento> ejemplO: 10203."

Después de 2 rondas fallidas del campo de búsqueda libre ([[87]]), el
cliente pidió abandonar ese enfoque y construir un flujo guiado de
pasos explícitos en su lugar.

**Status:** implementado

## Implementación

`packages/_resultados.html`, modal "Asignar apartamento" -- reemplaza
por completo el campo de búsqueda libre por 3 pasos:

1. **Apartamento**: un solo input numérico (`inputmode="numeric"`,
   filtra cualquier no-dígito al escribir). El catálogo real NO es
   siempre 3 dígitos -- pisos 10 y 11 usan 4 (ej. "1001"-"1102") --
   verificado contra la base antes de programar: ningún número completo
   de 3 dígitos es AL MISMO TIEMPO prefijo de uno de 4, así que un match
   EXACTO (no por prefijo) contra el catálogo, recalculado en cada
   tecla, resuelve ambos casos sin ambigüedad ni resultados prematuros.
2. **¿Cuál Torre?**: en cuanto el número escrito calza EXACTO con al
   menos una unidad real, aparecen tarjetas de un clic SOLO para las
   Torres donde ese número realmente existe (no siempre las 10 -- ej. el
   piso 9 completo, "908", solo existe en 6 de las 10 Torres; mostrar
   las 10 igual habría llevado a combinaciones inválidas).
3. **Resumen + confirmar**: al elegir una Torre, aparece "Torre X · Apt
   Y" + la lista COMPLETA de residentes actuales (o "Libre -- sin
   residentes registrados") + un botón "Asignar apartamento" visible --
   a propósito NO se auto-envía al elegir la Torre (a diferencia de
   [[85]]/[[86]]): el punto explícito de este pedido es poder revisar
   quién vive ahí ANTES de comprometerse a la asignación.

Cambiar el número de Apartamento en cualquier momento reinicia los
pasos 2 y 3 (nunca queda una Torre/resumen viejo mostrando datos que ya
no aplican al número recién escrito).

La rama `prototype/asignar-apartamento-buscar` (issue 85) y los 2
commits del campo de búsqueda libre (issues 86/87) quedan como
referencia histórica de ese intento -- ya no es el código que corre acá.

## Por qué las rondas anteriores fallaron (auto-crítica)

- **Issue 87, ronda 1**: solo probé la función de match aislada con
  Node, nunca contra el navegador real -- no atrapé que "torre 3"
  mostraba TORRE 1 (el dígito de Apartamento se confundía con el de
  Torre).
- **Issue 87, ronda 2**: usé Playwright, pero solo verifiqué el caso
  feliz antes de anunciar que estaba listo -- el cliente probó por su
  cuenta y confirmó que seguía mal, sin decirme exactamente qué
  reproducía. Terminé pidiendo cambiar de enfoque en vez de seguir
  parchando el mismo campo de texto libre.
- **Esta ronda**: Playwright contra el flujo COMPLETO (1 dígito → sin
  resultados; 3 dígitos → tarjetas de Torre; Torre ocupada → residentes
  completos; Torre libre → "Libre"; confirmar → la fila de la tabla
  refleja la unidad asignada de verdad; caso de 4 dígitos piso 10 →
  solo las Torres válidas) ANTES de reportar que funciona.

## Tests

- `test_modal_asignar_apartamento_es_flujo_guiado_de_3_pasos`
  (reemplaza el test de la ronda anterior que asumía un campo de
  búsqueda): confirma los 3 ids del wizard, ausencia de `<select>`, y
  los campos `torre`/`apartamento` del form.

## Verificación

- Playwright (Chromium headless) contra el servidor local real, con
  capturas en cada paso: 1 dígito (sin resultados), 3 dígitos (10
  tarjetas de Torre), Torre ocupada (5 residentes completos visibles),
  Torre libre ("Libre -- sin residentes registrados"), confirmar
  (la fila de /paquetes refleja "TORRE 5 · APT 302" después del clic),
  y el caso de 4 dígitos ("1001", piso 10 -- solo 8 Torres válidas, ni
  Torre 1 ni Torre 10 tienen esa unidad).
- `tests/web/test_packages.py` completo: 95 tests pasan.

## Ajuste posterior -- residentes como lista

"MUCHO mejor, ahora en ese mismo modal quiero que muestres los
residentes en caso que existan pero en forma de lista, similar a como
se hace en los otros modales" -- el resumen del paso 3 mostraba los
nombres en un solo texto corrido separado por comas; pasa a una lista
(ícono de persona + nombre por fila), mismo patrón visual que
"Residentes de la unidad" del modal Ver. Verificado con Playwright
(captura real). Sin cambios de backend ni de tests server-rendered
(la lista se construye en el mismo JS del paso 3).

- Pendiente: deploy a test.papyrus.com.co.

# 87 — `/paquetes` "Asignar apartamento": bug de búsqueda (se vaciaba al escribir el apartamento) + buscar por nombre de residente

**Pedido original (cliente):**
"si se ve que se busca, pero solo la torre, al empezar a digitar el
apartamento se eliminan los datos posibles que se estaban mostrando, la
idea es que se muestren todos los posibles, la idea es optimizar esto
para ver incluso los residentes que existan en un apartamento
seleccionado (digitado), con el fin de asignar a la persona correcta al
apartamento correcto, analiza el como lo haces y como se puede hacer
esto"

**Status:** implementado

## Diagnóstico (ronda 1)

El buscador de [[85]]/[[86]] comparaba la QUERY COMPLETA como un solo
substring contiguo contra la etiqueta `"TORRE X · Apt Y"`
(`etiqueta.indexOf(q)`). En cuanto el staff escribía algo que calzaba
con la Torre (ej. "torre 3") y seguía tecleando el número del
apartamento en el MISMO campo (ej. "torre 3 302"), la cadena completa
ya no era substring contiguo de la etiqueta -- el " · Apt " literal de
en medio rompe la continuidad -- así que los resultados se vaciaban
apenas se empezaba a escribir el apartamento.

## Ronda 2 -- el fix de la ronda 1 quedó incompleto

El cliente probó en su propio navegador y reportó que seguía mal
("no entendiste lo que quiero o no lo hiciste"). Verifiqué con
Playwright (headless real, no solo análisis estático) reproduciendo la
escritura exacta -- y confirmé que SÍ había un bug residual real: el
match por tokens de la ronda 1 comparaba cada palabra como substring
EN CUALQUIER PARTE de una bolsa de texto (`bolsa.indexOf(t)`), sin
distinguir "número de Torre" de "número de Apartamento" -- ambos son
solo dígitos sueltos. Escribir "torre 3" hacía calzar el token "3"
contra apartamentos como "103", "203", "303" de OTRAS torres (el
dígito "3" aparece ahí como substring), así que el resultado mostraba
**TORRE 1** en vez de TORRE 3. "torre 3 302" mezclaba TORRE 1/10/2/3,
todos con Apt 302, porque "302" también calzaba en cualquier torre y
"3" seguía sin distinguir Torre de Apartamento.

## Implementación (versión final, ronda 2)

- `packages/_resultados.html`, JS del buscador: parser consciente de
  los campos, no un match a ciegas contra un texto pegado. Se extrae
  explícitamente el número de Torre con `/torre\s*(\d{1,2})/` -- si
  aparece, filtra por ESE número EXACTO de Torre (nunca por substring).
  El resto de lo escrito se interpreta por token: dígitos buscan por
  **prefijo** del número de Apartamento (`apto.indexOf(t) === 0`, no
  "contiene"), letras buscan por substring en los nombres de
  residentes actuales de esa unidad.
- Cada resultado muestra los residentes **completos, sin truncar**, en
  una segunda línea -- chip de estado a la derecha ("N residentes" /
  "Libre"). Buscar por el nombre de un residente (ej. "mariana")
  también encuentra su unidad, sin necesidad de saber Torre/Apto de
  memoria -- efecto directo del pedido "asignar a la persona correcta
  al apartamento correcto".
- Tope de resultados: 10.

## Verificación

- **Ronda 1** (insuficiente): solo aislé la función de match con Node,
  sin probar contra el navegador real -- por eso no atrapé el bug
  residual de confundir dígitos de Torre con dígitos de Apartamento.
- **Ronda 2** (real): usé Playwright (Chromium headless) contra el
  servidor local de verdad -- login, abrir el modal, escribir
  exactamente como lo describió el cliente ("torre 3", luego
  " 302"), capturar pantalla en cada paso. Confirmé el bug (TORRE 1
  apareciendo al buscar "torre 3") y luego la corrección (solo TORRE 3
  aparece; "torre 3 302" da un único resultado con sus 5 residentes
  completos; "mariana" encuentra la misma unidad por nombre; clic en
  un resultado asigna de verdad -- confirmado viendo "TORRE 3 · APT
  302" en la fila de MARIANA RESTREPO después del clic).
- `tests/web/test_packages.py` completo: 95 tests pasan (estructura
  server-rendered del modal no cambió -- el bug era 100% client-side,
  sin cobertura automatizada de JS en este proyecto).
- Pendiente: deploy a test.papyrus.com.co.

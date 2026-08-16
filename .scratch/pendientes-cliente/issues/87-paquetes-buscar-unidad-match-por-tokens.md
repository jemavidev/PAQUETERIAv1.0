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

## Diagnóstico

El buscador de [[85]]/[[86]] comparaba la QUERY COMPLETA como un solo
substring contiguo contra la etiqueta `"TORRE X · Apt Y"`
(`etiqueta.indexOf(q)`). En cuanto el staff escribía algo que calzaba
con la Torre (ej. "torre 3") y seguía tecleando el número del
apartamento en el MISMO campo (ej. "torre 3 302"), la cadena completa
ya no era substring contiguo de la etiqueta -- el " · Apt " literal de
en medio rompe la continuidad -- así que los resultados se vaciaban
apenas se empezaba a escribir el apartamento. Bug real, no percepción:
reproducido con Node aislando la función de match antes de tocar la
plantilla.

## Implementación

- `packages/_resultados.html`, JS del buscador: cambia de "toda la
  query como un bloque" a **match por tokens** -- la query se separa por
  espacios y CADA palabra debe aparecer (en cualquier orden, en
  cualquier parte) en una "bolsa de texto" por unidad que ahora incluye
  Torre + Apartamento + **los nombres de todos sus residentes actuales**
  (antes solo comparaba contra la etiqueta Torre/Apto). Efecto directo
  del pedido "asignar a la persona correcta al apartamento correcto":
  escribir el nombre de quien ya vive ahí también encuentra la unidad,
  no hace falta saber el número de memoria.
- Cada resultado ahora muestra los residentes **completos, sin
  truncar** en una segunda línea (antes: solo el primer nombre + "+N" en
  el `title`, había que pasar el mouse para ver el resto) -- chip de
  estado a la derecha resumido como "N residentes" / "Libre".
- Tope de resultados sube de 8 a 10 (más margen ahora que el match es
  más preciso).

## Verificación

- Aislé la función de match con Node y confirmé el bug original
  ("torre 3 302" contra la etiqueta antigua fallaba) y la corrección
  ("torre 3 302", "mariana", "302" contra la nueva bolsa de texto
  calzan correctamente).
- `tests/web/test_packages.py` completo: 95 tests pasan (estructura
  server-rendered del modal, no cambió -- el bug era 100% client-side).
- Pendiente: deploy a test.papyrus.com.co (ahí sí se puede probar la
  interacción en un navegador real).

# 84 — `/paquetes`: campo Anuncio, advertencia clickeable, regla de anunciar por co-residentes, candidatos de un clic

**Pedidos originales (cliente), varias rondas seguidas sobre [[83]]:**
1. "en la vista /paquetes, el modal de clientes en la seccion de
   'Destinatario', seria bueno saber como se anuncio el paquete... esto
   deberia ser enfocado a mostrar donde se recibira esta notificacion...
   literal mostrar siempre donde se recibira la notificacion del anuncio."
2. "existe la posibilidad de hacer scroll dentro de un modal sin
   visualizar la barra lateral" — scroll interno de los modales sin barra
   visible.
3. "vamos a trabajar en el boton de esta vista que hace referencia a 'El
   nombre anunciado no coincide con el registrado', necesito que este
   boton sea clickeable y que me redirija al modal 'Corregir
   destinatario'".
4. "el flujo hoy en dia debe ser que: solo personas de un apartamento
   especifico... podran anunciar a nombre de otros, en caso que no
   pertenezca a los residentes de ese apartamento, entonces no podra
   anunciar para el mismo, por otro lado si esta persona intenta anunciar
   y no tiene apartamento asociado, entonces se realizara el anuncio pero
   como una persona individual." — confirmado en vivo: aplica solo a
   `/anunciar` (no a `/announce` de staff), y el bloqueo es silencioso
   (auto-corrige a individual, sin mensaje de error).
5. "Quiero que este modal sea lo mas interactivo posible... para esta
   seleccion de la persona correcta para anunciar un paquete sea con la
   menor cantidad de click posibles" — prototipado en vivo con 3
   variantes reales sobre `/paquetes` (`?variant=select|click|confirm`);
   ganó B ("Creo que la opcion B se ve perfecto").

**Status:** implementado

## Implementación

- `packages/_resultados.html`, sección "Destinatario" del modal Ver:
  nuevo campo "Anuncio" (reemplaza el "Teléfono" condicional) -- SIEMPRE
  muestra algo: el teléfono propio del destinatario si lo tiene, si no
  cae al teléfono o WhatsApp de quien anunció (mismo fallback que usa el
  envío real de SMS, `notificacion_service.resolver_destino_notificable`).
- `components/_modales.html` + `static/css/input.css`: nueva utilidad
  `.scrollbar-none` (Firefox/IE por propiedad, WebKit por pseudo-elemento)
  en el contenedor scrolleable de `modal()`/`modal_confirmacion()`.
- `packages/_resultados.html`, columna Cliente: el ícono de advertencia
  ("el nombre anunciado no coincide") ahora es un botón con
  `data-open="modal-correct-<id>"` -- abre "Corregir destinatario"
  directo, solo mientras el paquete sigue ANUNCIADO (fuera de ese estado
  el modal ni existe, ADR-0001 ya congeló el snapshot).
- `domain/paquete_service.py`, `announce()`: el fallback de
  `Destinatario.declarado_por_cliente` (único consumidor: `/anunciar`) ya
  NO acepta un nombre arbitrario -- solo se honra si coincide con un
  co-residente YA CONOCIDO de la MISMA unidad del Anunciante
  (`_resolver_ocupante_por_nombre`, ya existía); sin esa unidad o sin esa
  coincidencia, el anuncio queda a nombre del propio Anunciante. No
  afecta `/announce` (staff), que sigue con su propia autorización por
  sesión.
- `packages/_resultados.html`, modal "Corregir destinatario": los
  candidatos pasan de `<select>` + botón "Guardar corrección" a tarjetas
  de un clic (cada una ES el submit). Prototipado en vivo con 3
  variantes reales (`?variant=select|click|confirm` sobre `/paquetes`) --
  el prototipo completo (las 3 + su switcher) queda archivado en la rama
  `prototype/corregir-destinatario-candidatos`, fuera de `main`.

## Tests

- 3 tests nuevos para "Anuncio" (teléfono propio / cae a teléfono del
  Anunciante / cae a WhatsApp del Anunciante).
- 2 tests nuevos para la advertencia clickeable (clickeable en Anunciado
  / plana fuera de Anunciado).
- 2 tests actualizados + 1 nuevo para la regla de co-residentes en
  `announce()` (los que simulaban un nombre no coincidente vía
  `declarado_por_cliente` se movieron a `solo_nombre`, que sigue sin
  restricción -- son pruebas de OTRAS features, como la advertencia y el
  filtro `q`, no de esta regla).
- 1 test actualizado + 1 nuevo para las tarjetas de un clic.

## Verificación

- `tests/` completo: 916 tests pasan (913 + 3 netos nuevos de esta
  ronda).
- Verificación manual en navegador (ambiente local) para el switcher del
  prototipo (las 3 variantes renderizan sin error 500, con el markup
  esperado cada una) y para el caso "advertencia clickeable" (candidato
  automático detectado correctamente por nombre).
- Pendiente: deploy a test.papyrus.com.co.

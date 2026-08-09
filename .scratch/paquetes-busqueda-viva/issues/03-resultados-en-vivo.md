# 03 — Resultados en vivo (fetch + debounce + fragmento reusable)

**What to build:** Los resultados de `/paquetes` (tarjetas + paginación) se actualizan solos,
sin recargar la página, mientras el staff escribe en el campo de búsqueda (debounce ~300ms)
o toca un ícono de Estado/reseteo — reemplazando el submit tradicional de los tickets 01/02
por peticiones `fetch` en segundo plano (JS vanilla, sin librerías nuevas).

El backend extrae la porción de tarjetas+paginación de `packages/list.html` a una plantilla
Jinja reusable, incluida tanto por la carga normal de página como devuelta SOLA cuando la
petición es AJAX (detectada por un header/convención que el JS adjunta a cada petición en
vivo). Un `AbortController` por petición en vuelo cancela la anterior si el staff sigue
escribiendo antes de que responda, evitando que una respuesta vieja y lenta sobrescriba una
más nueva.

Como el fragmento se reemplaza dinámicamente, los `data-open`/`data-close` de los modales de
acción (Recibir/Entregar/Cancelar/Corregir) y el anti-doble-envío de esos `<form>` — hoy
enlazados una sola vez al cargar la página — se convierten a delegación de eventos sobre un
contenedor estable, para que las tarjetas que llegan por una actualización en vivo conserven
sus acciones. Sin JavaScript, Enter en el campo de texto sigue funcionando como el submit
normal heredado de los tickets 01/02 (recarga completa, sin fragmento).

La paginación NO entra al circuito de `fetch` en vivo (sigue siendo navegación normal), pero
como vive dentro del mismo fragmento que se re-renderiza en cada búsqueda, sus enlaces
siempre reflejan el texto/Estado vigente.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] La porción de tarjetas + paginación de `packages/list.html` se extrae a una plantilla
      reusable, incluida por la carga normal de página.
- [ ] La ruta `/paquetes` devuelve SOLO ese fragmento cuando la petición trae la
      marca/convención AJAX, y la página completa en carga normal.
- [ ] Escribir en el campo de texto actualiza los resultados sin recargar la página, con
      debounce ~300ms.
- [ ] Clic en un ícono de Estado o en el de reseteo actualiza los resultados sin recargar la
      página (sin debounce — no es tecleo).
- [ ] Una petición en vuelo se cancela (`AbortController`) si el staff sigue escribiendo
      antes de que responda — no hay condición de carrera visible con respuestas fuera de
      orden.
- [ ] Los botones Recibir/Entregar/Cancelar/Corregir siguen abriendo su modal correctamente
      en tarjetas que llegaron por una actualización en vivo, no solo en las de la carga
      inicial.
- [ ] El anti-doble-envío de los `<form>` de acción sigue funcionando en tarjetas llegadas
      por una actualización en vivo.
- [ ] Sin JavaScript, Enter en el campo de texto sigue devolviendo resultados correctos
      (recarga completa, comportamiento heredado de 01/02).
- [ ] Los enlaces de paginación dentro del fragmento reflejan el texto/Estado vigente en el
      momento de la búsqueda.
- [ ] Test HTTP en `tests/web/test_packages.py`: la petición con la marca AJAX devuelve solo
      el fragmento (por ejemplo, no incluye el `<h1>Paquetes` de la página completa); la
      petición normal sigue devolviendo la página completa.
- [ ] Verificación manual en navegador (skill `run`): la búsqueda se siente en vivo y rápida
      tecleando, los íconos de Estado/reseteo actualizan sin recargar, y las acciones
      (Recibir/Entregar/Cancelar/Corregir) funcionan sobre resultados que llegaron por una
      actualización en vivo.
- [ ] Suite completa (`pytest`) pasa.

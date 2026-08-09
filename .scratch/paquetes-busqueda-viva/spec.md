# Búsqueda unificada y en vivo para `/paquetes`

Status: ready-for-agent

## Problem Statement

En `/paquetes` (vista de staff, principal del día a día operativo) la barra de búsqueda hoy
ocupa dos filas: una fila de chips de texto para el Estado (Todos/Anunciado/Recibido/
Entregado/Cancelado) y una segunda fila con tres cajas separadas — texto libre, Torre,
Apartamento — más un botón "Consultar". Para encontrar un Paquete por su unidad, el staff
tiene que llenar dos cajas más además del texto libre, y siempre debe presionar el botón y
esperar una recarga completa de la página para ver el resultado.

Además, el texto libre de hoy no cubre todos los datos por los que el staff naturalmente
reconoce a un residente — no busca por el nombre registrado del Anunciante (distinto del
nombre del destinatario que sí busca) ni por su usuario de WhatsApp, y Código de
acceso/Guía solo hacen match exacto, así que un dato recordado a medias no encuentra nada.

## Solution

Una sola línea de búsqueda en desktop: un campo de texto libre que busca contra todos los
datos relevantes de un Paquete a la vez (con coincidencia parcial), más un filtro de Estado
representado como íconos de color (reusando la paleta de badges ya aprobada), un ícono de
reseteo, y sin botón de envío — los resultados (tarjetas + paginación) se actualizan solos
mientras el staff escribe o toca un ícono, sin recargar la página.

Mobile queda fuera de esta iteración (ver Out of Scope) — se aborda como una iteración
separada posterior a esta.

## User Stories

1. Como miembro del staff en `/paquetes`, quiero un solo campo de búsqueda, para no tener
   que decidir en qué caja separada va cada dato que recuerdo del paquete.
2. Como miembro del staff, quiero que ese campo encuentre un Paquete por Código de acceso,
   Guía, nombre del destinatario, nombre registrado del Anunciante, usuario de WhatsApp del
   Anunciante, teléfono (del Anunciante o del Destinatario), Torre o Apartamento, para no
   tener que recordar exactamente cuál de esos datos tengo a mano.
3. Como miembro del staff, quiero que la búsqueda encuentre resultados aunque solo recuerde
   una parte del Código de acceso o de la Guía, para no depender de tener el dato completo y
   exacto.
4. Como miembro del staff, quiero ver los resultados actualizarse mientras escribo, sin tener
   que presionar un botón ni esperar una recarga completa de la página, para encontrar un
   paquete más rápido durante la atención de un residente o transportador.
5. Como miembro del staff, quiero filtrar por Estado con un clic sobre un ícono de color, para
   no tener que leer etiquetas de texto largas para encontrar el estado que busco.
6. Como miembro del staff, quiero poder quitar el filtro de un Estado ya activo con un
   segundo clic sobre el mismo ícono, para volver a ver todos los estados sin perder lo que
   ya había escrito en el campo de texto.
7. Como miembro del staff, quiero un ícono de reseteo que borre el texto y el filtro de
   Estado a la vez, para empezar una búsqueda nueva de un solo clic cuando ya no me sirve
   nada de lo que había filtrado.
8. Como miembro del staff, quiero que la paginación (página 2, 3…) siga funcionando y respete
   el texto/Estado que tengo filtrado en ese momento, para no perder el filtro al navegar
   entre páginas de resultados.
9. Como miembro del staff con JavaScript deshabilitado o fallando, quiero que presionar Enter
   en el campo de texto siga funcionando como una búsqueda normal (con recarga de página),
   para no quedarme sin poder buscar si el JS no carga.
10. Como miembro del staff, quiero que cada tecla que escribo no dispare inmediatamente una
    petición al servidor, para no generar tráfico innecesario ni resultados que lleguen
    desordenados mientras sigo escribiendo.

## Implementation Decisions

### Backend — `app/web/routes/packages.py`

- **`_listar`**: se elimina el filtro separado de `torre`/`apartamento` (parámetros y lógica).
  El único criterio de texto libre (`q`) pasa a cubrir, todos combinados con `OR` y todos con
  coincidencia parcial (`ILIKE '%valor%'`, incluyendo Código de acceso y Guía, que hoy son
  match exacto):
  - `Paquete.access_code`
  - `Paquete.guide_number`
  - `Paquete.recipient_name`
  - `Persona.nombre` (el Anunciante — requiere `outerjoin` desde `Paquete.announced_by_persona_id`
    hacia `Persona.id`, que hoy no existe en esta consulta)
  - `Persona.whatsapp_usuario` (mismo join)
  - `Paquete.announced_by_phone` / `Paquete.recipient_phone` (se mantiene el intento de
    normalizar `q` como teléfono, igual que hoy)
  - `Paquete.snapshot_torre`
  - `Paquete.snapshot_apartamento`
  - El filtro de `estado` no cambia: se sigue combinando con `AND` sobre el resultado del `OR`
    de arriba.
- **`packages_list`**: se eliminan los parámetros `torre`/`apartamento` de la firma de la ruta
  y de `_render_lista`.
- **Fragmento reusable**: la porción de la vista que hoy son las tarjetas (`<ul>` de
  `tarjeta_paquete`, o el estado vacío) más los dos bloques de `paginacion` (arriba y abajo)
  se extrae a una plantilla Jinja propia (`packages/_resultados.html`), incluida tanto por
  `packages/list.html` (carga normal de página) como devuelta *sola* cuando la petición es
  AJAX. La detección de petición AJAX usa un header estándar de `fetch` (p. ej.
  `X-Requested-With`) que el JS del cliente adjunta a cada petición en vivo — la carga normal
  de página (sin ese header) sigue devolviendo la página completa igual que hoy.
- La condición del estado vacío (`filtro_estado or filtro_q or filtro_torre or
  filtro_apartamento`) se simplifica a `filtro_estado or filtro_q`.

### Frontend — `components/_busqueda_filtros.html` + `packages/list.html`

- La barra pasa a una sola fila: ícono de lupa + campo de texto único (sin cajas de Torre/
  Apartamento) + 4 íconos de Estado + 1 ícono de reseteo. Sin botón de envío.
- **Íconos de Estado**: 4 círculos sólidos (Anunciado/Recibido/Entregado/Cancelado), reusando
  la MISMA paleta ya fijada para los badges de estado (ámbar/azul/esmeralda/rojo, ver
  `docs/design-system/tokens.md` sección 6/7). Cada uno con `aria-label`/`title` con el nombre
  del estado (accesibilidad, ya que no llevan texto visible). No existe un ícono "Todos" — la
  ausencia de cualquier ícono activo ES "todos los estados".
- **Toggle de Estado**: un clic sobre un ícono inactivo lo activa (y desactiva cualquier otro
  Estado activo — sigue siendo selección única); un clic sobre el ícono YA activo lo
  desactiva, volviendo a "todos los estados" sin tocar el texto de búsqueda.
- **Ícono de reseteo**: un clic limpia el campo de texto Y cualquier Estado activo a la vez,
  y dispara la búsqueda resultante (lista sin filtrar).
- El `<form>` GET existente se conserva por debajo (mismo `action="/paquetes"`, mismos
  nombres de campo `q`/`estado`) como *fallback* sin JS: Enter en el campo de texto sigue
  siendo un GET normal con recarga completa.

### JavaScript (vanilla, sin librerías nuevas)

- Un listener de `input` sobre el campo de texto, debounced ~300ms.
- Un listener de `click` sobre cada ícono de Estado (aplica el toggle descrito arriba) y sobre
  el ícono de reseteo — disparan la búsqueda de inmediato (sin debounce, ya que no es tecleo).
- Cada disparo construye la URL de `/paquetes` con los parámetros vigentes (`q`, `estado`) y
  hace `fetch` con el header AJAX; la respuesta (el fragmento) reemplaza el contenedor de
  resultados actual vía `innerHTML`.
- Un `AbortController` por petición en vuelo: si el usuario sigue escribiendo antes de que
  la petición anterior responda, esa petición se cancela — evita que una respuesta vieja y
  lenta sobrescriba una más nueva.
- Los `data-open`/`data-close` de los modales de acción (Recibir/Entregar/Cancelar/Corregir)
  hoy se enlazan una sola vez al cargar la página (`querySelectorAll(...).forEach(...)`) — como
  el fragmento se reemplaza dinámicamente, esos listeners deben convertirse a delegación de
  eventos sobre un contenedor estable (o volver a enlazarse tras cada reemplazo), para que las
  tarjetas nuevas conserven sus acciones. Aplica lo mismo al listener de "anti doble-envío" de
  los `<form>` dentro de las tarjetas.
- No se sincroniza la URL del navegador (`history.pushState`/`replaceState`) con el estado de
  búsqueda en vivo — los enlaces de paginación (ver abajo) ya llevan los parámetros vigentes
  porque se re-renderizan dentro del mismo fragmento.

### Paginación

- Sin cambio de mecanismo: los enlaces de `paginacion(...)` siguen siendo navegación normal
  (recarga completa de página), no entran al circuito de `fetch` en vivo.
- Los parámetros que preserva (`params={...}`) se reducen a `estado`/`q` (se quitan `torre`/
  `apartamento`, ya inexistentes). Como la paginación vive dentro del mismo fragmento que se
  re-renderiza en cada búsqueda en vivo, los enlaces que ve el staff siempre reflejan el
  texto/Estado vigente en ese momento, aunque la navegación en sí recargue la página.

## Testing Decisions

- Un buen test acá verifica comportamiento observable por HTTP (qué aparece o no en la
  respuesta), no la forma interna de la query SQL — mismo criterio que ya sigue
  `tests/web/test_packages.py`.
- **Seam preferido: HTTP a través de `TestClient`** (`client.get("/paquetes", params={...})`),
  el mismo que ya usan `test_filtro_por_estado`, `test_filtro_por_q_encuentra_por_*`,
  `test_filtro_por_torre_y_apartamento` y `test_filtros_combinados` en
  `tests/web/test_packages.py` — se extiende ese mismo archivo, no se crea un seam nuevo.
- Casos a cubrir en `test_packages.py`:
  - `q` encuentra por cada uno de los 8 criterios por separado (extender/reemplazar los tests
    de `torre`/`apartamento` que hoy usan parámetros propios, ya que esos parámetros
    desaparecen de la ruta).
  - `q` con coincidencia PARCIAL de Código de acceso y de Guía (antes exacto).
  - `q` encuentra por el nombre registrado del Anunciante (Persona.nombre) cuando difiere del
    nombre del destinatario, y por su `whatsapp_usuario`.
  - Filtro de Estado combinado con `q` (equivalente al `test_filtros_combinados` existente,
    ajustado a los nuevos parámetros).
  - La petición con el header AJAX devuelve SOLO el fragmento (no incluye el `<h1>Paquetes`
    de la página completa, por ejemplo), y la petición normal sigue devolviendo la página
    completa.
  - Los parámetros `torre=`/`apartamento=` ya no son aceptados por la ruta (o se ignoran sin
    romper — a decidir por quien implemente, ver Further Notes).
- **Fuera de la suite automatizada**: el comportamiento de JavaScript (debounce, `fetch`,
  cancelación con `AbortController`, toggle visual de los íconos, que los modales de acción
  sigan funcionando tras un reemplazo de fragmento) no es verificable con `pytest`/
  `TestClient` — se verifica manualmente lanzando la app y probando en navegador (skill
  `run`), como paso de validación antes de dar el ticket por cerrado.

## Out of Scope

- Versión mobile de esta barra (layout de una sola línea en pantallas angostas) — queda para
  una iteración posterior, a definir cuando se retome.
- Sincronizar la URL del navegador con el estado de búsqueda en vivo (bookmarks, back/forward
  del navegador reflejando cada búsqueda).
- Que la paginación entre al circuito de `fetch` en vivo (queda como recarga normal).
- Cualquier cambio a `/residentes` u otra vista — aunque comparten paleta de badges, esta
  spec no toca esas vistas ni el componente `_busqueda_filtros.html` más allá de lo que usa
  `/paquetes` (es el único lugar que lo invoca hoy).

## Further Notes

- Quien implemente decide el detalle visual exacto del ícono de reseteo (p. ej. una flecha
  circular tipo "refrescar" vs. una "X"); no fue una decisión explícita del cliente, solo que
  exista y limpie texto+Estado juntos.
- El nombre exacto del header/convención usada para detectar petición AJAX (p. ej.
  `X-Requested-With: fetch`, o un query param `?fragmento=1`) queda a criterio de
  implementación — no fue una decisión explícita, solo que exista una forma de distinguir la
  petición JS de la carga normal de página.
- Revisado contra `CONTEXT.md` y las ADRs 0001/0003/0005/0006: esta spec no toca el modelo de
  datos, el snapshot inmutable del Paquete, ni la identidad por Teléfono — es un cambio de
  capa de presentación/consulta sobre datos ya existentes, sin conflicto con ninguna ADR.

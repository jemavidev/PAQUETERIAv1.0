# 02 — Íconos de Estado con toggle + ícono de reseteo

**What to build:** El filtro de Estado de `/paquetes` deja de ser chips de texto
("Todos"/"Anunciado"/"Recibido"/"Entregado"/"Cancelado") y pasa a 4 íconos circulares de
color sólido (Anunciado/Recibido/Entregado/Cancelado), reusando la misma paleta ya aprobada
para los badges de estado (ámbar/azul/esmeralda/rojo — `docs/design-system/tokens.md`
sección 6/7), cada uno con `aria-label`/`title` con el nombre del estado. No existe un ícono
"Todos": la ausencia de cualquier ícono activo ES "todos los estados".

Clic en un ícono inactivo lo activa (y desactiva cualquier otro Estado que estuviera activo
— sigue siendo selección única); clic en el ícono YA activo lo desactiva, volviendo a "todos
los estados" sin tocar el texto de búsqueda. Se agrega un ícono de reseteo aparte, que limpia
el campo de texto Y cualquier Estado activo a la vez, y dispara la búsqueda resultante (lista
sin filtrar). El botón "Consultar" desaparece de la barra — un clic sobre un ícono de Estado
o de reseteo dispara el submit del formulario por JS; Enter en el campo de texto sigue
funcionando como submit normal.

Todavía sin resultados en vivo por tecleo (eso es el ticket 03) — cada acción sigue siendo un
submit tradicional con recarga de página.

**Blocked by:** 01 — trabaja sobre la barra ya reducida a un único campo de texto libre.

**Status:** ready-for-agent

- [ ] 4 íconos circulares de color (Anunciado/Recibido/Entregado/Cancelado) reemplazan el
      radiogroup de chips de texto de Estado, con la misma paleta que los badges.
- [ ] Cada ícono lleva `aria-label`/`title` con el nombre del estado (no llevan texto
      visible).
- [ ] No existe ícono "Todos".
- [ ] Clic en un ícono de Estado inactivo lo activa y desactiva cualquier otro Estado que
      estuviera activo.
- [ ] Clic en el ícono de Estado YA activo lo desactiva (vuelve a "todos los estados"), sin
      alterar el texto de búsqueda vigente.
- [ ] Cada clic sobre un ícono de Estado dispara la búsqueda (submit del formulario)
      conservando el texto ya escrito en el campo.
- [ ] Ícono de reseteo (aparte de los de Estado) limpia el campo de texto y cualquier Estado
      activo, y dispara la búsqueda resultante.
- [ ] El botón "Consultar"/"Buscar" se elimina de la barra.
- [ ] Enter en el campo de texto sigue funcionando como submit normal (fallback sin depender
      de los íconos).
- [ ] Tests HTTP en `tests/web/test_packages.py` verifican que el filtro de Estado sigue
      aplicando correctamente vía los parámetros de la URL (el toggle en sí es interacción de
      cliente — ver ticket 03/Further Notes de la spec sobre alcance de JS en la suite
      automatizada); se cubre que la ausencia de `estado` en la URL sigue devolviendo todos
      los estados.
- [ ] Verificación manual en navegador (skill `run`): toggle de cada ícono, reseteo, y que
      Enter en el campo de texto sigue funcionando.
- [ ] Suite completa (`pytest`) pasa.

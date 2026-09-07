# 327 — `/announce`: 5 bugs/mejoras visuales (checkbox mover, botones duplicados, ícono, lista de residentes, píldora Auto)

**Pedido original (cliente):**

> "BUGS VISUALES - Reemplaza este mensaje 'Si el contacto ya es Ocupante (no principal) de otra
> unidad, moverlo acá' por 'Mudar este residente a <Torre y Apartamento>'
> - Al presionar la sección '+ Nueva persona', aparecen otro set de botones de 'Anunciar y
> Recibir', de qué forma puedes unificarlos para que no se repitan, ya que al habilitar esta
> sección aparecen arriba y abajo, y creo que cumplen la misma función.
> - Cambia esto '+ Nueva persona' por un ícono alusivo a agregar un nuevo residente.
> - De qué forma se podrían cambiar la forma en que se visualizan los residentes actuales, tanto
> en el desktop como la versión mobile [...] hasta 2 columnas [...] hasta 2 líneas por cada uno de
> forma que aparezca nombre arriba y apellidos abajo. Dame alternativas [...]
> - Necesito que la píldora de 'Auto' se dé un color que contraste con el verde de fondo [...]
> rojo con letras blancas."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Decisiones de alcance

- El layout de residentes (punto 4) se presentó con 3 alternativas en vivo (columnas + qué va en
  la 2da línea) -- el cliente eligió "2 columnas desde tablet/desktop + nombre partido en 2 líneas
  (1ra palabra / resto)", con la salvedad conocida y aceptada de que un residente registrado con
  un solo nombre (frecuente acá: "Mamá", "Papá", "Hijo") deja la 2da línea vacía -- `Persona.nombre`
  es un solo campo, no hay `apellido` separado en el modelo.
- El color rojo/blanco de la píldora "Auto" (punto 5) se replicó en las 3 vistas que ya la usan
  (`/announce`, ficha de residente y tabla de `/residentes`) para no romper la unificación que ya
  había hecho issue 245 -- solo la de `/announce` tenía el problema real de contraste (fondo
  emerald sobre fondo emerald), pero dejarla divergente del resto habría sido peor.
- El checkbox "moverlo acá" (punto 1) con el mismo texto también existe en `/paquetes` (modal
  "Asignar apartamento", `packages/_resultados.html`) -- NO se tocó ahí: esa unidad se elige con un
  picker dentro del mismo modal (no hay una Torre/Apto ya resuelta como variable fija de la
  plantilla), así que el mismo fix necesitaría JS para reflejar la selección en vivo -- fuera de
  alcance de este pedido, que fue puntual sobre `/announce`.

## Implementación

- `app/web/templates/announce_new/_identificar_unidad.html`:
  - Checkbox: texto genérico reemplazado por "Mudar este residente a {{ apartamento.torre }} · Apto
    {{ apartamento.apartamento }}" -- la unidad destino ya es una variable fija de este fragmento.
  - `<summary>` de "+ Nueva persona": ahora ícono (`iconos_nav.agregar_persona`, nuevo) + texto
    "Nueva persona" (sin el "+").
  - Lista de residentes: `grid grid-cols-1 sm:grid-cols-2` (antes `space-y-1.5`, una sola columna
    siempre); cada botón parte `r.nombre` en `partes = r.nombre.split(' ', 1)` -- 1ra palabra en
    una línea (`text-sm font-medium`), el resto debajo (`text-xs text-slate-600`) si existe.
  - `<details>` marcado con `data-nueva-persona` para que el JS de `form.html` lo enganche.
- `app/web/templates/announce_new/form.html`: nuevo listener `toggle` (fase de CAPTURA, delegado
  sobre `#announce-resultado` -- ese evento no hace bubble) que oculta `#announce-unidad-accion`
  mientras `[data-nueva-persona]` está abierto, y lo vuelve a mostrar al cerrarlo (su contenido
  nunca se pierde, solo se oculta/muestra).
- `app/web/icons.py`: nueva clave `agregar_persona` -- path OUTLINE oficial de Heroicons
  "user-plus" (`stroke-width` ajustado de 1.5 a 2 para calzar con el resto del subconjunto
  outline de este archivo).
- Píldora "Auto": `bg-emerald-100 text-emerald-700 border-emerald-200` -> `bg-red-600 text-white
  border-red-700` en `components/_persona_resuelta.html`, `customers_manage/detail.html` y
  `customers_manage/_resultados.html`.

## Verificación

- `tests/web/test_announce_new.py`: 81/81 en verde (sin tests nuevos -- ninguno de los 5 cambios
  altera comportamiento observable por HTTP más allá de markup/CSS/JS de presentación; se
  verificaron a mano los tests existentes que citan nombres de residentes, checkbox y botones para
  confirmar que ninguno dependía del markup exacto que cambió).
- `tests/web/test_customers_manage.py`: 175/175 en verde (píldora Auto, sin tests que fijen su
  color).
- No se pudo verificar visualmente en navegador dentro de esta sesión (sin Chrome conectado) --
  pendiente que el cliente lo confirme en test.papyrus.com.co, especialmente el toggle de
  Anunciar/Recibir (JS) y el layout de 2 columnas en mobile real.

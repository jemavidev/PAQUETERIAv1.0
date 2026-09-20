# 353 — `/administracion/contactos-externos`, "Importar CSV": campo de fuente nueva nunca aparece cuando "Otra" es la única opción

**Pedido original (Jesús):** "En la vista /administracion/contactos-
externos/importar sigo sin poder seleccionar una fuente para el archivo,
en caso que este vacío, no es posible subir contactos."

**Status:** implementado

## Causa raíz

`admin/contactos_externos.html`: el `<select name="fuente">` lista las
fuentes YA usadas por contactos existentes (`{% for f in fuentes %}`) más
una opción fija `"Otra (especificar)…"` al final. Cuando **todavía no hay
ningún contacto importado** (ambiente nuevo, o la primerísima vez que se
usa esta pantalla), `fuentes` queda vacío -- "Otra (especificar)…" termina
siendo la ÚNICA opción del selector, seleccionada por defecto.

El campo de texto "Nombre de la fuente nueva" (obligatorio cuando se elige
"Otra") solo se revela vía `select.addEventListener('change', ...)` -- si
"Otra" ya viene seleccionada al cargar la página (porque es la única
opción), nunca se dispara ningún `change`, así que el campo se queda
oculto para siempre y no hay forma de escribir el nombre de la fuente ni
de completar el import.

Reproducible en cualquier ambiente/cliente que use esta pantalla por
primera vez -- confirmado en test.papyrus.com.co (BD limpia, sin
contactos).

## Fix

La misma función que sincroniza la visibilidad del campo se llama una vez
de entrada (al cargar el script), además de en cada `change` -- así el
estado inicial del selector (elegido por el usuario o, como en este caso,
el único que existe) siempre queda reflejado.

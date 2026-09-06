# 315 — Columna Acciones de /residentes: siempre 4 íconos, apagados cuando no aplican

**Pedido original (cliente):** en `/residentes`, cuando no aplican los 4 íconos de la columna
Acciones para una fila, en vez de omitirlos se deben mostrar desactivados -- mismo patrón ya
usado para otros íconos -- para que la lista de íconos sea siempre del mismo tamaño y se vea de
forma uniforme entre filas.

**Status:** implementado -- pendiente verificar visualmente en vivo (extensión de Chrome no
disponible en esta sesión).

## Los 4 íconos

1. WhatsApp -- SIEMPRE tiene un link válido (usuario de WhatsApp o teléfono, la constraint
   `ck_personas_telefono_o_whatsapp` garantiza al menos uno) -- nunca necesitó variante apagada.
2. Llamar -- YA tenía el patrón apagado (`{% if p.telefono %}...{% else %}<span apagado>`), sin
   teléfono propio. Sin cambios, es el patrón que los otros 2 ahora replican.
3. Comparte apartamento (👫) -- antes se OMITÍA sin `p.comparte_apartamento`. Ahora queda
   apagado (`opacity-40`, no `text-slate-300` -- es un emoji, no un ícono SVG con
   `fill="currentColor"`, el color de texto no lo tiñe).
4. Eliminar residente -- antes se OMITÍA para staff no-ADMIN. Ahora queda apagado (mismo patrón
   visual que "Llamar": `bg-slate-50 text-slate-300 border border-slate-100`) en vez de
   desaparecer -- la columna queda igual de ancha sin importar el rol de quien la mire.

Ningún ícono cambia su comportamiento cuando SÍ aplica -- solo se agregó la rama `{% else %}`
apagada donde antes no había nada.

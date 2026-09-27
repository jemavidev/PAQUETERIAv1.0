# 365 — `/announce`: el mensaje de la sugerencia de Contacto externo resalta como aviso

**Pedido original (cliente):**
"Pero de que forma puedo advertir al usuario que esta haciendo este anuncio
para que este mensaje resalte 'Este usuario no registra en el sistema, pero
podría ser:'" -- se propusieron 3 formas (caja de aviso ámbar / solo texto
destacado / franja lateral) y el cliente eligió la **A, caja de aviso ámbar**:
"Si aplica la opcion A".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

- Solo estilo del mensaje, en `announce_new/_identificar_con_sugerencia.html`
  (ver `.scratch/contactos-externos-en-announce`, ticket 02): el texto sigue
  siendo exactamente el del cliente y el comportamiento no cambia.
- Caja de aviso: fondo ámbar claro + borde ámbar, ícono de alerta a la
  izquierda, texto a 14 px en semibold ámbar oscuro. Mismo ámbar que la
  píldora "Sin notificar" de la tarjeta.
- Solo clases que ya están en el `tailwind.css` compilado (no hace falta
  reconstruirlo).

## Implementación

- `announce_new/_identificar_con_sugerencia.html`: el `<p>` gris de 12 px se
  reemplaza por una caja de aviso -- `flex items-start gap-2 rounded-lg border
  border-amber-200 bg-amber-50 px-3 py-2 mb-3 text-sm font-semibold
  text-amber-800`, con el ícono `iconos_nav.alerta` (`h-5 w-5 shrink-0`) a la
  izquierda y el texto en su propio `<p class="m-0">`. El texto es el mismo,
  en una sola línea del HTML (las pruebas lo buscan tal cual).
- Sin clases nuevas: todas ya estaban en el `tailwind.css` compilado
  (verificado una por una), así que no se tocó ni se reconstruyó el CSS.
- El aviso queda fuera del contenedor `#announce-unidad-accion`: sigue visible
  después de elegir la tarjetita, mientras se decide entre Anunciar y Recibir.

## Verificación

- `tests/web/test_announce_sugerencia_contacto_externo.py`: 17 pasan (el
  texto del mensaje no cambió). Es un cambio de estilo: no se agregó prueba
  que fije clases.
- Navegador a 390 px (iframe del mismo origen, sesión de Staff real, contacto
  ficticio sembrado y luego borrado): la caja mide 317x58 px, el texto parte
  en dos líneas, 14 px semibold, contraste 6,84:1 (pasa AA), sin scroll
  horizontal; con la tarjeta seleccionada el aviso sigue arriba.
- Pendiente: confirmación visual del cliente y deploy a test.papyrus.com.co.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.

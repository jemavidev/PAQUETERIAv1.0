# 391 — `/mis-datos`: aviso de privacidad bajo "Autorizo…" y saldo contra entrega como píldora desplegable

**Pedido original (Jesús):** "Esta sección "Tus datos se tratan según nuestra Política de Tratamiento de Datos
Personales." cámbiala de lugar, la vas a colocar debajo de "Autorizo a Papyrus para recibir todos los paquetes a mi
nombre. Términos y condiciones." ... reemplaza el texto "Saldo a favor (contra entrega)" por "Saldo (contra entrega)" ...
toda esta sección [la tarjeta del saldo] la puedes colocar con un botón que diga por ejemplo "Saldo (contra entrega)"
$<valor del saldo> y al presionarlo se muestre el contenido, ... una especie de píldora que se presione y se muestre la
información desplegada."

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- El aviso de privacidad sale de debajo del título y pasa dentro de la tarjeta de Datos, justo debajo del interruptor
  "Autorizo a Papyrus…".
- "Saldo a favor (contra entrega)" → "Saldo (contra entrega)" (el saldo también puede ser negativo).
- La tarjeta del saldo pasa a una píldora "Saldo (contra entrega) $X" (`<details>`/`<summary>`: abre y cierra sin
  JavaScript); al tocarla se despliega el historial de movimientos debajo. Cerrada por defecto. Monto en rojo si es
  negativo, igual que antes. Sin movimientos, no se muestra nada (sin cambios).

## Verificación

- `tests/web/test_portal_saldo_contra_entrega.py`: 3 ajustadas al texto nuevo + 2 nuevas (píldora `<details>` cerrada
  por defecto con "Saldo (contra entrega) $X" en el resumen y el historial dentro; aviso de privacidad una sola vez y
  después de "Autorizo a Papyrus…"). 71 en verde con `test_customer_verify.py`.
- Tailwind reconstruido (`group-open:rotate-180`, marcador de `<details>` oculto), `?v=103`. Capturas a 390 px
  revisadas, cerrada y abierta.

# 275 — Columna "Acciones" de `/residentes` con el mismo estilo de íconos que la tab "Residentes", + ícono de Eliminar consistente en todo el sistema

**Pedido original (cliente):** "en la vista /residentes, específicamente
la columna de 'Acciones', sus íconos deberían ser similares en como se
ven en la vista de /residentes en el tab de 'Residentes'." Seguimiento:
"algo a tener presente, creo que me gustó más este ícono para eliminar
'Eliminar residente'" (el SVG de basurero que ya tenía la columna
Acciones) -- "utiliza ese ícono en lo que aplique en el sistema".

**Status:** implementado

## Alcance

1. `customers_manage/_resultados.html` -- columna Acciones (WhatsApp,
   Llamar, 👫 comparte apartamento, Ver ficha, Eliminar) pasa del ícono
   suelto (solo cambia de color al hover, sin fondo) al mismo macro
   `chip_icono(color)` que ya usa la tab Residentes de la ficha
   (círculo 32px, fondo de color, borde). Los SVG existentes se quedan
   igual -- solo se envuelven en el nuevo estilo, no se reemplazan
   (excepto el punto 2). Colores: WhatsApp verde, Llamar azul (gris
   apagado si no tiene teléfono, mismo estado deshabilitado de hoy),
   👫 índigo, Ver ficha slate, Eliminar rojo (solo ADMIN).
2. El ícono de basurero (`iconos_nav.eliminar`, ya usado acá y en
   `/paquetes`) reemplaza el emoji "❌" en `customers_manage/detail.html`
   (tab Residentes de la ficha, botón Eliminar/Rechazar) -- mismo
   `chip_icono('red')`, solo cambia qué hay adentro.
3. `customer/verify.html` (`/mis-datos`, autoservicio): el botón
   Eliminar/Rechazar hoy es SOLO texto (`chip_accion('red')`, sin
   ningún ícono) -- se le antepone el mismo SVG de basurero, sin
   cambiar a icon-only (esa vista mantiene su propio patrón
   ícono+texto en los botones hermanos ⭐/✏️/🔔, cambiar solo este a
   icon-only rompería esa consistencia interna).

## Verificación

- Suite `test_customers_manage.py` + `test_customer_verify.py`: 217
  passed.
- Con el navegador reconectado, verificado VISUALMENTE (screenshot
  real, no solo HTML): la columna Acciones de `/residentes` y el
  botón Eliminar de la ficha (`/residentes/{id}`) se ven exactamente
  como se pidió -- círculos de color con los mismos íconos SVG de
  siempre (WhatsApp verde, Llamar azul/gris, 👫 índigo, Ver ficha
  slate, Eliminar rojo con el basurero).
- `/mis-datos` (autoservicio): la sesión de cliente se cayó en el
  navegador durante la verificación (problema de la sesión OTP en el
  browser, no de la app) -- confirmado por HTML servido en su lugar
  (curl), no visualmente. Es el cambio de menor riesgo de los 3 (solo
  antepone el ícono al texto ya existente, mismo patrón exacto que ya
  usan los botones hermanos ⭐/✏️/🔔 de esa misma vista).

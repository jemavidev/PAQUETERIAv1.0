# 40 — `/mis-datos`: 9 ajustes de texto/copy

**Pedido original (cliente):** "Se ve bastante bien, pero para terminar
necesito que cambien el texto de algunas secciones: 1. Remieve este texto
'El Conjunto lo asigna el staff — '. 2. Cambia esto 'Quiénes' por 'Quien'.
3. Cambia esto 'Principal (tú)' por 'Principal'. 4. Remueve esto 'Con
teléfono propio'.. 5. Cambia el texto de 'Dar de baja' por 'Eliminar' o una
'X'. 6. Cambia esto 'Agregar Ocupante' por 'Agregar'. 7. Cambia 'Guardar
teléfono' por 'Actualizar'. 8. Por ultimo remueve el numero de telefono de
la pestana principal, ya que es posible modificarlo en el formulario 'Mis
datos J JESUS MARIA VILLALOBOS +573002596319'. 9. Ademas cambia esto 'el
staff' por 'Papyrus' en la frase 'Autorizo que el staff anuncie/reciba
paquetes a mi nombre sin necesidad de llamarme primero'."

**Status:** verificado

## Alcance

Solo `customer/verify.html` (`/mis-datos`, vista del cliente) — no toca
`customers_manage/detail.html` (staff), que tiene su propia audiencia y
texto. Punto 5 el cliente dio dos opciones ("Eliminar" o "X"); se elige
"Eliminar" por consistencia con el resto de botones de texto de esa misma
tarjeta (Desvincular teléfono, Promover a principal, Asociar, Actualizar) —
un ícono "X" rompería ese patrón visual.

## Implementación

Los 9 cambios, todos en `customer/verify.html`:
1. "El Conjunto lo asigna el staff — " retirado del hint de Apartamento.
2. "Quiénes" → "Quien" en los 2 lugares (Mis Ocupantes y Quien más viven acá).
3. "Principal (tú)" → "Principal" (badge del propio principal en su lista).
4. "Con teléfono propio" retirado (esa rama del `{% elif %}` ya no muestra nada).
5. "Dar de baja" → "Eliminar" (botón; el texto del `confirm()` se dejó igual,
   sigue describiendo la acción real).
6. "Agregar Ocupante" → "Agregar".
7. "Guardar teléfono" → "Actualizar".
8. Teléfono retirado de la franja de perfil (avatar+nombre) arriba de las
   pestañas -- sigue editable en el campo de la pestaña Datos.
9. "el staff" → "Papyrus" en el checkbox de autorización automática.

Sin clases nuevas de Tailwind (cambios de texto puro) -- no hizo falta
recompilar CSS ni subir el cache-bust. Test actualizado:
`test_ocupante_no_principal_ve_roster_de_solo_lectura` (asertaba el texto
viejo "Quiénes más viven acá"). Suite completa: 539 passed.

# 31 — Validación visible por campo (no solo el toast genérico)

**Pedido original (cliente):** "para las ocasiones en donde se valida un
formulario y los datos son inválidos aparece la notificación sin
problemas, PERO sería bueno visualizar en el campo donde está el problema
una notificación (posiblemente un recuadro o asterisco o no sé qué me
recomiendas que sea sutil pero práctico)".

**Vistas:** las 9 rutas con validación de formulario en toda la app --
`/anunciar`, `/announce` (staff), `/ingresar`, `/otp`+`/otp/verificar`,
`/staff/olvide-password`+`/staff/restablecer-password`, `/mis-datos`,
`/administracion/personal`+`/administracion/notificaciones`,
`/residentes/{id}`, `/paquetes` (modal Corregir).

**Status:** verificado

## Recomendación dada y confirmada

El patrón YA existía en el componente `input_texto` (borde inferior rojo +
ícono + mensaje específico debajo del campo, `aria-invalid`/
`aria-describedby`) pero ninguna ruta lo conectaba -- todas mandaban el
error solo al toast genérico de arriba. Confirmado con el cliente:

1. Alcance: TODOS los formularios de una vez (no solo `/anunciar`).
2. Formularios de seguridad (login, código OTP, restablecer contraseña):
   se marcan AMBOS campos con el MISMO mensaje genérico -- nunca decir
   cuál de los dos falló (mismo principio anti-enumeración que ya regía
   el mensaje).

## Qué se hizo, por ruta

- **`/anunciar`**: nombre, teléfono, checkbox T&C (recuadro rojo +
  mensaje, no `input_texto` pero mismo lenguaje visual).
- **`/announce`** (staff): conjunto/torre/apartamento, los 3 campos del
  bloque "anunciar". Las filas dinámicas de "Residentes" (inputs
  clonados por JS) quedan fuera a propósito -- sin macro/error box
  propio, el toast ya es suficientemente claro para esta herramienta
  interna.
- **`/ingresar`**: email + contraseña, AMBOS marcados con el mismo
  mensaje genérico (campo de seguridad).
- **`/otp`**: teléfono (solo validación de formato -- la elegibilidad
  sigue silenciosa, sin campo ni mensaje distinto, a propósito).
- **`/otp/verificar`**: ambas casillas del código marcadas (campo de
  seguridad, un solo concepto partido en 2 inputs).
- **`/staff/restablecer-password`**: contraseña + confirmación
  (mismatch); contraseña sola (débil, clasificado por prefijo del
  mensaje ya que `confirmar_reset` no distingue tipo de error de otra
  forma). Token inválido/expirado se queda sin campo (no es un input
  visible).
- **`/mis-datos`**: email (formato); torre + apartamento (incompletos).
  El caso "conjunto no asignado" se queda sin campo -- esos inputs ni
  siquiera se renderizan en ese estado.
- **`/administracion/personal`**: email/nombre/contraseña del alta de
  cuenta nueva, clasificados por prefijo del mensaje de
  `staff_service`. Rol (chips) y los modales de editar/resetear-password
  por fila quedan fuera -- mismo criterio que "Residentes" de arriba.
- **`/administracion/notificaciones`**: el textarea de la fila específica
  que falló se marca en rojo (cada evento/motivo es su propio `<form>`).
- **`/residentes/{id}`**: email (formato).
- **`/paquetes`**: el modal "Corregir destinatario" del paquete
  específico se reabre automáticamente (nuevo parámetro `abierto` en el
  macro `modal()`) y el campo Nombre se marca si estaba vacío. Los demás
  modales (Recibir/Entregar/Cancelar) no tienen inputs de texto con un
  error de validación real -- solo transiciones de estado inválidas, sin
  campo natural que marcar.

## Verificación

- [x] Suite de tests completa sin regresiones (454 passed).
- [x] Capturas confirman el patrón en `/anunciar` (campo normal) y
      `/ingresar` (campo de seguridad, ambos marcados).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.

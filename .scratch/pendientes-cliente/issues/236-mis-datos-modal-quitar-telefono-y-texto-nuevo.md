# 236 — `/mis-datos`: modal para "Quitar mi Teléfono" + texto nuevo

**Pedido original (cliente):** "necesito que crees un modal para este
texto 'Vas a perder el acceso a "Mis datos" en este dispositivo -- el
ingreso siempre es por Teléfono. Solo podrás volver a entrar si el
personal te asigna un Teléfono nuevo. Entiendo que perderé el acceso a
"Mis datos" en este dispositivo.' por esto 'Vas a perder el acceso al
panel de "Mis datos", ya que el ingreso a este panel solamente por número
de Teléfono. Entiendo que perderé el acceso a "Mis datos".'"

**Status:** implementado

## Alcance

`customer/verify.html` -- sección "Quitar mi Teléfono" del Principal (tab
Datos). Hoy es un `<details>` con formulario inline (no un `confirm()`
nativo, pero el mismo espíritu que el resto del pedido: sacarlo del flujo
"disclosure inline" y pasarlo a modal, mismo componente `modal_confirmacion`
que ya usan Confirmar/Rechazar/Promover en esta misma vista). Texto del
cuerpo y del checkbox reemplazados por el nuevo, verbatim salvo el acento
en "número" (typo del texto tal como llegó, corregido para
consistencia ortográfica con el resto de la app).

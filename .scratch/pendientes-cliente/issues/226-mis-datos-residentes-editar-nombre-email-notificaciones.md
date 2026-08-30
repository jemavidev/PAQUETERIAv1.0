# 226 — `/mis-datos` tab Residentes: editar nombre/email y notificaciones por residente

**Pedido original (cliente):** "La opción para que a un residente se le
pueda cambiar el nombre e incluso asociar o no una dirección de email sería
buena, pero de qué forma puedes hacer que todo esto sea más compacto, ya
que van a ser varios datos adicionales, dime si puedes?" (seguimiento de la
pregunta sobre cómo editar datos/notificaciones de un co-residente desde
`/mis-datos`).

**Status:** implementado

## Implementación

- `customer_verify.py`: 2 rutas nuevas, `POST /mis-datos/ocupantes/{id}/datos`
  (nombre+email, reusa `update_datos_personales` sobre la Persona del
  residente) y `POST /mis-datos/ocupantes/{id}/notificaciones` (reusa
  `guardar_matriz_preferencias`, misma restricción `combinaciones_editables`
  que la matriz propia del principal). Ambas exigen `_ocupante_gestionable_por`
  (solo el principal de esa unidad) y que el Ocupante ya tenga
  `persona_id` (contacto propio).
- `_contexto_base`: agrega `personas_email`/`personas_matriz` (batch por
  apartamento, no por fila -- roster chico, no amerita el patrón de
  `/paquetes`).
- `verify.html`: 2 chips nuevos por residente con contacto ("✏️ Editar",
  "🔔 Notificaciones"), colapsados con `<details>` -- la tarjeta no crece
  salvo que se abran a propósito.

Verificado en vivo (curl): nombre y `Ocupante.nombre` se sincronizan igual
que en `/residentes` (staff), email se guarda, matriz de preferencias
individual del residente se guarda con la semántica correcta (checkbox
ausente = desactivado). 54 tests de `test_customer_verify.py` pasan.


## Diseño acordado

Compacto vía `<details>` (mismo mecanismo que `+ Teléfono`/`+ WhatsApp`,
issue 217): 2 chips nuevos por residente CON contacto propio --
"✏️ Editar" (Nombre + Email, reusa `update_datos_personales`) y
"🔔 Notificaciones" (matriz Canal×Evento de ESE residente, reusa
`guardar_matriz_preferencias`/`matriz_preferencias`, mismo criterio de
`combinaciones_editables` que ya usa el principal para sí mismo). Ambos
colapsados por defecto -- la tarjeta no crece salvo que se abran a
propósito.

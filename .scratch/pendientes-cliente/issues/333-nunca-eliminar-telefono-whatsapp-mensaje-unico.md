# 333 — Nunca eliminar Teléfono/WhatsApp (ni con respaldo) + mensaje único en toda la app

**Pedido original (cliente):** "Necesito que para la edicion de los datos de un residente en la vista
`/residentes/{id}/ocupantes/{id}/editar`, se pueda hacer sin problemas (solo edicion, nunca
eliminacion) [...]. Adicional necesito que en esta misma vista remuevas las opciones de 'Quitar
teléfono Quitar WhatsApp', la idea es que los numero de telefonos despues de ingresados no puedan
ser eliminados, solo editados. [...] Tambien necesito un mensaje para las vistas que hacen
referencia a la edicion de 'usuario de whatsapp o numero de telefono', necesito que en todas se
informe este mensaje 'No es posible eliminar este dato, solo se podra editar'. Este es uno de los
mensajes que estara remplazando 'No se puede quitar el WhatsApp -- es el único canal de esta
Persona...', como te lo solicite anteriormente."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Contexto

Extiende la decisión de la conversación 2026-09-14 (ese mismo día, más temprano): "nunca eliminar
Teléfono/WhatsApp, solo editar" ya estaba implementado para el caso de **único canal** (sin
respaldo). Este pedido lo extiende al caso de **canal doble** (con respaldo): ni siquiera teniendo
Teléfono Y WhatsApp a la vez se permite ya vaciar uno de los dos -- la única forma de cambiarlo es
escribir un valor nuevo directamente.

## Decisiones de alcance (confirmadas con el cliente antes de implementar, vía preguntas)

1. Alcance de los botones "Quitar teléfono/WhatsApp": **staff (`/residentes`) + autoservicio del
   cliente (`/mis-datos`)** -- no solo la vista de staff que mencionó el cliente.
2. Funciones de backend que quedaban sin ningún botón que las disparara
   (`desvincular_telefono_ocupante`, `desvincular_whatsapp_ocupante`, `desvincular_telefono_propio`):
   **se retiraron por completo** (mismo criterio que `desvinculada_en` esa misma mañana) -- no se
   dejó código muerto alcanzable solo por URL manual.
3. La pestaña "Datos" de la ficha (staff) y el formulario "Datos personales" (autoservicio) tenían
   su PROPIO camino, separado de los botones "Quitar": dejar el campo en blanco y Guardar SÍ borraba
   el dato cuando había canal doble. **Se cerró también**, para quedar 100% consistente.

## Implementación

- `app/domain/ocupante_service.py`: se retiraron `desvincular_telefono_ocupante` y
  `desvincular_whatsapp_ocupante` por completo.
- `app/domain/persona_service.py`:
  - Se retiró `desvincular_telefono_propio` por completo.
  - Nueva constante `MENSAJE_NO_SE_PUEDE_ELIMINAR = "No es posible eliminar este dato, solo se
    podrá editar."` -- único mensaje, reusado en todas las vistas.
  - `update_datos_personales`: `whatsapp_usuario=""` ya NO borra el campo si la Persona ya tenía uno
    cargado -- ahora lanza `ValueError(MENSAJE_NO_SE_PUEDE_ELIMINAR)`. Sigue siendo no-op inofensivo
    si no había nada que borrar. `email` no cambió (sigue con su contrato de 3 estados -- no tiene
    invariante de "canal" que proteger).
- `app/web/routes/customers_manage.py` (`customers_manage_update`, tab Datos del staff):
  - Teléfono: el branch de canal-doble-permitido se retiró -- vaciar un Teléfono ya existente se
    rechaza siempre con `MENSAJE_NO_SE_PUEDE_ELIMINAR`.
  - WhatsApp: se simplificó -- ya no hace su propio chequeo de canal doble/único aparte
    (`limpiar_whatsapp` se retiró); ahora pasa `whatsapp_v` directo a `update_datos_personales` y
    deja que ESA función rechace, igual que Email/formato. El `except ValueError` que distingue a
    qué campo atribuir el error se ajustó: un WhatsApp vacío nunca puede fallar por formato, así que
    "vacío + hay error" ya es inequívocamente el rechazo de WhatsApp.
  - Se retiraron las 2 rutas `POST /residentes/{id}/ocupantes/{id}/desvincular-telefono` y
    `.../desvincular-whatsapp`.
- `app/web/routes/customer_verify.py` (autoservicio):
  - Mismo ajuste de atribución de campo en `customer_verify_submit` (`/mis-datos`, tab Datos
    personales).
  - Se retiraron 3 rutas: `POST /mis-datos/desvincular-telefono` (self, ticket 14 histórico),
    `POST /mis-datos/ocupantes/{id}/desvincular-telefono` y `.../desvincular-whatsapp`.
- Templates:
  - `customers_manage/detail.html`: se retiró el bloque "Quitar teléfono"/"Quitar WhatsApp" del
    modal Editar por Ocupante (antes gateado a canal doble).
  - `customer/verify.html`: se retiró el botón+modal "Quitar mi Teléfono" (ticket 14) y el bloque
    "Quitar teléfono"/"Quitar WhatsApp" por Ocupante.

## Verificación

- `tests/data_model/test_persona_service.py`: 2 tests invertidos (`test_whatsapp_usuario_string_
  vacio_ya_no_lo_borra`, nuevo no-op test), import huérfano limpiado.
- `tests/data_model/test_ocupante_service.py`: 6 tests borrados (probaban las funciones retiradas),
  import huérfano limpiado.
- `tests/web/test_customers_manage.py`: 2 tests invertidos (canal doble ahora rechaza, antes
  permitía), 4 tests borrados (rutas retiradas), 2 mensajes de aserción actualizados al texto nuevo.
- `tests/web/test_customer_verify.py`: 9 tests borrados (rutas retiradas), 1 test nuevo (WhatsApp
  vacío en `/mis-datos` ya no borra).
- Suite completa: 1640 passed, sin fallos (baja de 1658 a 1640 -- balance neto de tests borrados
  contra los agregados, todo intencional).
- Verificado en vivo (navegador, ambiente local), con la URL EXACTA del pedido
  (`/residentes/454a2bb5-.../ocupantes/a28df466-.../editar`, Angelica Arrazola):
  - Modal Editar ya no muestra "Quitar teléfono"/"Quitar WhatsApp".
  - Editar el teléfono de un Ocupante no-Principal (Jesús) a un valor nuevo funciona sin
    problemas (guardado correcto, sin errores).
  - Editar el teléfono del Principal (Angelica) vía este modal sigue rechazado -- comportamiento
    INTENCIONAL preexistente, sin relación con este pedido (`editar_telefono_ocupante`: "El
    teléfono del principal se edita desde 'Datos personales', no acá"); confirmado que el toast de
    error SÍ se muestra correctamente (se verificó con `fetch()` directo -- la demora del navegador
    real hizo que el toast (5s de duración) ya se hubiera autodescartado antes de la captura de
    pantalla, un artefacto de la prueba, no un bug real).

## Pendiente

- El texto pegado por el cliente en el pedido original ("[Pasted text #21 +3 lines]") no llegó --
  se le pidió reenviarlo por si mostraba algo adicional no cubierto acá. Sin respuesta al momento de
  cerrar este ticket -- si aparece algo nuevo, se abre un ticket de seguimiento.

# 334 — "Eliminar residente": bloquear con saldo pendiente + ficha de solo lectura tras eliminar

**Origen:** hallazgo en vivo (no pedido explícito inicial) -- al hacer una prueba end-to-end completa
(crear residente, moverle paquetes/cobro/saldo contra entrega/cancelación, y finalmente eliminarlo)
para explicarle al cliente cómo se comporta el sistema, encontré 2 gaps reales en el flujo de
"Eliminar residente" (`anonimizar_persona`, ADR-0005). Confirmados con el cliente antes de
implementar (2 preguntas, ambas resueltas por la opción recomendada).

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Hallazgo 1 — saldo contra entrega pendiente no se resuelve ni se advierte

`anonimizar_persona` nunca tocó `movimientos_saldo_contra_entrega` -- si un residente tenía saldo
distinto de cero al momento de eliminarlo, ese saldo quedaba huérfano, visible en el ledger global
(`/residentes/saldos-contra-entrega`) bajo el nombre genérico **"Cliente eliminado"**, indistinguible
de cualquier OTRO residente eliminado con saldo pendiente.

**Decisión (confirmada con el cliente):** bloquear la eliminación por completo si el saldo es
distinto de cero -- tanto para el ADMIN (`/residentes/{id}/eliminar`) como para el autoservicio
(`/mis-datos/eliminar-cuenta`), sin excepción para ninguno de los dos (a diferencia del guard de
"paquete en curso", que el staff SÍ puede saltarse -- acá es un problema de dinero, no de logística).

## Hallazgo 2 — la ficha de un residente eliminado seguía 100% editable

Encontrado navegando: aunque un eliminado ya no aparece en la búsqueda/listado de `/residentes`, su
ficha (`/residentes/{id}`) seguía siendo accesible por link directo (ej. desde el propio ledger de
saldos, que enlaza "Cliente eliminado" a su ficha) -- y una vez ahí, **todos los formularios
(Datos, Dirección, Notificaciones, Residentes/Ocupantes, Saldo) seguían aceptando cambios**, como si
nunca se hubiera eliminado. "Dar de baja"/"Bloquear" ya estaban ocultos para un eliminado (fix
anterior), pero ningún otro formulario tenía ese mismo cuidado.

**Decisión (confirmada con el cliente):** la ficha (GET) se queda consultable -- no romper el link
del ledger de saldos -- pero NINGÚN POST puede volver a tocarla.

## Implementación

- `app/web/routes/customers_manage.py`:
  - Nuevo helper `_get_persona_editable_o_404` (junto a `_get_persona_o_404`): igual, pero rechaza
    (400, "Este residente fue eliminado -- ya no se puede editar.") si `persona.eliminado_en` está
    seteado. Reemplazó a `_get_persona_o_404` en las 16 rutas POST que mutan una ficha existente
    (Datos, Dirección, Notificaciones, Ocupantes -- agregar/telefono/contacto/whatsapp/editar/
    confirmar/promover/baja --, Eliminar, Baja administrativa, Reactivar, Bloquear, Autorizar
    desbloqueo, Saldo). El GET de la ficha y el GET de "identificar contacto" (solo lectura, sin
    mutación) se quedaron con `_get_persona_o_404` sin cambios.
  - `customers_manage_delete` (`/residentes/{id}/eliminar`): nuevo chequeo de
    `saldo_de_persona(db, persona.id) != 0` ANTES de anonimizar -- si hay saldo, renderiza la ficha
    con el error vía `_render_detalle_con_error` (toast, mismo patrón que el resto de la app) en vez
    de redirigir con éxito.
- `app/web/routes/customer_verify.py`:
  - `customer_eliminar_cuenta` (`/mis-datos/eliminar-cuenta`): mismo chequeo de saldo, después del
    guard existente de "paquete en curso" -- mismo patrón `_render_con_error`.

## Verificación

- 4 tests nuevos en `test_customers_manage.py`: saldo pendiente rechaza (sin cambios en la Persona),
  eliminar dos veces rechaza en el segundo intento, editar Datos de un ya-eliminado rechaza (ficha
  GET sigue viéndose).
- 1 test nuevo en `test_customer_verify.py`: saldo pendiente rechaza en autoservicio.
- Suite completa de ambos archivos: 262/262 en verde.
- Verificado en vivo (navegador, ambiente local) ANTES de implementar el fix, con un residente de
  prueba creado para la ocasión ("María Testing", Torre 3 Apto 101): reproduje exactamente el saldo
  huérfano ("Cliente eliminado -- $8,000" en el ledger) y la ficha editable (cambié su Dirección tab
  sin ningún rechazo) -- confirmando que ambos gaps eran reales antes de tocar código.

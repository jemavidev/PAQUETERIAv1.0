# 157 — `/residentes`: cómo sumar un Residente existente a una unidad ocupada

**Pedido original:** reporte confuso/cortado ("no se porque no se me permite que un residente
pueda agregar a otro residente, ademas no se permite que un apartamento...", luego "quiero
enfocarme en lo único que te he pedido desde el principio, necesito poder gestionar a [residentes]
y los apartamentos... la vista de residentes no permite gestionarlos de ninguna manera, COMO ME
PUEDES COLABORAR"). Diagnóstico en vivo (reproducido contra `localhost:8010`, no un bug de
"no funciona" sino de descubribilidad):

1. Tab Dirección **solo** asigna unidades completamente vacías -- si la unidad ya tiene gente,
   rechaza con "Ya tiene residentes -- agregá más gente desde tab Residentes", pero **no decía a
   la ficha de quién ir** -- el staff se quedaba sin saber el siguiente paso.
2. "+ Agregar un nuevo Residente" (tab Residentes) SÍ reconoce y suma a alguien con ficha propia
   si se escribe su Teléfono o WhatsApp exacto -- pero eso no era obvio (probado con un caso real:
   una Persona sin teléfono, solo WhatsApp, parecía "no se puede agregar" hasta confirmar que el
   campo también acepta `@usuario`).

Ambos puntos, confirmados reproduciendo el flujo completo (asignar unidad vacía → agregar
segunda Persona YA existente por su contacto → confirmado en la lista con 👫 de [[156]]) antes de
tocar código.

**Status:** implementado

## Cambio

- `customers_manage.py` (`customers_manage_asignar_apartamento`): el mensaje "Ya tiene
  residentes" ahora resuelve con `listar_ocupantes(db, nuevo_apto)` el primer Ocupante activo con
  `persona_id` (principal primero) y arma un link real a su ficha
  (`/residentes/<id>?tab=residentes`) vía `Markup(...).format(...)` (mismo patrón ya usado para
  `titulo_paquete` en `/paquetes`, acá en Python en vez de Jinja porque el mensaje se arma
  server-side). Fallback al texto plano de siempre si ningún Ocupante activo tiene `persona_id`
  (caso defensivo -- el invariante de dominio ya garantiza que el primer Ocupante de una unidad
  vacía y todo Principal confirmado siempre tienen `persona_id`, así que en la práctica esto no
  debería dispararse nunca).
- `customers_manage/detail.html`: aviso nuevo bajo el campo de contacto de "+ Agregar un nuevo
  Residente" -- "Si la persona ya tiene su propia ficha, escribí su teléfono o WhatsApp para
  sumarla acá (en vez de crear un registro nuevo)."

## Verificación

- 2 tests nuevos/extendidos en `test_customers_manage.py`: el mensaje de error trae el `href`
  correcto a la ficha del Ocupante existente; el aviso del campo de contacto aparece en la ficha.
- Suite completa: 1044/1044.
- Verificado en vivo: reproducido el escenario completo (asignar unidad vacía a un Residente,
  intentar sumar a otro directo por Dirección → bloqueado con el link correcto al Residente que ya
  vive ahí). Datos de prueba limpiados al terminar.

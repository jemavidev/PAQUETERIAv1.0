# 156 — `/residentes` columna Acciones: ícono 👫 si comparte apartamento

**Pedido original:** "Necesito que en la columna de acciones agregues este emoji 'People holding
hands' (muestrame una posibilidades) esto con el fin de saber si un residente comparte su
apartamento con otros residentes, muestrame opciones" — se mostraron 4 variantes del emoji
(neutro 🧑‍🤝‍🧑, hombre+mujer 👫, dos hombres 👬, dos mujeres 👭); eligió **👫 hombre y mujer**.
Aclaración inmediata: "Solo quiero que sean las 2 personitas, nada más" — sin número/texto visible
al lado, solo el ícono.

**Status:** implementado

## Cambio

- `customers_manage.py`: nuevo helper `_adjuntar_comparte_apartamento(db, personas)` — un solo
  `GROUP BY Ocupante.apartamento_id` (filtrado a `desvinculado_en IS NULL`) para todo el listado,
  mismo patrón anti-N+1 que `_adjuntar_apartamentos`/`_adjuntar_ocupante` (ya documentado ahí).
  Adjunta `p.comparte_apartamento = True` si su unidad tiene 2+ Ocupantes activos (cuenta también
  Ocupantes sin Persona propia — sin contacto — que igual ocupan la unidad).
- `customers_manage/search.html`: en la columna Acciones, entre "Llamar" y "Ver ficha", `<span>👫</span>`
  visible SOLO si `p.comparte_apartamento` — sin texto ni conteo al lado (pedido explícito), con
  `title`/`aria-label` para accesibilidad (tooltip al pasar el mouse, no visible por defecto).

## Verificación

- 3 tests nuevos en `test_customers_manage.py`: aparece con 2+ ocupantes activos, no aparece con
  1 solo ocupante, no aparece sin apartamento asignado.
- Suite completa: 1043/1043.
- Verificado en vivo contra `localhost:8010`: agregado un segundo Ocupante (sin contacto) a la
  unidad de un Residente existente vía `/residentes/{id}/ocupantes`, confirmado que 👫 aparece en
  su fila de `/residentes`; dado de baja el Ocupante de prueba, confirmado que el ícono desaparece.
  Datos de prueba limpiados al terminar.

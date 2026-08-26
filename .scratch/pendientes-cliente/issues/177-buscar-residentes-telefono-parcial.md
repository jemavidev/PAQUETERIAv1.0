# 177 — `_buscar_residentes`: permitir buscar por teléfono parcial, no solo completo

**Pedido original:** "dime si esta opcion permite buscar por numero de telefono parcial o
completo?" → explicado que hoy solo matchea teléfono completo y válido (`normalizar_telefono` +
comparación exacta `==`), un fragmento no encuentra nada → confirmado: "sí, agrégalo."

**Status:** implementado

## Cambio

- `customers_manage.py` (`_buscar_residentes`): nuevo filtro
  `Persona.telefono.ilike(f"%{termino}%")`, agregado cuando `termino` (sin espacios) es solo
  dígitos PERO no normalizó a un teléfono completo/válido (`telefono is None`) -- así un
  fragmento como "3001" o los últimos 4 dígitos encuentra coincidencias parciales sobre el
  teléfono canónico guardado (`+573001234567`), sin exigir el número completo. Si el término SÍ
  normaliza a un teléfono válido completo, se mantiene la comparación exacta de siempre (no hace
  falta la parcial, la exacta ya es más precisa).

## Verificación

- 2 tests nuevos: buscar por fragmento de teléfono (últimos 4 dígitos) encuentra a la Persona;
  guard de que no confunda con el teléfono de otra Persona que no contiene esa secuencia.
- Suite completa: 302/302 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`): buscar "3849" (últimos 4 dígitos de un teléfono real de
  prueba) encuentra correctamente a esa Persona.
- Pendiente: verificar en test.papyrus.com.co tras deploy.

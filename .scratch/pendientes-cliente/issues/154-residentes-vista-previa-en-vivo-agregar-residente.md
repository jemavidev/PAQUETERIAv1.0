# 154 — `/residentes` tab Residentes: vista previa en vivo en "+ Agregar un nuevo Residente"

**Pedido original:** dentro de la propuesta de refactor de `/residentes` ("vamos con tus
recomendaciones") -- reusar en el tab Residentes el mismo mecanismo de vista previa en vivo que
ya tenía "+ Nuevo residente" en `/paquetes` (Recibir/Corregir destinatario), para que agregar un
residente desde acá se sienta igual que hacerlo desde `/paquetes`.

**Status:** implementado

## Refactor de dominio (seam real, no hipotético)

`nuevo_residente_identificar` (`packages.py`) era el ÚNICO caller de esta lógica -- al agregar un
segundo caller casi idéntico (`/residentes`), se extrajo a
`ocupante_service.identificar_contacto_para_unidad(session, contacto, apto_actual)`, compartida
por los dos. `apto_actual` entra ya resuelto (cada caller lo calcula distinto: `/paquetes` desde
el snapshot del Paquete, `/residentes` desde `Persona.apartamento_actual_id`) -- la función en sí
no sabe nada de Paquete ni de Persona "actual". `packages.py` quedó reducido a resolver
`apto_actual` y delegar; sin cambio de comportamiento (mismos 7 tests de esa ruta, todos verdes).

## Lo nuevo en `/residentes`

- `GET /residentes/{persona_id}/ocupantes/identificar?contacto=` -- mismo contrato JSON que su
  equivalente de `/paquetes`.
- Formulario "+ Agregar un nuevo Residente" (tab Residentes): al teclear Teléfono/WhatsApp, si ya
  existe una Persona con ese contacto, el campo Nombre se autocompleta y bloquea (readonly) con
  su nombre real + aviso "Ya existe como X"; si además ya es Ocupante activo de OTRA unidad,
  aparece el checkbox "Mudar residente a `<unidad real>`" (antes era un checkbox genérico,
  siempre visible, sin decir a cuál unidad); si esa unidad la tiene como Principal, aviso ámbar
  con link a su propia ficha (`?tab=residentes`, mecanismo ya usado desde `/paquetes` hacia acá)
  en vez de bloquear en seco.

**Única diferencia deliberada vs. el mecanismo de `/paquetes`**: acá el campo Nombre NO se oculta
hasta teclear el contacto (en `/paquetes` sí) -- en este form el contacto es explícitamente
opcional (no todo Residente lo necesita), así que ocultar Nombre sería más fricción que ayuda.
Tampoco reabre el modal "Promover" con picker de candidatos (no existe en esta plantilla) -- un
link directo a la ficha del conflicto alcanza, porque acá el staff ya está en pantalla de gestión
de residentes.

## Verificación

- `tests/data_model/test_ocupante_service.py`: 4 tests nuevos para
  `identificar_contacto_para_unidad` (sin match, match sin conflicto, conflicto con otra unidad,
  sin conflicto si ya es de la misma unidad).
- `tests/web/test_customers_manage.py`: 6 tests nuevos para el endpoint
  (encuentra por teléfono, sin match, conflicto no-principal, conflicto principal, sin conflicto
  misma unidad, requiere sesión de staff).
- `tests/web/test_packages.py`: sus 7 tests de `nuevo_residente_identificar` siguen en verde tras
  el refactor -- confirma que extraer la lógica compartida no cambió el comportamiento ahí.
- Suite completa: 1041/1041.
- Verificado en vivo contra `localhost:8010`: el endpoint responde el JSON esperado, y el HTML de
  la ficha trae el nuevo markup apuntando al `persona_id` correcto.

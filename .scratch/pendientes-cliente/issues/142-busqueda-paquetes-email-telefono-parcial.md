# 142 — `/paquetes`: búsqueda por email + teléfono parcial (últimos dígitos)

**Pedido original (cliente):** pidió análisis de qué busca y qué no busca la barra de
`/paquetes`; de las sugerencias presentadas, confirmó implementar email y teléfono parcial,
"aplica la búsqueda parcial a todo lo que aplique".

**Status:** implementado

## Implementación (`_listar` en `packages/routes.py`)

- **Email del Anunciante**: agregado a las condiciones `OR` (`Persona.email.ilike(patron)`),
  mismo join a `Persona` que ya existía para nombre/WhatsApp.
- **Teléfono parcial**: antes exigía el número COMPLETO y válido
  (`normalizar_telefono(q)` sin excepción, match exacto). Ahora: se extraen los dígitos de `q`
  (`re.sub(r"\D", "", q)`, ignora espacios/guiones/`+`) y, si hay **4 o más dígitos**, se busca
  como substring dentro del teléfono guardado (`announced_by_phone`/`recipient_phone`, ambos
  `ilike`). Alcanza con "los últimos 4 dígitos". El piso de 4 evita que un texto corto (ej.
  "torre 5") dispare falsos positivos contra prácticamente cualquier teléfono.
- Placeholder actualizado: "...nombre, **email**, WhatsApp, teléfono...".
- El resto de los campos (código, guía, nombre, WhatsApp, torre, apartamento) ya eran parciales
  desde antes -- sin cambios ahí.
- Import de `normalizar_telefono` retirado de `packages/routes.py` (ya no se usa en este
  archivo).

## Verificación

- 3 tests nuevos: búsqueda por email, por teléfono parcial (últimos 4 dígitos), y confirmación
  de que <4 dígitos NO dispara matching de teléfono. Los 2 tests existentes de teléfono/torre
  siguen pasando sin cambios (matching exacto viejo era un caso particular del parcial nuevo).
- Verificado contra datos reales migrados (buscar `0960` encuentra el paquete real por los
  últimos 4 dígitos del teléfono).
- `test_packages.py`: 166 passed.
- Investigado en vivo un reporte de "solo lista 3-4 resultados" buscando "3002" -- confirmado
  que es el filtro de Estado combinado con AND (comportamiento correcto, no bug): sin filtro,
  86 coincidencias reales / 5 páginas; con RECIBIDO o CANCELADO activo, exactamente 4.
- Pendiente: deploy a test.papyrus.com.co.

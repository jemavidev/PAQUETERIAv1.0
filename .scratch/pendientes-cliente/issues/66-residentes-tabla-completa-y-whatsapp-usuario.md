# 66 — `/residentes`: tabla con todos los campos al cargar + campo nuevo "Usuario de WhatsApp"

**Pedido original (cliente):** "muestralos todo. Adicional quiero agregar
un nuevo campo que incluira el nombre de usuario de whatsapp de un
cliente. Realiza todo lo necesario para agregar este campo y que puedas
mostarr todos los campos posibles de todos los clientes en la vista al
cargarla." — sobre el inventario completo de campos de `Persona` que se
presentó en el turno anterior.

**Status:** implementado

## Contexto

Antes: `/residentes` no mostraba nada hasta buscar, y el resultado era una
tarjeta con solo 3-4 campos (nombre, teléfono, notificaciones, documento).

## Implementación

**Campo nuevo `Persona.whatsapp_usuario`** (`app/domain/persona.py`,
migración `0026_persona_whatsapp_usuario`): texto opcional, mismo patrón
que `email`/`segundo_contacto`. `update_datos_personales`
(`persona_service.py`) gana el parámetro -- `/mis-datos` (el propio
cliente) no lo pasa, así que queda intacto para ese flujo, solo
`/residentes/{id}` (staff) lo escribe.

**`/residentes` sin término de búsqueda lista TODOS los clientes**, no
vacío como antes -- `_listar_todos_los_residentes` (mismo patrón de
paginación que `/paquetes`, `_POR_PAGINA=20`). Con término, la búsqueda
existente (`_buscar_residentes`) sigue igual, sin paginar (ya es un
subconjunto acotado).

**Tabla completa reemplaza las tarjetas**: 12 columnas -- Nombre,
Teléfono, Email, WhatsApp, Segundo contacto, Documento, Apartamento,
Notificaciones, Recepción automática, Estado (Activo/Eliminado),
Registrado, Actualizado. Con scroll horizontal (herramienta de
escritorio para staff, no una vista de cliente). El Apartamento de cada
fila se resuelve con UN solo query batched (`_apartamentos_por_id`) en
vez de uno por fila -- mismo patrón N+1 ya corregido en `/paquetes`/
`/mis-paquetes` en la auditoría de base de datos (issue 63).

`documento`/`tipo_documento` se muestran (dato histórico, issue [[63]]
no aplica acá) pero siguen sin ser editables -- decisión previa del
cliente ("sacar ese dato de todo flujo del sistema", Grupo 12), no se
revirtió.

El macro `tarjeta_cliente` (usado solo en esta vista) se eliminó de
`components/_tarjetas.html` -- quedó sin ningún caller.

`Ficha de cliente` (`/residentes/{id}`) gana el campo editable "Usuario
de WhatsApp" -- sin ícono a propósito (`iconos_nav.whatsapp` es un ícono
SOLID, pero `input_texto` solo sabe renderizar íconos outline; usarlo se
habría visto roto, mismo tipo de mismatch que ya se corrigió en el header
esta sesión).

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Guard de paridad esquema↔ORM: pasa.
- Ciclo manual `upgrade head` → `downgrade -1` → `upgrade head` contra un
  Postgres desechable: limpio.
- 5 tests nuevos en `tests/web/test_customers_manage.py`: listar sin
  búsqueda, estado vacío sin clientes, paginación con 25+ clientes, el
  campo WhatsApp aparece en la tabla, el campo WhatsApp se edita y
  persiste -- 46/46 en el archivo.
- Suite completa (`tests/data_model tests/web`): 647/647, sin
  regresiones.
- Tailwind recompilado y comiteado (nuevas clases `max-w-[1400px]`/
  `min-w-[1400px]`, no existían antes) -- `?v=32` → `?v=33`.
- Pendiente: confirmar en `test.papyrus.com.co` que la tabla se ve bien
  en un computador de staff, y decidir si el scroll horizontal de 12
  columnas es cómodo o si conviene ocultar algunas por defecto.

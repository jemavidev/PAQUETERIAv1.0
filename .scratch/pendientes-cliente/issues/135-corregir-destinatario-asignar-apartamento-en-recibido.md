# 135 — "Corregir destinatario": permitir asignar apartamento en RECIBIDO

**Pedido original (cliente, pregunta exploratoria):**
"Necesito que me sugieras que hacer en el modal 'Corregir destinatario',
esto especificamente para la seccion donde dice que 'Este paquete no
tiene apartamento asignado, así que no se puede agregar un nuevo
residente acá.', de que forma incluso en estado recibido yo pueda
asociar un apartamento en este estado, ya que para paquetes anunciados
si aparece una opcion para asignar un apartamento. El unico estado que
no deberia tener opcion de asignar apartamento es 'Cancelado'"

**Confirmación (cliente):** "La asignacion de apartamento para esta
vista 'Corregir destinatario' podra ser para los estados 'Anunciado y
Recibido'." -- ENTREGADO queda fuera (Corregir destinatario tampoco se
abre ahí, sin relación con esta ampliación).

**Status:** implementado

## Diagnóstico

`corregir_apartamento` (`paquete_lifecycle.py`) estaba HARD-gateada a
`ANUNCIADO` únicamente -- excepción acotada y documentada en ADR-0001,
pensada originalmente para el caso "Paquete huérfano". No era solo un
tema de interfaz: había que ampliar una regla de negocio documentada,
no solo mostrar un botón.

## Implementación

- `paquete_lifecycle.py`, `corregir_apartamento`: guard de
  `EstadoPaquete.ANUNCIADO` a `ESTADOS_CORREGIBLES` (ANUNCIADO/RECIBIDO
  -- misma constante que ya usa `corregir_destinatario`, elegibilidad
  consistente entre las dos correcciones del mismo modal).
- `docs/adr/0001-paquete-snapshot-inmutable.md`: actualizada la sección
  de excepciones conocidas.
- `packages/_resultados.html`: **3 gates** que tocar, no 2 -- el primer
  intento solo amplió los 2 botones que ABREN el modal "Asignar
  apartamento" (columna Dirección + swap dentro de Corregir
  destinatario), pero el modal EN SÍ (`{% if p.estado.value ==
  "ANUNCIADO" ... %}` envolviendo `{% call modal("asignar-apto-...") %}`)
  seguía condicionado solo a Anunciado. Bug real reportado en vivo por
  el cliente ("solo se cierra el modal") y reproducido con Playwright:
  el botón intentaba abrir un elemento que no existía en el DOM para
  RECIBIDO, así que el clic solo cerraba "Corregir destinatario" sin
  abrir nada. Los 3 gates ahora amplían igual (ANUNCIADO+RECIBIDO):
  1. Columna Dirección: ícono/emoji de asignar.
  2. Swap dentro de "+ Nuevo residente" (simplificado a solo
     `{% elif catalogo_torres %}` -- ya vive dentro del `{% if
     p.estado.value in ("ANUNCIADO", "RECIBIDO") %}` que envuelve TODO
     "Corregir destinatario", el chequeo de estado ahí era redundante).
  3. El modal "Asignar apartamento" en sí.
- `packages.py`, `assign_apartment_action`: docstring actualizada
  (seguía documentando "solo ANUNCIADO").
- **Ampliación del mismo pedido, en paralelo:** reemplazar el ícono SVG
  de casa por el emoji 🏢 (estado asignable) y el texto "Sin
  apartamento" por "🏢❌" (no asignable -- Entregado/Cancelado) en la
  columna Dirección de `/paquetes`.

## Verificación

- `tests/data_model/test_corregir_apartamento.py`:
  `test_corregir_en_recibido_falla_sin_efecto` invertido a
  `test_corregir_en_recibido_actualiza_snapshot_y_registra_actor`
  (ahora confirma éxito, no rechazo). Entregado/Cancelado siguen
  rechazando sin cambios.
- `tests/web/test_packages.py`: 4 tests actualizados/nuevos --
  `test_icono_asignar_apartamento_en_anunciado_y_recibido_sin_unidad`
  (ícono/emoji en Anunciado+Recibido, 🏢❌ en Entregado),
  `test_asignar_apartamento_exitoso_en_recibido`,
  `test_asignar_apartamento_rechaza_si_ya_esta_entregado` (mueve el
  límite probado de "ya no Anunciado" a "ya Entregado"),
  `test_nuevo_residente_ofrece_asignar_apartamento_si_recibido_y_sin_apartamento`
  (reemplaza el test que fijaba el bloqueo viejo).
- Suite completa de `test_packages.py`: 163 passed.
- **Verificación real, no solo sintética:** confirmado contra el
  paquete real del cliente (código YGAW, RECIBIDO, sin apartamento) --
  tras el fix, "Corregir destinatario" ya no muestra el mensaje
  bloqueante, ofrece "Asignar apartamento", y una vez asignado (Torre
  1 · Apto 302) "+ Nuevo residente" queda disponible con normalidad
  (confirmado en vivo: se llegó a crear un residente nuevo, "Natalia
  Gomez", con la función ya desbloqueada).
- Suite completa: pendiente de confirmar.
- Pendiente: deploy a test.papyrus.com.co.

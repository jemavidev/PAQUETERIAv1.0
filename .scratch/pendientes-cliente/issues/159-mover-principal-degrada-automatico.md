# 159 — Mover a un Residente Principal se degrada automáticamente

**Pedido original:** "Este proceso debería ser automático 'Ya es Ocupante PRINCIPAL de TORRE 1
Apto 302 -- no se puede mover directo (debe promover a otro residente primero, o desvincularse si
está solo)'... si intento mover un residente (principal) a otro apartamento, la idea es que si
existen otros residentes y el que intento mover es principal, se degrade automáticamente y sea
movido al nuevo apartamento como residente, no como principal." Confirmado con 2 preguntas antes
de implementar: (1) si está solo, también se mueve directo -- **sí**; (2) alcance -- **los 4
lugares** donde existía este bloqueo, con la aclaración explícita del cliente: "necesito que
confirmes que antes de mover, en caso que existan residentes adicionales, estos deben tener un
teléfono o usuario de whatsapp antes de poder convertirlo en principal, sea o no el más viejo" --
confirmado: el contacto es un filtro obligatorio, la antigüedad solo desempata ENTRE los que ya
tienen contacto.

**Status:** implementado

## Cambio

- `ocupante_service.mover_ocupante`: ya no rechaza a un Principal, sin excepción. Nuevo
  comportamiento:
  - Con otro Ocupante activo en la unidad actual que tenga Teléfono o WhatsApp propio: se lo
    promueve automáticamente (`promover_a_principal`, el MÁS ANTIGUO -- `created_at` ascendente --
    entre los que tienen contacto, nunca uno sin contacto) ANTES de mover al Principal, que llega
    al destino como Residente normal.
  - Solo en su unidad: se mueve directo, la unidad vieja queda vacía.
  - Con otros Ocupantes activos pero NINGUNO con contacto propio: rechaza con mensaje explicando
    por qué (degradar a alguien sin contacto rompería el invariante de que todo Principal necesita
    Teléfono o WhatsApp propio).
- `mensaje_ya_ocupante_activo`: el mensaje de "Ya es Ocupante PRINCIPAL..." ya no dice "debe
  promover a otro primero" -- ahora ofrece "Mover acá" igual que el caso no-principal (la
  degradación queda implícita en el propio movimiento).
- Aplicado en los 4 puntos de entrada que compartían este bloqueo: tab Dirección y tab Residentes
  de `/residentes`, "Corregir destinatario"/Recibir/Asignar apartamento de `/paquetes`, y
  `/announce`. Se corrigió de paso un gap real de integridad transaccional encontrado en el
  camino: 2 de los 4 (`/paquetes` y `/announce`) no hacían `db.rollback()` si `mover_ocupante`
  fallaba a mitad de camino (ej. destino lleno) DESPUÉS de ya haber promovido/degradado a alguien
  -- sin ese rollback, el cambio parcial quedaba comiteado igual al cerrar el request.
- Limpieza de UI: el flujo "Degradarlo" (abría un modal aparte "Promover a otro residente" con
  picker de candidatos) queda sin ningún botón que lo abra en las 3 plantillas donde vivía --
  el checkbox "Mudar residente acá" ya alcanza para los dos casos (principal o no). El modal y
  las rutas `/paquetes/promover-principal`/`/paquetes/promover-candidatos` NO se borraron (código
  ahora sin uso, no roto) -- limpieza aparte pendiente si el cliente la quiere.

## Verificación

- Domain: 3 tests nuevos (solo se mueve directo, con candidato con contacto degrada y promueve,
  sin candidato con contacto falla).
- Web (`/residentes`): 2 tests reescritos para reflejar el nuevo comportamiento permitido.
- Suite completa: 1044/1044 (antes de la corrección del test de [[160]], ver spec.md).
- Verificado en vivo contra `localhost:8010`: movido un Principal con otro residente a una unidad
  nueva -- el otro residente quedó promovido en la unidad vieja, el movido llegó confirmado pero
  NO principal a la nueva. Datos de prueba limpiados al terminar.

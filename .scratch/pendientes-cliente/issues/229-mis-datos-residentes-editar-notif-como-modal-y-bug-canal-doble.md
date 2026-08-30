# 229 — `/mis-datos` tab Residentes: Editar/Notificaciones como modal + bug real de canal doble

**Pedido original (cliente):** "Hagamos algo mejor... de qué forma puedes
mostrar esto en un modal, similar como lo haces en 'Promover o Eliminar'"
(seguimiento de [[228-mis-datos-residentes-editar-un-boton-y-acordeon-exclusivo]]).

**Status:** implementado

## Implementación

- "✏️ Editar" y "🔔 Notificaciones" pasan de `<details>` inline a modales
  (`components/_modales.html::modal`), mismo mecanismo `data-open`/
  `data-close` que ya usan "⭐ Promover"/"Rechazar-Eliminar". Cada botón
  trae `data-close` del OTRO modal (mismo patrón "traspaso limpio entre
  modales" de `_recibir_paquete.html`, issue 80) -- solo uno queda abierto
  a la vez, sin JS propio ni el atributo `name` de `<details>` del issue 228
  (ya no aplica, dejaron de ser `<details>`).

## Bug real encontrado en vivo (no pedido, hallado verificando el guardado unificado)

Al probar `/editar` con Teléfono+WhatsApp+Nombre+Email a la vez sobre un
residente de CANAL DOBLE, el WhatsApp se perdió: `editar_whatsapp_ocupante`
(y `editar_telefono_ocupante`) re-resolvían identidad vía `get_or_create_
persona(_por_whatsapp)` y RE-LIGABAN `ocupante.persona_id` a una Persona
DISTINTA -- correcto para canal único (preserva historial, issue 35), pero
para canal doble la Persona nueva/existente que resuelve el valor nuevo NO
tiene el OTRO canal, así que se perdía en silencio.

Corregido en `ocupante_service.py`: ambas funciones ahora detectan canal
doble (`persona_actual.whatsapp_usuario`/`.telefono` ya seteado) y en ese
caso escriben el campo EN EL LUGAR sobre la MISMA Persona (dos helpers
nuevos, `_asignar_telefono_a_persona`/`_asignar_whatsapp_a_persona`,
compartidos con `agregar_telefono_a_persona_de_ocupante`/`agregar_whatsapp_
a_persona_de_ocupante` del issue 217/213) -- el comportamiento de canal
único (re-ligar, preservar historial) se queda intacto, ya cubierto por
tests existentes. 4 tests nuevos en `test_ocupante_service.py` cubren el
caso de canal doble (no pierde el otro canal + colisión con otra Persona
existente falla). Datos de prueba dañados por el bug (Angélica quedó
partida en 2 Personas) reparados a mano en el ambiente local.

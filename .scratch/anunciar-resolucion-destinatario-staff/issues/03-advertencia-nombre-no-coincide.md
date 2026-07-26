# 03 — Advertencia de nombre no coincide en `/paquetes`

**Qué construir:** El staff ve una advertencia visual en `/paquetes` cuando el nombre anunciado de un Paquete difiere del nombre actualmente registrado para el teléfono que anunció. La advertencia se calcula al mostrar la lista (no se guarda), así que si el staff corrige el nombre de la Persona más adelante, la advertencia desaparece sola. No bloquea ninguna acción normal (recibir/entregar/cancelar) sobre ese paquete.

**Bloqueado por:** 02 (necesita el nuevo modo de `Destinatario` — es el único que puede producir un nombre distinto al registrado).

**Estado:** ready-for-agent

- [ ] Helper de solo lectura que compara `paquete.recipient_name` contra el `nombre` actual de la Persona (`announced_by_persona_id`), normalizando espacios/mayúsculas para la comparación (nunca para el guardado).
- [ ] La advertencia NO aparece cuando el nombre coincide, ni cuando la Persona fue creada por este mismo anuncio (nada que comparar todavía).
- [ ] `/paquetes` muestra la advertencia visualmente en la tarjeta del paquete correspondiente, sin ocultar ni deshabilitar los botones de acción existentes.
- [ ] `tests/web/test_packages.py` con un caso que confirma que la advertencia aparece cuando corresponde y no aparece cuando no.
- [ ] Suite completa (`pytest`) pasa.

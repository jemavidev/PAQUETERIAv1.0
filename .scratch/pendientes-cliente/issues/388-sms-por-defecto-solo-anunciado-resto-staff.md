# 388 — SMS: solo "Anunciado" por defecto; el resto lo activa el staff

**Pedido original (Jesús):** "el único SMS por defecto que deberá estar habilitado es Anunciado, el resto solo lo podrá activar el personal de staff" (hallazgo 13).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** verificado sin cambios de código -- Jesús confirmó (2026-09-23): "solo el admin, deja el 388 así"

## Decisiones

- Default: SMS activo solo para Anunciado -- ya era así (`_default_activo`, 2026-08-10).
- Recibido/Entregado/Cancelado por SMS: el Residente no puede activarlos -- ya era así (`canal_evento_editable`).
- Quién del staff: hoy SOLO el Admin. El Operador tiene la misma restricción que el Residente por decisión explícita
  del cliente del 2026-08-26 (costo de SMS), fijada en `test_operador_no_puede_activar_sms_fuera_de_anunciado`. No se
  cambió: "personal de staff" podría incluir al Operador, lo que revertiría esa decisión -- se le preguntó a Jesús.

# 02 — Corregir destinatario de un paquete `ANUNCIADO`

**Qué construir:** El staff puede corregir `recipient_name`/`recipient_phone` de un Paquete que sigue en `ANUNCIADO` (típicamente uno con la advertencia de nombre-no-coincide del Grupo 1). Excepción acotada y auditada a la inmutabilidad de ADR-0001 — ver la nota en `spec.md`. No aplica a paquetes en cualquier otro estado.

**Bloqueado por:** 01 (comparte la pantalla `/announce`/`/paquetes`, aunque la lógica de dominio es independiente).

**Estado:** ready-for-agent

- [ ] `corregir_destinatario(session, paquete, actor, recipient_name, recipient_phone=None)` en `paquete_lifecycle.py`: `TransicionInvalida` si `paquete.estado != ANUNCIADO`. Si es válido, actualiza `recipient_name`/`recipient_phone` y registra `corrected_at`/`corrected_by_usuario_id` (columnas nuevas, migración Alembic).
- [ ] Botón/modal "Corregir" en `/paquetes`, visible solo si `estado == ANUNCIADO` (con o sin advertencia — el staff puede corregir proactivamente).
- [ ] Corregir exitosamente recalcula la advertencia del Grupo 1 (si ahora coincide con el registrado, desaparece — ya es automático porque se calcula al leer).
- [ ] `tests/data_model/test_corregir_destinatario.py` (nuevo): corrige en `ANUNCIADO`; falla en `RECIBIDO`/`ENTREGADO`/`CANCELADO` sin efecto; registra actor y timestamp.
- [ ] `tests/web/test_packages.py` extendido: el botón/modal aparece solo en `ANUNCIADO`; corregir exitosamente actualiza la lista.
- [ ] Suite completa (`pytest`) pasa.

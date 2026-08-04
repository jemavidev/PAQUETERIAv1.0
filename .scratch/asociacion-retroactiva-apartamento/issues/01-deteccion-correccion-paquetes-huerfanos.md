# 01 — Detección y corrección de Paquetes huérfanos (dominio)

**What to build:** las dos funciones de dominio que hacen posible todo lo demás de este spec: una
que encuentra los Paquetes "huérfanos" de un Teléfono (Anunciados, sin Apartamento resuelto en su
snapshot), y otra que corrige el snapshot de Apartamento de un Paquete puntual — reutilizando
exactamente el mismo patrón ya auditado que usa `corregir_destinatario` (excepción acotada a
ADR-0001: solo mientras el Paquete sigue `Anunciado`, actor y `corrected_at` registrados). Esta
rebanada es 100% dominio — no toca ninguna ruta ni plantilla todavía; se demuestra y verifica
completa con tests de `tests/data_model/`.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `paquete_service.paquetes_sin_apartamento_de_telefono(session, telefono_canonico)` existe y
      devuelve los Paquetes `Anunciado` sin snapshot de Apartamento para ese teléfono, ya sea como
      Anunciante o como Destinatario.
- [ ] Paquetes `Recibido`, `Entregado` o `Cancelado` NUNCA aparecen en el resultado, aunque no
      tengan Apartamento en su snapshot.
- [ ] Un teléfono sin ningún Paquete huérfano devuelve lista vacía (no lanza, no falla).
- [ ] `paquete_lifecycle.corregir_apartamento(session, paquete, actor, apartamento)` existe, con el
      mismo guard que `corregir_destinatario`: `TransicionInvalida` si el Paquete no está
      `Anunciado` (el Paquete queda intacto, sin excepción).
- [ ] `corregir_apartamento` escribe `snapshot_conjunto`/`snapshot_torre`/`snapshot_apartamento`
      copiando el texto del `Apartamento` dado (nunca un FK — mismo criterio que
      `paquete_service.announce`), y registra `corrected_at`/`corrected_by_usuario_id` con `actor`
      (reutiliza las columnas existentes, sin migración nueva).
- [ ] Tests de integración nuevos en `tests/data_model/`, mismo arnés que
      `tests/data_model/test_ocupante_service.py` (fixture `db_session`, marker
      `pytest.mark.integration`, Postgres efímero real). Prior art directo para
      `corregir_apartamento`: `tests/data_model/test_corregir_destinatario.py`.
- [ ] `docs/adr/0001-paquete-snapshot-inmutable.md` actualizado con una nota corta que liste esta
      corrección como la segunda excepción conocida a la inmutabilidad del snapshot (junto a
      `corregir_destinatario`).
- [ ] Suite completa del proyecto sigue en verde.

# 04 — Mudanza/desvinculación + inmutabilidad del snapshot

**Spec:** `.scratch/data-model/spec.md` · **ADR:** 0001 (Paquete snapshot inmutable)

**What to build:** Una **Persona** puede **mudarse** a otro Apartamento o **desvincularse** en cualquier momento — y hacerlo **nunca reescribe** los paquetes que ya anunció. Los paquetes viejos siguen mostrando el apartamento de entonces. Este ticket corona el invariante central del rebuild.

**Blocked by:** 03 — Anunciar Paquete con snapshot congelado.

**Status:** done · 66 tests verdes

- [x] `move_resident(telefono, apartamento)` cambia el `apartamento_actual` de la Persona; con `apartamento = None` la **desvincula** (deja el actual nulo).
- [x] **Invariante corona (ADR-0001):** tras anunciar un Paquete y luego mudar/desvincular a la Persona, el **snapshot de apartamento** del Paquete viejo permanece **idéntico** al del instante del anuncio.
- [x] Tests: mudar cambia el apartamento actual; desvincular lo pone nulo; **ninguno** altera el snapshot de un paquete ya anunciado.
